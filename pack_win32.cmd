cls

rmdir build /s /q

rem python setup.py bdist

rem python setup.py build_ext --inplace

rem pyinstaller --icon rsteditor\share\pixmaps\rsteditor-text-editor.ico --clean --noupx --noconfirm --windowed rsteditor.py

pyinstaller --clean --noconfirm rsteditor.spec

rem set MAKENSIS="c:\Program Files (x86)\NSIS\Bin\makensis.exe"
rem %MAKENSIS% inst_script.nsi
