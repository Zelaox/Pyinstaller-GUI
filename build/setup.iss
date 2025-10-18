#define MyAppName "Pyinstaller"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Kim Nilsson"
#define MyAppExeName "enhanced_pyinstaller_gui.exe"

[Setup]
AppId={{enhanced_pyinstaller_gui}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=build\Output
OutputBaseFilename=Pyinstaller Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=D:/AI/ChatGPT/My_programs/Zelaox_Pig_sunglasses_pink_background_3D_8K_f2242065-660b-4065-afe7-3b3f337b0d20.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "enhanced_pyinstaller_gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
