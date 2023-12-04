#!/bin/zsh
#dos2unix entitlements.plist
rm -rf dist
rm -rf build
pyinstaller --noconfirm --clean  -i SpotifyDownloader.icns --windowed SpotifyDownloader.py

if [[ "$HOST" == "BE-BRU-MJX6DDQ1" || "$HOST" == "mots" ]]; then
	rm -rf ../Tracks/SpotifyDownloader.app
	mv dist/SpotifyDownloader.app ../Tracks
	rm -rf dist
	rm -rf build
fi

