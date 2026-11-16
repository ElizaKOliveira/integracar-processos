[Setup]
AppId={{8F3B2C1A-5D4E-4F6A-9B7C-2E1D0A9C8B73}
AppName=Leitor de Processos
AppVersion={#AppVersion}
DefaultDirName={autopf}\Leitor de Processos
DefaultGroupName=Leitor de Processos
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=Setup-LeitorDeProcessos-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
UninstallDisplayName=Leitor de Processos
#if FileExists("icone.ico")
SetupIconFile=icone.ico
#endif
UninstallDisplayIcon={app}\LeitorDeProcessos.exe

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Área de Trabalho"; GroupDescription: "Atalhos:"

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\backend\dist\LeitorDeProcessos\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "AVISOS.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Leitor de Processos"; Filename: "{app}\LeitorDeProcessos.exe"
Name: "{autodesktop}\Leitor de Processos"; Filename: "{app}\LeitorDeProcessos.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LeitorDeProcessos.exe"; Description: "Abrir o Leitor de Processos agora"; Flags: nowait postinstall skipifsilent