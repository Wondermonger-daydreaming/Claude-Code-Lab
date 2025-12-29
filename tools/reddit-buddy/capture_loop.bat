@echo off
REM Reddit Scrolling Buddy - Auto-capture every 5 seconds
REM Ctrl+C to stop

cd /d "%~dp0"
py scroll_buddy.py --loop 5
