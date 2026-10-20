@echo off
title Windows Shutdown Timer
color 0A

:menu
cls
echo ========================================
echo    Windows Shutdown Timer
echo ========================================
echo.
echo 1. Shutdown in 60 minutes
echo 2. Shutdown in 90 minutes
echo 3. Shutdown in 120 minutes
echo 4. Custom timer
echo 5. Cancel shutdown
echo 6. Exit
echo.
set /p choice="Select option (1-6): "

if "%choice%"=="1" shutdown /s /t 3600 & echo Shutdown set for 60 minutes! & pause & goto menu
if "%choice%"=="2" shutdown /s /t 5400 & echo Shutdown set for 90 minutes! & pause & goto menu
if "%choice%"=="3" shutdown /s /t 7200 & echo Shutdown set for 120 minutes! & pause & goto menu
if "%choice%"=="4" goto custom
if "%choice%"=="5" shutdown /a & echo Shutdown cancelled! & pause & goto menu
if "%choice%"=="6" exit

:custom
cls
set /p mins="Enter minutes (1-1440): "
set /a seconds=%mins%*60
shutdown /s /t %seconds%
echo Shutdown set for %mins% minutes!
pause
goto menu