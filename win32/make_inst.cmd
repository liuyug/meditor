@echo off

pushd ..
for /F %%i in ('python -c "from meditor import __app_version__; print(__app_version__)"') do ( set version=%%i)
popd

set MAKENSIS="c:\Program Files (x86)\NSIS\Bin\makensis.exe"


echo on
%MAKENSIS% /V4 /DPRODUCT_VER=%version% inst_script.nsi
