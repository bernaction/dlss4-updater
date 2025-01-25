@echo off
echo ===============================
echo  ATUALIZADOR NVIDIA DLSS4    
echo ===============================
echo  Descoberta by CandidoN7     
echo  Script by Berna Cripto      
echo -                        
echo  Se inscrevam nos canais :)  
echo ===============================
echo -

echo Procedimentos do Script:
echo - Download da versao mais atual do arquivo NVIDIA DLSS4
echo - Procurar em pastas e subpastas seu arquivo DLL atual
echo - Renomear seu arquivo atual para .old e fazer a copia do novo para o local
echo -

pause
cls

:: Continue com o restante do script aqui
echo ===============================
echo  ATUALIZADOR NVIDIA DLSS4    
echo ===============================
echo -

setlocal enabledelayedexpansion

:: Define o nome do arquivo e URL para download
set "dll_name=nvngx_dlss.dll"
set "temp_folder=%cd%\temp"
set "downloaded_file=%temp_folder%\%dll_name%"
set "download_url=https://raw.githubusercontent.com/bernaction/dlss4-updater/main/nvngx_dlss.dll"

:: Cria a pasta temporária se ela não existir e deleta o arquivo antigo
if not exist "%temp_folder%" mkdir "%temp_folder%"
if exist "%downloaded_file%" del "%downloaded_file%"

:: Inicializa as variáveis
set "found_files="
set "found_versions="
set "file_count=0"

:: Procura o arquivo nas subpastas
echo Procurando o arquivo "%dll_name%" no diretorio atual e subpastas...
for /r %%i in (%dll_name%) do (
    if /i not "%%~dpi"=="%temp_folder%\\" (
        if exist "%%i" (
            rem Incrementa o contador de arquivos encontrados
            set /a file_count+=1

            rem Adiciona o caminho do arquivo à lista
			set "found_files=!found_files! "%%i";"

            rem Obtém a versão do arquivo e armazena
            for /f "tokens=*" %%j in ('powershell -command "(Get-Item '%%i').VersionInfo.FileVersion" 2^>^&1') do (
                echo [!file_count!] Arquivo encontrado: %%~i , versao: %%j

                rem Adiciona a versão correspondente à lista
                set "found_versions=!found_versions!%%j;"
            )
        )
    )
)

:: Verifica se encontrou algum arquivo
if "!file_count!"=="0" (
    echo Nenhum arquivo "%dll_name%" foi encontrado.
    echo Finalizando o script.
    pause
    exit /b
)

:: Exibe a contagem de arquivos encontrados
echo Encontrado !file_count! arquivo(s).
echo -

:: Rotina de download 
echo Fazendo download do arquivo "%dll_name%" em uma pasta temporaria...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%download_url%', '%downloaded_file%')"
set "new_version="
for /f "tokens=*" %%k in ('powershell -command "& {(Get-Item '%downloaded_file%').VersionInfo.FileVersion}"') do set "new_version=%%k"
echo Nova versao NVIDIA DLSS: %new_version%
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
    echo Versao atual: !current_version!
    echo -

    rem Pergunta ao usuário se deseja atualizar o arquivo
    :ask_choice
    set "choice="
    set /p "choice=Deseja atualizar este arquivo? [S/N]: "
    if /i "!choice!"=="S" (
        echo Criando backup e atualizando...
        if exist "!current_file!" (
            ren "!current_file!" "!dll_name!.old"
            copy "%downloaded_file%" "!current_file!"
            echo Arquivo atualizado com sucesso.
            echo Backup criado como "!dll_name!.old".
        ) else (
            echo O arquivo "!current_file!" nao foi encontrado para renomeacao.
        )
    ) else if /i "!choice!"=="N" (
        echo Pulando atualizacao deste arquivo...
    ) else (
        echo Escolha invalida. Por favor, responda com S ou N.
        goto ask_choice
    )

    set /a index+=1
)







:: Limpeza final
if exist "%downloaded_file%" del "%downloaded_file%"
rmdir /s /q "%temp_folder%"
echo -
echo -
echo Operacao concluida.
pause
