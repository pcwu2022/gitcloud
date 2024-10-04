@echo off
echo Running Launcher...

:: Execute launcher.js
node launcher.js

:: Git Commit

echo Executing Git...
git add --all
git commit -m "auto commit on %TIME%"
git push

echo Finished!
pause