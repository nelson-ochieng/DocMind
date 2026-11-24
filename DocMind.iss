[Setup]
AppName=DocMind
AppVersion=4.2.0
DefaultDirName={localappdata}\Programs\DocMind
DefaultGroupName=DocMind
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=DocMind-Setup
Compression=lzma2
SolidCompression=yes
[Files]
Source: "dist\DocMind\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\DocMind"; Filename: "{app}\DocMind.exe"
Name: "{userdesktop}\DocMind"; Filename: "{app}\DocMind.exe"
