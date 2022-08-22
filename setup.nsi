;--------------------------------
; Includes

  !include "MUI2.nsh"
  !include "logiclib.nsh"

;--------------------------------
; Custom defines
  !define NAME "Phoenix_Turns"
  !define APPFILE "phoenix_turns.exe"
  !define VERSION "0.1.1"
  !define SLUG "${NAME} v${VERSION}"
  !define REG_NAME "Skeletal\PhoenixTurns"
  !define REG_DIR "PhoenixTurns"
;--------------------------------
; General

  Name "${NAME}"
  OutFile "release\${NAME} Setup v${VERSION}.exe"
  InstallDir "$PROGRAMFILES\${NAME}"
  InstallDirRegKey HKCU "Software\${REG_NAME}" ""
  RequestExecutionLevel admin

;--------------------------------
; UI
  
  !define MUI_ICON "phoenix.ico"
  !define MUI_HEADERIMAGE
  !define MUI_WELCOMEFINISHPAGE_BITMAP "doc\welcome.bmp"
  !define MUI_HEADERIMAGE_BITMAP "doc\head.bmp"
  !define MUI_ABORTWARNING
  !define MUI_WELCOMEPAGE_TITLE "${SLUG} Setup"

;--------------------------------
; Pages
  
  ; Installer pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  ; Uninstaller pages
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
  ; Set UI language
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Section - Shortcut

  Section "Desktop Shortcut" DeskShort
    SetOutPath "$INSTDIR"
    CreateShortCut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${APPFILE}"
  SectionEnd

;--------------------------------
; Section - Install App

  Section "-hidden app"
    ;kill process
    ExecWait "taskkill /f /IM ${APPFILE}"
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /r "app\*.*" 
    WriteRegStr HKCU "Software\${REG_NAME}" "Path" $INSTDIR
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${REG_DIR}" '"$INSTDIR\${APPFILE}"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REG_DIR}" "DisplayName" "Phoenix Turns Downloader"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REG_DIR}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REG_DIR}" "DisplayIcon" '"$INSTDIR\${APPFILE}"'

    WriteUninstaller "$INSTDIR\Uninstall.exe"
    Exec '"$INSTDIR\${APPFILE}"'
  SectionEnd

;--------------------------------
; Section - Uninstaller
Section "Uninstall"

  ExecWait "taskkill /f /IM ${APPFILE}"
  ;Delete Shortcut
  Delete "$DESKTOP\${NAME}.lnk"

  ;Delete Uninstall
  Delete "$INSTDIR\Uninstall.exe"

  ;Delete Folder
  RMDir /r "$INSTDIR"

  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${REG_DIR}"
  DeleteRegValue HKCU "Software\${REG_NAME}" "Path"
  DeleteRegKey /ifempty HKCU "Software\${REG_NAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${REG_DIR}"

SectionEnd