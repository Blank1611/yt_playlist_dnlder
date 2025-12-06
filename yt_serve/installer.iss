; YouTube Playlist Manager - Inno Setup Installer Script
; This creates a professional Windows installer with everything bundled

#define MyAppName "YouTube Playlist Manager"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Your Name"
#define MyAppURL "https://github.com/YOUR_USERNAME/youtube-playlist-manager"
#define MyAppExeName "YouTubePlaylistManager.exe"
#define PythonVersion "3.14"
#define NodeVersion "20"

[Setup]
; Basic app information
AppId={{YOUR-GUID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output
OutputDir=installer_output
OutputBaseFilename=YouTubePlaylistManager_Setup
SetupIconFile=app_icon.ico
Compression=lzma
SolidCompression=yes

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Wizard appearance
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no

; License and info
LicenseFile=LICENSE
InfoBeforeFile=INSTALL_INFO.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files
Source: "dist\YouTubePlaylistManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "yt_serve\*"; DestDir: "{app}\yt_serve"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "DOCS\*"; DestDir: "{app}\DOCS"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "yt_playlist_audio_tools.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "migrate_playlists.py"; DestDir: "{app}"; Flags: ignoreversion

; Portable Python (embed version)
Source: "portable\python\*"; DestDir: "{app}\portable\python"; Flags: ignoreversion recursesubdirs createallsubdirs

; Portable Node.js
Source: "portable\nodejs\*"; DestDir: "{app}\portable\nodejs"; Flags: ignoreversion recursesubdirs createallsubdirs

; Launcher scripts
Source: "LAUNCH_APP.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "setup_dependencies.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Run dependency setup after installation
Filename: "{app}\setup_dependencies.bat"; Description: "Install dependencies (required)"; Flags: postinstall runhidden waituntilterminated
; Offer to launch the app
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DownloadPage: TDownloadWizardPage;
  InstallPathPage: TInputDirWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  // Custom page for installation path
  InstallPathPage := CreateInputDirPage(wpSelectDir,
    'Select Installation Location', 
    'Where should YouTube Playlist Manager be installed?',
    'Select the folder where you want to install the application, then click Next.',
    False, '');
  InstallPathPage.Add('');
  InstallPathPage.Values[0] := ExpandConstant('{autopf}\{#MyAppName}');
  
  // Download page for portable runtimes (if needed)
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    // Add downloads if portable runtimes not included
    // DownloadPage.Add('https://...', 'python-embed.zip', '');
    // DownloadPage.Add('https://...', 'node-portable.zip', '');
    // DownloadPage.Download;
    Result := True;
  end else
    Result := True;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\yt_serve\backend\venv"
Type: filesandordirs; Name: "{app}\yt_serve\frontend\node_modules"
Type: filesandordirs; Name: "{app}\yt_serve\backend\*.db"
Type: filesandordirs; Name: "{app}\yt_serve\backend\*.log"
