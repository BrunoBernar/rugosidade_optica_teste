; Inno Setup Script - BCI STLA

#define AppName      "BCI STLA"
#define AppVersion   "1.0.0"
#define AppPublisher "Bruno Bernardinetti"
#define AppExeName   "BCI_STLA.exe"
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
DefaultDirName={autopf}\BCI_STLA
DefaultGroupName=BCI STLA
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=Setup_BCI_STLA_v{#AppVersion}
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
Name: "autoupdate";   Description: "Verificar atualizacoes automaticamente ao iniciar"; GroupDescription: "Opcoes:"

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "stellantis.ico";     DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\stellantis.ico"
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
function InitializeSetup(): Boolean;
var
  ExistingVersion: String;
  Msg: String;
begin
  Result := True;
  if RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{A3F2B1C4-9D7E-4F8A-B2C3-1E5D6F7A8B9C}_is1',
                         'DisplayVersion', ExistingVersion) or
     RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{A3F2B1C4-9D7E-4F8A-B2C3-1E5D6F7A8B9C}_is1',
                         'DisplayVersion', ExistingVersion) then begin
    if ExistingVersion <> '{#AppVersion}' then begin
      Msg := 'Versao instalada: ' + ExistingVersion + #13#10 +
             'Nova versao: {#AppVersion}' + #13#10#13#10 +
             'Deseja atualizar o BCI STLA agora?';
      Result := (MsgBox(Msg, mbConfirmation, MB_YESNO) = IDYES);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir, SettFile, Content: String;
begin
  if CurStep = ssPostInstall then begin
    AppDataDir := ExpandConstant('{userappdata}\BCI-Knuckle');
    ForceDirectories(AppDataDir);
    SettFile := AppDataDir + '\settings.json';
    if WizardIsTaskSelected('autoupdate') then
      Content := '{"auto_update": true}'
    else
      Content := '{"auto_update": false}';
    SaveStringToFile(SettFile, Content, False);
  end;
end;
