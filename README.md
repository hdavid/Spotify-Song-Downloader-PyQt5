# Spotify Song Downloader with Python and PyQt5

## Changelog

- v2.1.2-hdavid
  - add download cover
  - skip already downloaded tracks
  - grey + enlarged UI
  - download single track
  - better feedback

- v2.1.1 **Release** 19th October 2023
  - Fixed API Paths
  
- v2.1 Stop Working [ 19th October 2023 ]
  
- v2.1 
  - Added Song Metadata such as song cover, artist, title and song release date
    
- v2.0
  - Added Progress bar and interface to view songs as it is being downloaded.
  - Used v2 method for 320 kbps songs and if not available will revert to 128 kbps
  - **Release**
  - version 2.0 is in the same mega download link below.
  - To get v2.0 files, use the release feature on the right side of the repository named : [Release](https://github.com/surenjanath/Spotify-Song-Downloader-PyQt5/releases/tag/SpotifyDownloader2.0)
    
- v1.0
  - Released
  
## Introduction

In this project, we have created a Spotify song downloader using Python and PyQt5. The application allows users to download their favorite Spotify songs by providing the playlist link. We utilize web scraping techniques to extract the song data and PyQt5 for building an interactive and user-friendly desktop application.<br>
This is the code for the User Interface.<br>


## How it Works

The Spotify song downloader uses web scraping to interact with a specific website and extract song information, including the song title, artists, and YouTube ID. It then utilizes the YouTube ID to generate Analyze and Conversion IDs, which are used to download the songs. The PyQt5 interface allows users to input the Spotify playlist link, view real-time download progress, and receive updates on the downloaded songs.

  
## Usage
###  Running from command line 

1. Clone the repository: `git clone https://github.com/hdavid/Spotify-Song-Downloader-PyQt5.git`
2. `pip3 install -r requirements.txt`
3. `python3 SpotifyDownlader.py`


###  Creating an application 

1. Clone the repository: `git clone https://github.com/hdavid/Spotify-Song-Downloader-PyQt5.git`
2. `pip3 install -r requirements.txt`
3. Mac: run `./package.sh` in the terminal
3. Windows: double click `package.bat`


### Using it
1. Enter the Spotify playlist or track link and press Enter.
2. The application will start scraping the website and downloading the songs to a local folder named 

#### Note
while running from command line, it will download the files to : `~/Music/Tracks/'playlist name'`

When running as an app, it will download the files to : `./'playlist name'"`



## Author

- based on code from [Surenjanath Singh](https://github.com/surenjanath)
- see the wonderful [Building an Interface for our Spotify Song Downloader with PyQt5](https://surenjanath.medium.com/building-an-interface-for-our-spotify-song-downloader-with-pyqt5-fa0442909be9)

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Please use the Spotify song downloader responsibly and respect copyright laws. Only download songs that you have the rights to use.

For example : https://open.spotify.com/playlist/3fQ6EJdy6n1kF4Yw5bTAVx?si=2f26056713504154

PS : CREATED TO DOWNLOAD COPYRIGHT FREE MUSIC
