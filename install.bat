@echo off
echo installing everything

:: up pip, setuptools, and wheel
python -m pip install --upgrade pip setuptools wheel

:: install telegram bot library only needed
pip install python-telegram-bot

echo everything now installed
pause
