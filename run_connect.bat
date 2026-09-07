@echo off
title Tally Connect Service
cd /d %~dp0
echo Starting Tally Connect Service on port 8001...
python run_connect.py
pause
