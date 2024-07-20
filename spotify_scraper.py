import json
import re
import requests
import signal
import sys
import traceback
from unidecode import unidecode
from dataclasses import dataclass

#from datetime import datetime
from pathlib import Path
from time import sleep
import os

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

# Want to figure out how to do this without a third party module
import eyed3
from eyed3.id3 import ID3_V2_3
from eyed3.id3.frames import ImageFrame

# Suppress warnings about CRC fail for cover art
import logging
logging.getLogger('eyed3.mp3.headers').warning = logging.debug



def clean_filename(fn):
    validchars = "-_.() '',"
    out = ""
    for c in fn:
      if str.isalpha(c) or str.isdigit(c) or (c in validchars):
        out += c
      else:
        out += "-"
    return unidecode(out)
    
    
@dataclass(frozen=True, eq=True)
class SpotifySong:
    title: str
    artist: str
    album: str
    id: str
    
    @property
    def url(self):
         return f"https://open.spotify.com/track/{id}"
    
    @property
    def filename(self):
        return clean_filename(f"{self.artist} - {self.album} - {self.title}.mp3")
        
    @property
    def name(self): 
        return f"{self.artist} - {self.album} - {self.title}"


class SpotifyScraper(QObject):
    
    song_downloading = pyqtSignal(str)
    counts = pyqtSignal(str, int, int, int, int)
    playlist_name = pyqtSignal(str)
    details_update = pyqtSignal(str)
    
    DOWNLOADER_URL = "https://api.spotifydown.com"
    # Clean browser heads for API
    DOWNLOADER_HEADERS = {
        'Host': 'api.spotifydown.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'Referer': 'https://spotifydown.com/',
        'Origin': 'https://spotifydown.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Sec-GPC': '1',
        'TE': 'trailers'
    }

    
    def __init__(self):
        super(SpotifyScraper, self).__init__()
        self.playlist_tracks = []
        self.downloaded_tracks = []
        self.skipped_tracks = []
        self.failed_tracks = []
        
    
    def is_album(self, url):
            return "/album/" in url 
           
            
    def is_playlist(self, url):
            return "/playlist/" in url
    
    
    def is_track(self, url):
        return "/track/" in url
        
        
    @property
    def playlist_track_count(self):
        return len(self.playlist_tracks)
        
        
    @property
    def downloaded_track_count(self):
        return len(self.downloaded_tracks)
    
    
    @property
    def skipped_track_count(self):
        return len(self.skipped_tracks)
    
    
    @property
    def failed_track_count(self):
        return len(self.failed_tracks)
        
             
    def scrape(self, url, music_folder):
        self.details_update.emit("")
        
        if self.is_playlist(url) or self.is_album(url):
            entity_id = url.split('/')[-1].split('?')[0]
            if self.is_playlist(url):
                entity_type = "playlist"
            else:
                entity_type = "album"
                
            entity_metadata = self._call_downloader_api(f"/metadata/playlist/{entity_id}").json()
            if entity_type == "playlist":
                entity_name = entity_metadata['title'] + " (" + entity_metadata['artists'] + ")"
            else:
                entity_name = entity_metadata['artists']+ " - " + entity_metadata['title']
            
            self.playlist_name.emit(entity_type + ": " + entity_name)
            
            if not entity_metadata["success"]:
                self.song_downloading.emit("not a valid "+ entity_name + ", Spotify api return error message: " + playlist_metadata["message"])
                return                
            
            music_folder = Path(music_folder + "/" + entity_name)
            
        elif self.is_track(url):
            self.details_update.emit("")
            self.song_downloading.emit("")
            self.playlist_name.emit("Single track")
            entity_type = "track"
            music_folder = Path(music_folder)
            entity_id = url.split('/')[-1].split('?')[0]
        else:
            self.details_update.emit("Invalid url")
            return
        
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
            
        self.update_track_counts_ui("Scanning")
        self.playlist_tracks = self.get_tracks_to_download(entity_type, entity_id)
        
        self.update_track_counts_ui("Downloading")
        self.download_all_tracks(
            self.playlist_tracks,
            music_folder
        )
        if self.is_track(url):
            self.update_track_scrape_details()
        else:
            self.update_playlist_scrape_details(music_folder)
        self.song_downloading.emit("")
        self.update_track_counts_ui("Done")
        
    
    def update_track_counts_ui(self, message):
        self.counts.emit(message, self.playlist_track_count, self.downloaded_track_count, self.skipped_track_count, self.failed_track_count)  
        
    def update_playlist_scrape_details(self, music_folder):
        details = ""   
                 
        if self.failed_track_count>0:
            details += "\nFailed track downloads:"
            for track in self.failed_tracks:
                details += "\n" + track.name
            details += "\n"
        
        directory_files = os.listdir(music_folder)
        in_folder_not_in_playlist = []
        playlist_filenames = []
        for track in self.playlist_tracks:
            playlist_filenames.append(track.filename)
        for filename in directory_files:
            if filename not in playlist_filenames and filename != ".DS_Store" and not filename.startswith(".syncthing.") and not filename.endswith(".stem.m4a"):
                in_folder_not_in_playlist.append(filename)
        if len(in_folder_not_in_playlist):
            details += "\nTracks in folder but not in playlist:"
            for track in in_folder_not_in_playlist:
                details += "\n" + track
            details += "\n"
                
        in_playlist_not_in_folder = []
        for track in self.playlist_tracks:
            if track.filename not in directory_files:
                 in_playlist_not_in_folder.append(track.name)
        if len(in_playlist_not_in_folder):
            details += "\nTracks in playlist but not in folder:"
            for track in in_playlist_not_in_folder:
                details += "\n" + track
            details += "\n"
        
        if len(in_playlist_not_in_folder)==0 and len(in_folder_not_in_playlist)==0 and self.failed_track_count==0:
            details += "Hurray ! All downloads completed sucessfully!\n\n\n\n"
            
        self.details_update.emit(details)
        
    
    def update_track_scrape_details(self):
        details = ""
        
        if len(self.failed_tracks)>0:
            details += "\nFailed track download:"
            for track in self.failed_tracks:
                details += "\n" + track
            details += "\n"
        
        if len(self.failed_tracks)==0:
            details += "Hurray ! Download completed sucessfully!\n\n\n\n"
            
        self.details_update.emit(details)
    

    def _call_downloader_api(
        self,
        endpoint: str,
        method: str = 'GET',
        headers=DOWNLOADER_HEADERS,
        **kwargs
    ) -> requests.Response:
        _map = {
            'GET': requests.get,
            'POST': requests.post
        }

        if method not in _map:
            raise ValueError

        try:
            resp = _map[method](self.DOWNLOADER_URL + endpoint, headers=headers, **kwargs)
        except Exception as exc:
            raise RuntimeError("ERROR: ", exc)

        return resp


    def get_track_data(self, track_id: str):
        resp = self._call_downloader_api(f"/download/{track_id}")
        resp_json = resp.json()
        if not resp_json['success']:
            # print("[!] Bad URL. No song found.")
            resp_json = {}
        return resp_json


    def get_multi_track_data(self, entity_id: str, entity_type: str):
        metadata_resp = self._call_downloader_api(f"/metadata/{entity_type}/{entity_id}").json()

        # For paginated response
        track_list = []

        tracks_resp = self._call_downloader_api(f"/trackList/{entity_type}/{entity_id}").json()

        if not tracks_resp.get('trackList'):
            return {}

        track_list.extend(tracks_resp['trackList'])

        while next_offset := tracks_resp.get('nextOffset'):
            tracks_resp = self._call_downloader_api(f"/trackList/{entity_type}/{entity_id}?offset={next_offset}").json()
            track_list.extend(tracks_resp['trackList'])

        if not metadata_resp['success']:
            return {}

        return {
            **metadata_resp,
            'trackList': [
                SpotifySong(
                    title=track['title'],
                    artist=track['artists'],
                    album=track['album'] if entity_type == "playlist" else metadata_resp['title'],
                    id=track['id']
                )
                for track in track_list
            ]
        }


    def get_spotify_playlist(self, playlist_id: str, token: str):
        # GET to playlist URL can get first 30 songs only
        # soup.find_all('meta', content=re.compile("https://open.spotify.com/track/\w+"))

        playlist_resp = requests.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}',
            headers={'Authorization': f"Bearer {token}"}
        )

        playlist = playlist_resp.json()

        tracks_list = [
            SpotifySong(
                title=track['track']['name'],
                artist=', '.join(artist['name'] for artist in track['track']['artists']),
                album=track['track']['album']['name'],
                id=track['track']['id']
            )
            for track in playlist['tracks']['items']
        ]

        return playlist['name'], playlist['owner']['display_name'], tracks_list
    


    def get_tracks_to_download(self, entity_type: str, entity_id: str) -> list:
        tracks = []

        if entity_type == "track":
            track_resp_json = self.get_track_data(track_id=entity_id)
            if not track_resp_json:
                self.update_track_counts_ui("Error")
                details = "no track found at url"
                self.details_update.emit(details)
                return []
            
            spotify_song = SpotifySong(
                title=track_resp_json['metadata']['title'],
                artist=track_resp_json['metadata']['artists'] ,
                album=track_resp_json['metadata']['album'],
                id=track_resp_json['metadata']['id']
            )
            self.playlist_tracks.append(spotify_song.filename)
            tracks.append(spotify_song)
            

        elif entity_type in ["playlist", "album"]:

            multi_track_resp_json = self.get_multi_track_data(entity_id, entity_type)

            if not multi_track_resp_json:
                self.update_track_counts_ui("Error")
                details = "no track found at url"
                self.details_update.emit(details)
                return []

            for track in multi_track_resp_json['trackList']:
                tracks.append(track)
                self.playlist_tracks.append(track.filename)

        else:
            return []

        return tracks


    def download_track(self, track:SpotifySong, dest_dir: Path):
        
        # Grab a fresh download link since the one was got may have expired
        resp_json = self.get_track_data(track.id)
        # Clean browser heads for API
        hdrs = {
            #'Host': 'cdn[#].tik.live', # <-- set this below
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip',
            'Referer': 'https://spotifydown.com/',
            'Origin': 'https://spotifydown.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-GPC': '1'
        }

        if 'link' not in resp_json or 'metadata' not in resp_json:
            raise RuntimeError(
                f"Bad response for track '{track.name}' ({track.id}): {resp_json}"
            )

        # For audio
        hdrs['Host'] = resp_json['link'].split('/')[2]
        audio_dl_resp = requests.get(resp_json['link'], headers=hdrs)
        
        
        if not audio_dl_resp.ok:
            raise RuntimeError(
                f"Bad download response for track '{track.title}' ({track.id}): {audio_dl_resp.content}"
            )
        
        with open(dest_dir/track.filename, 'wb') as track_mp3_fp:
            track_mp3_fp.write(audio_dl_resp.content)

        # For cover art
        if cover_art_url := resp_json['metadata'].get('cover'):
            hdrs['Host'] = cover_art_url.split('/')[2]
            cover_resp = requests.get(cover_art_url,headers=hdrs)

            mp3_file = eyed3.load(dest_dir/track.filename)
            if (mp3_file.tag == None):
                mp3_file.initTag()

            mp3_file.tag.images.set(ImageFrame.FRONT_COVER, cover_resp.content, 'image/jpeg')
            mp3_file.tag.album = resp_json['metadata']['album']
            mp3_file.tag.recording_date = resp_json['metadata']['releaseDate']

            # default version lets album art show up in Serato
            #mp3_file.tag.save()
            # version fixes FRONT_COVER not showing up in windows explorer
            mp3_file.tag.save(version=ID3_V2_3)
            
        # prevent API throttling
        sleep(0.1)


    def download_all_tracks(
        self,
        tracks: list,
        output_dir: Path
    ):
       
        for track in tracks:
            self.song_downloading.emit(track.name)
            full_filename = output_dir / track.filename
            try:
                if os.path.exists(full_filename):
                    self.skipped_tracks.append(track)
                else:
                    ok = False
                    errors = 0
                    while not ok:
                        try:
                            self.download_track(track, output_dir)
                            self.downloaded_tracks.append(track)
                            ok = True
                        except Exception as exc:
                            print(exc)
                            print('Retrying!')
                            sleep(1)
                            errors += 1
                            if errors>3:
                                raise exc
                self.update_track_counts_ui("Downloading")
            except Exception as exc:
                print(traceback.format_exc())
                self.failed_tracks.append(track)
                self.update_track_counts_ui("Error")



      




      



