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

:: Continue com o restante do script aqui

setlocal enabledelayedexpansion

:: Define o nome do arquivo e URL para download
set "dll_name=nvngx_dlss.dll"
set "download_url=https://raw.githubusercontent.com/bernaction/dlss4-updater/main/nvngx_dlss.dll"
set "downloaded_file=%cd%\%dll_name%"

:: Variáveis auxiliares
set "found_files="
set "found_versions="

:: Procura o arquivo nas subpastas
for /r %%i in (%dll_name%) do (
    if exist "%%i" (
        set "found_files=!found_files! "%%i";"
        for /f "tokens=*" %%j in ('powershell -command "& {(Get-Item '%%i').VersionInfo.FileVersion}"') do (
            set "found_versions=!found_versions!%%j;"
        )
    )
)

:: Verifica se encontrou algum arquivo
if "!found_files!"=="" (
    echo Nenhum arquivo "%dll_name%" foi encontrado no diretorio atual e suas subpastas.
    pause
    exit /b
)

:: Faz o download do arquivo na pasta atual
cls
echo ===============================
echo  ATUALIZADOR NVIDIA DLSS4    
echo ===============================
echo Fazendo download do arquivo "%dll_name%" na pasta atual...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%download_url%', '%downloaded_file%')"

:: Verifica a versão do arquivo baixado
set "new_version="
for /f "tokens=*" %%k in ('powershell -command "& {(Get-Item '%downloaded_file%').VersionInfo.FileVersion}"') do set "new_version=%%k"

echo Versao baixada do NVIDIA DLSS: %new_version%


:: Pergunta para atualizar cada arquivo encontrado
set "index=1"
for %%i in (!found_files!) do (
    set "current_file=%%~i"
    for /f "delims=;" %%v in ("!found_versions!") do (
        set "current_version=%%v"
        set "found_versions=!found_versions:%%v;=!"
        echo Arquivo %index%:
        echo Local: !current_file!
        echo Versao atual: !current_version!
        echo -------------------------------------------------
        
        :ask_choice
        set "choice="
        set /p "choice=Deseja atualizar este arquivo? [S/N]: "
        if /i "!choice!"=="S" (
            echo Criando backup e atualizando...
            if exist "!current_file!" (
                ren "!current_file!" "!dll_name!.old"
                copy "%downloaded_file%" "!current_file!"
                echo Arquivo atualizado com sucesso. Backup criado como "!dll_name!.old".
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
)

:: Limpeza final
if exist "%downloaded_file%" del "%downloaded_file%"
echo Operacao concluida.
pause
