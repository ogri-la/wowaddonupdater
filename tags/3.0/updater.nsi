;NSIS Script For SmallwxApp 
 
;Background Colors 
BGGradient 0000FF 000000 FFFFFF 
 
;Title Of Your Application 
Name "WoWUpdaterApp" 
 
;Do A CRC Check 
CRCCheck On 
 
;Output File Name 
OutFile "WoWUpdaterAppSetup.exe" 
 
;The Default Installation Directory 
InstallDir "$PROGRAMFILES\WoWAddOnUpdater" 
 
;The text to prompt the user to enter a directory 
DirText "Please select the folder below" 

SetCompressor /SOLID lzma

Section "Install" 
  ;Install Files 
  SetOutPath $INSTDIR 
  SetCompress Auto 
  SetOverwrite IfNewer 
  File "dist\updater.exe" 
  File "dist\w9xpopen.exe" 
  File "dist\python24.dll" 
  File "dist\library.zip" 
  File "dist\unzip.exe" 
  File "dist\unrar.exe" 
  File "dist\updater.ico" 
  File "dist\MSVCR71.dll" 
  Delete "$INSTDIR\updates\*.*"
 
  ; Write the uninstall keys for Windows 
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WoWAddOnUpdater" "DisplayName" "WoW AddOn Updater Program (remove only)" 
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WoWAddOnUpdater" "UninstallString" "$INSTDIR\Uninst.exe" 
WriteUninstaller "Uninst.exe" 
SectionEnd 
 
Section "Shortcuts" 
  ;Add Shortcuts 
;  CreateDirectory "$SMPROGRAMS\SmallwxApp" 
;  CreateShortCut "$SMPROGRAMS\SmallwxApp\Small wxApp.lnk" "$INSTDIR\SmallwxApp.exe" "" "$INSTDIR\SmallwxApp.exe" 0 
  CreateShortCut "$DESKTOP\WoW AddOn Updater.lnk" "$INSTDIR\updater.exe" "" "$INSTDIR\updater.ico" 0 
SectionEnd 
 
UninstallText "This will uninstall SmallwxApp from your system" 
 
Section Uninstall 
  ;Delete Files 
  Delete "$INSTDIR\updater.exe" 
  Delete "$INSTDIR\w9xpopen.exe" 
  Delete "$INSTDIR\python24.dll" 
  Delete "$INSTDIR\library.zip" 
  Delete "$INSTDIR\unzip.exe" 
  Delete "$INSTDIR\updater.ico" 
  Delete "$INSTDIR\MSVCR71.dll" 
  Delete "$DESKTOP\WoW AddOn Updater.lnk" 
 
  ;Delete Start Menu Shortcuts 
 ; Delete "$SMPROGRAMS\SmallwxApp\*.*" 
  ;RmDir "$SMPROGRAMS\SmallwxApp" 
 
  ;Delete Uninstaller And Unistall Registry Entries 
  Delete "$INSTDIR\Uninst.exe" 
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\WoWAddOnUpdater"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\WoWAddOnwUpdater" 
  RMDir "$INSTDIR" 
SectionEnd 

