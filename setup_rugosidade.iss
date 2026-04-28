; Inno Setup Script - BCI KNUCKLE SOFTWARE

#define AppName      "BCI - Knuckle Software"
#define AppVersion   "1.0.0"
#define AppPublisher "Bruno Bernardinetti"
#define AppExeName   "Rugosidade_Stellantis.exe"
#define AppURL       "https://www.stellantis.com"
#define Contato      "+55 32 9 9965-0392"

[Setup]
AppId={{A3F2B1C4-9D7E-4F8A-B2C3-1E5D6F7A8B9C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\BCI-Knuckle
DefaultGroupName=BCI Knuckle Software
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=Setup_BCI_Knuckle_v{#AppVersion}
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
Name: "desktopicon";  Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Icones adicionais:"; Flags: unchecked
Name: "autoupdate";   Description: "Verificar atualizacoes automaticamente ao iniciar"; GroupDescription: "Opcoes:"; Flags: checked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "stellantis.ico";     DestDir: "{app}"; Flags: ignoreversion
Source: "manual.pdf";         DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\stellantis.ico"
Name: "{group}\Manual do Usuario";       Filename: "{app}\manual.pdf"
Name: "{group}\Desinstalar {#AppName}";  Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\stellantis.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Executar {#AppName} agora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Messages]
WelcomeLabel1=Bem-vindo ao {#AppName}
WelcomeLabel2=Este instalador configurara o {#AppName} {#AppVersion} em seu computador.%n%nPERIODO DE AVALIACAO GRATUITA: 7 DIAS%n%nApos o periodo de teste, entre em contato para adquirir sua licenca:%n%n     {#Contato}%n%nClique em Avancar para continuar.
FinishedHeadingLabel=Instalacao concluida!
FinishedLabel=O {#AppName} foi instalado com sucesso.%n%nPeriodo de avaliacao: 7 dias gratuitos.%nPara licenciamento permanente: {#Contato}%n%nClique em Concluir para sair.

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir, SettFile, Content: String;
begin
  if CurStep = ssPostInstall then begin
    AppDataDir := ExpandConstant('{userappdata}\BCI-Knuckle');
    ForceDirectories(AppDataDir);
    SettFile := AppDataDir + '\settings.json';
    if IsTaskSelected('autoupdate') then
      Content := '{"auto_update": true}'
    else
      Content := '{"auto_update": false}';
    SaveStringToFile(SettFile, Content, False);
  end;
end;
