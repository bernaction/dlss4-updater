@echo off
echo ===============================
echo  ATUALIZADOR NVIDIA DLSS4    
echo ===============================
echo  Descoberta by Nigro e Caminotti
echo  Divulgado by CandidoN7    
echo  Script by Berna Cripto      
echo -                        
echo  Se inscrevam nos canais :)  
echo ===============================
echo -

echo Procedimentos do Script:
echo - Download das versões mais atuais dos arquivos NVIDIA DLSS4
echo - Procurar em pastas e subpastas seus arquivos DLL atuais
echo - Renomear os arquivos atuais para .old e fazer a cópia dos novos para o local
echo -

pause
cls

:: Recomeça o script
echo ===============================
echo  ATUALIZADOR NVIDIA DLSS4    
echo ===============================
echo -

setlocal enabledelayedexpansion

:: Define os nomes dos arquivos e URL base para download
set "dll_names=nvngx_dlss.dll nvngx_dlssd.dll nvngx_dlssg.dll"
set "temp_folder=%cd%\temp"
set "download_url_base=https://raw.githubusercontent.com/bernaction/dlss4-updater/main"

:: Cria a pasta temporária se ela não existir
if not exist "%temp_folder%" mkdir "%temp_folder%"

:: Baixa os 3 arquivos
for %%f in (%dll_names%) do (
    set "downloaded_file=%temp_folder%\%%f"
    echo Baixando %%f...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%download_url_base%/%%f', '%downloaded_file%')"
)

:: Inicializa as variáveis
set "found_files="
set "found_versions="
set "file_count=0"

:: Procura os 3 arquivos nas subpastas
echo Procurando os arquivos NVIDIA DLSS no diretório atual e subpastas...
for %%f in (%dll_names%) do (
    for /r %%i in (%%f) do (
        if /i not "%%~dpi"=="%temp_folder%\\" (
            if exist "%%i" (
                rem Incrementa o contador de arquivos encontrados
                set /a file_count+=1

                rem Adiciona o caminho do arquivo à lista
                set "found_files=!found_files! "%%i";"

                rem Obtém a versão do arquivo e armazena
                for /f "tokens=*" %%j in ('powershell -command "(Get-Item '%%i').VersionInfo.FileVersion" 2^>^&1') do (
                    echo [!file_count!] Arquivo encontrado: %%~i , versão: %%j

                    rem Adiciona a versão correspondente à lista
                    set "found_versions=!found_versions!%%j;"
                )
            )
        )
    )
)

:: Verifica se encontrou algum arquivo
if "!file_count!"=="0" (
    echo Nenhum arquivo foi encontrado.
    echo Finalizando o script.
    pause
    exit /b
)

:: Exibe a contagem de arquivos encontrados
echo Encontrado !file_count! arquivo(s).
echo -

:: Exibe as versões baixadas
for %%f in (%dll_names%) do (
    set "downloaded_file=%temp_folder%\%%f"
    set "new_version="
    for /f "tokens=*" %%k in ('powershell -command "& {(Get-Item '%downloaded_file%').VersionInfo.FileVersion}"') do set "new_version=%%k"
    echo Nova versão de %%f: !new_version!
)
echo -

:: Loop de atualização
set "index=1"
for %%i in (!found_files!) do (
    set "current_file=%%~i"
    set "current_version="

    rem Obtém a versão correspondente para o arquivo atual
    for /f "tokens=1* delims=;" %%v in ("!found_versions!") do (
        set "current_version=%%v"
        set "found_versions=!found_versions:%%v;=!"
    )

    echo -------------------------------------------------
    echo Arquivo !index!:
    echo DLL encontrada no local:
    echo "!current_file!"
    echo Versão atual: !current_version!
    echo -

    rem Pergunta ao usuário se deseja atualizar o arquivo
    :ask_choice
    set "choice="
    set /p "choice=Deseja atualizar este arquivo? [S/N]: "
    if /i "!choice!"=="S" (
        echo Criando backup e atualizando...
        if exist "!current_file!" (
            ren "!current_file!" "!current_file!.old"
            copy "%temp_folder%\%dll_name%" "!current_file!"
            echo Arquivo atualizado com sucesso.
            echo Backup criado como "!current_file!.old".
        ) else (
            echo O arquivo "!current_file!" não foi encontrado para renomeação.
        )
    ) else if /i "!choice!"=="N" (
        echo Pulando atualização deste arquivo...
    ) else (
        echo Escolha inválida. Por favor, responda com S ou N.
        goto ask_choice
    )

    set /a index+=1
)

:: Limpeza final
if exist "%temp_folder%" rmdir /s /q "%temp_folder%"
echo -
echo Operação concluída.
pause