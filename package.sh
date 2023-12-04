#!/bin/zsh
#dos2unix entitlements.plist
rm -rf dist
rm -rf build
rm -rf ~/Music/Tracks/SpotifyDownloader.app

pyinstaller --noconfirm --clean  -i icons/SpotifyDownloader.icns --windowed SpotifyDownloader.py

host=`hostname -s`
if [[ "$host" == "BE-BRU-MJX6DDQ1" || "$host" == "sixteen" ]]; then
	rm -rf /Applications/SpotifyDownloader.app
	mv dist/SpotifyDownloader.app /Applications/
fi

