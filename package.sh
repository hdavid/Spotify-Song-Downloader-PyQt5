#!/bin/zsh
#dos2unix entitlements.plist
rm -rf dist
rm -rf build
rm -rf ~/Music/Tracks/SpotifyDownloader.app

pyinstaller --noconfirm --clean  -i SpotifyDownloader.icns --windowed SpotifyDownloader.py

if [[ "$HOST" == "BE-BRU-MJX6DDQ1" || "$HOST" == "mots" ]]; then
	rm -rf ../Tracks/SpotifyDownloader.app
	cp -r dist/SpotifyDownloader.app ~/Music/Tracks
fi

