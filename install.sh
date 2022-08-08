#!/bin/sh

echo "creating main executable file "
python -m PyInstaller app.spec
echo "moving main executable file"
mv ./dist/main ./main
rm main.spec

echo "creating directory with files for application"
pyinstaller --onedir --noconfirm app_combined.spec
echo "moving main executable to directory and creating final directory"
mv ./main ./dist/pp/
mv ./dist/app/ ./KeithleyDashApp

echo "executable creation completed, press enter to continue"
read input