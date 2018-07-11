rm -rf ./macOS/ 
rm -rf ./dist/
make check
make clean
python3 setup.py macos
mkdir ./dist
dmgbuild -s package/dmg_settings.py "Mu Editor" dist/mu-editor.dmg
du -skh dist/
mv dist/mu-editor.dmg dist/mu-editor_$(date '+%Y-%m-%d_%H_%M')_manual.dmg
