@echo off
echo Activating virtual environment and running chat test...
call venv\Scripts\activate
python test_chat.py
pause
