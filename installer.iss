; Inno Setup script for Simpaudio
; Download Inno Setup: https://jrsoftware.org/isdl.php
; Compile: right-click installer.iss -> Compile (or run "ISCC.exe installer.iss")

#define MyAppName "Simpaudio"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "alimaandev"
#define MyAppURL "https://github.com/alimaandev/simpaudio"
#define MyAppExeName "Simpaudio.exe"
#define MyAppDescription "Offline Text-to-Speech, Voice Blending, Audiobook Studio and Transcription"

[Setup]
AppId={{36F9DB2C-20E7-4D17-B8A1-B5DBE3144CA2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppVerName={#MyAppName} {#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=Simpaudio_Setup_{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
WizardImageFile=installer_banner.bmp
WizardSmallImageFile=installer_small.bmp
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico
DisableStartupPrompt=yes
PrivilegesRequired=admin
ShowLanguageDialog=no
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
Source: "dist\Simpaudio\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Simpaudio\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "{#MyAppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; Comment: "{#MyAppDescription}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: files; Name: "{app}\icon.ico"

[Code]
function InitializeSetup: Boolean;
begin
  Result := True;
end;
