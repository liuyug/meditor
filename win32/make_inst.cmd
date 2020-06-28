@echo off

set MAKENSIS="c:\Program Files (x86)\NSIS\Bin\makensis.exe"

set ver=%1

if "%ver%" == "" echo Please input version, such as v0.1.0.0 & exit /b

echo on
%MAKENSIS% /V4 /DPRODUCT_VER=%ver% inst_script.nsi
