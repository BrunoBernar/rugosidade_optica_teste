; Inno Setup Script - Estimador de Rugosidade Stellantis
; Requer Inno Setup 6+ -> https://jrsoftware.org/isdl.php

#define AppName      "Estimador de Rugosidade"
#define AppVersion   "1.0.0"
#define AppPublisher "Stellantis"
#define AppExeName   "Rugosidade_Stellantis.exe"
#define AppURL       "https://www.stellantis.com"

[Setup]
AppId={{A3F2B1C4-9D7E-4F8A-B2C3-1E5D6F7A8B9C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\Stellantis\Rugosidade
DefaultGroupName=Stellantis\Estimador de Rugosidade
AllowNoIcons=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=Setup_Rugosidade_Stellantis_v{#AppVersion}
SetupIconFile=stellantis.ico
WizardImageFile=compiler:WizClassicImage-IS.bmp
WizardSmallImageFile=compiler:WizClassicSmallImage-IS.bmp
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=classic
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} {#AppVersion}
ShowLanguageDialog=no
LanguageDetectionMethod=none

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon";    Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Icones adicionais:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Criar atalho na Barra de Tarefas"; GroupDescription: "Icones adicionais:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "stellantis.ico";     DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";                  Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\stellantis.ico"
Name: "{group}\Desinstalar {#AppName}";      Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";            Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\stellantis.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Executar {#AppName} agora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Messages]
; Mensagens customizadas em portugues
WelcomeLabel1=Bem-vindo ao instalador do%n{#AppName}
WelcomeLabel2=Este programa instalara o {#AppName} {#AppVersion} em seu computador.%n%nRecomenda-se fechar todos os outros programas antes de continuar.%n%nClique em Avancar para continuar.
FinishedHeadingLabel=Instalacao concluida
FinishedLabel=O {#AppName} foi instalado com sucesso.%n%nClique em Concluir para sair do instalador.
