rem create win32 executable with cx_Freeze and pack installer with NSIS

set BUILD_DIR="build"
set TARGET_DIR="%BUILD_DIR%\exe.win32-3.4"

set PYTHON="c:\python34\python"
set ZIP7="c:\Program Files\7-Zip\7z.exe"
set MAKENSIS="c:\Program Files (x86)\NSIS\Bin\makensis.exe"

rmdir /s /q %TARGET_DIR%

%PYTHON% setup_cxFreeze.py build
%ZIP7% x -y -o%TARGET_DIR% %TARGET_DIR%\library.zip docutils rsteditor
%ZIP7% d %TARGET_DIR%\library.zip docutils rsteditor

rem delete unused debug files
rem del %TARGET_DIR%\imageformats\*d.pdb
rem del %TARGET_DIR%\imageformats\*d.dll
rem del %TARGET_DIR%\platforms\*d.pdb
rem del %TARGET_DIR%\platforms\*d.dll

%MAKENSIS% inst_script.nsi
