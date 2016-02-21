;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

!include "MUI2.nsh"

;--------------------------------
;General
!define PRODUCT_NAME "rsteditor"
!define PRODUCT_VER "0.2.0.6"
!define SHORTCUT_NAME "rsteditor.lnk"
!define EXEC_NAME "rsteditor.exe"
!define EXEC_ICON "$INSTDIR\pixmaps\rsteditor-text-editor.ico"

Name "${PRODUCT_NAME}"
OutFile "build\${PRODUCT_NAME}-${PRODUCT_VER}.exe"

;--------------------------------
SetCompressor lzma
CRCCheck on

;Interface Configuration

!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING

!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\orange-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\orange-uninstall.ico"
!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\orange.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "${NSISDIR}\Contrib\Graphics\Header\orange-uninstall.bmp"
!define MUI_HEADERIMAGE_BITMAP_STRETCH FitControl
!define MUI_HEADERIMAGE_UNBITMAP_STRETCH FitControl
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange-uninstall.bmp"



;--------------------------------
;Pages
!insertmacro MUI_PAGE_WELCOME
;!insertmacro MUI_PAGE_LICENSE "License-GNU.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${EXEC_NAME}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_RESERVEFILE_LANGDLL

InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"

ShowInstDetails show
ShowUninstDetails nevershow

BrandingText "${PRODUCT_NAME} ${PRODUCT_VER}"


;--------------------------------
;Installer Sections
;--------------------------------

Section "!Install"

  SetOutPath "$INSTDIR"
  ; CreateDirectory $INSTDIR\dir
  ;File /r /x *.nsi /x .svn  *.*
  File /r "build\exe.win32-3.4\*.*"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

; Optional section (can be disabled by the user)
Section "Start menu"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${SHORTCUT_NAME}" "$INSTDIR\${EXEC_NAME}" "" "${EXEC_ICON}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Shortcut desktop"
  CreateShortCut "$DESKTOP\${SHORTCUT_NAME}" "$INSTDIR\${EXEC_NAME}" "" "${EXEC_ICON}"
SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  RMDir /r "$INSTDIR"
  Delete "$INSTDIR\Uninstall.exe"

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\*.*"
  Delete "$SMSTARTUP\${SHORTCUT_NAME}"
  Delete "$DESKTOP\${SHORTCUT_NAME}"
  Delete "$QUICKLAUNCH\${SHORTCUT_NAME}"
  ; Remove directories used
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir "$INSTDIR"
SectionEnd
