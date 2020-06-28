;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

!include "MUI2.nsh"

;--------------------------------
; makensis /DPRODUCT_VER=v0.0.0.0

;General
!define PRODUCT_NAME "Markup Editor"
;!define PRODUCT_VER "x.x.x.x"
!define SHORTCUT_APP_NAME "${PRODUCT_NAME}.lnk"
!define SHORTCUT_UNINSTALL_NAME "${PRODUCT_NAME} Uninstall.lnk"
!define EXEC_NAME "meditor.exe"
!define EXEC_ICON "$INSTDIR\data\meditor-text-editor.ico"
;
!define DIST_PATH '..\dist'

Name "${PRODUCT_NAME}"
OutFile "${DIST_PATH}\meditor-${PRODUCT_VER}.exe"

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
  File /r "${DIST_PATH}\meditor\*.*"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

; Optional section (can be disabled by the user)
Section "Start menu"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${SHORTCUT_APP_NAME}" "$INSTDIR\${EXEC_NAME}" "" "${EXEC_ICON}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${SHORTCUT_UNINSTALL_NAME}" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Shortcut desktop"
  CreateShortCut "$DESKTOP\${SHORTCUT_APP_NAME}" "$INSTDIR\${EXEC_NAME}" "" "${EXEC_ICON}"
SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  RMDir /r "$INSTDIR"
  Delete "$INSTDIR\Uninstall.exe"

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\*.*"
  Delete "$SMSTARTUP\${SHORTCUT_APP_NAME}"
  Delete "$DESKTOP\${SHORTCUT_APP_NAME}"
  Delete "$QUICKLAUNCH\${SHORTCUT_APP_NAME}"
  ; Remove directories used
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir "$INSTDIR"
SectionEnd
