import os
import shutil
import requests
from pathlib import Path
from tqdm import tqdm
from time import time
from win32api import GetFileVersionInfo, LOWORD, HIWORD

# Configurações
dll_names = ["nvngx_dlss.dll", "nvngx_dlssd.dll", "nvngx_dlssg.dll"]
temp_folder = Path.cwd() / "temp"
download_url_base = "https://raw.githubusercontent.com/bernaction/dlss4-updater/main"

# Cabeçalho do script
def print_header():
    print("=" * 30)
    print(" ATUALIZADOR NVIDIA DLSS4")
    print("=" * 30)
    print(" Descoberta by Nigro e Caminotti")
    print(" Divulgado by CandidoN7")
    print(" Script by Berna Cripto")
    print("-" * 30)
    print(" Se inscrevam nos canais :)")
    print("=" * 30)
    print("\nProcedimentos do Script:")
    print("- Download das versões mais atuais dos arquivos NVIDIA DLSS4")
    print("- Procurar em pastas e subpastas seus arquivos DLL atuais")
    print("- Renomear os arquivos atuais para .old e fazer a cópia dos novos para o local")
    print("-" * 30)

# Função para obter a versão de um arquivo
def get_file_version(file_path):
    try:
        info = GetFileVersionInfo(str(file_path), "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{HIWORD(ms)},{LOWORD(ms)},{HIWORD(ls)},{LOWORD(ls)}"
    except:
        return "Desconhecida"

# Função para fazer download com barra de progresso e velocidade
def download_with_progress(url, dest_file):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB

    with open(dest_file, "wb") as f, tqdm(
        desc=f"Baixando {dest_file.name}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        start_time = time()
        for data in response.iter_content(block_size):
            f.write(data)
            bar.update(len(data))
            elapsed_time = time() - start_time
            if elapsed_time > 0:
                bar.set_postfix(velocidade=f"{(bar.n / 1024) / elapsed_time:.2f} KB/s")







# Função para buscar arquivos DLL nas subpastas (ignorando temp e $RECYCLE.BIN)
def find_existing_files():
    found_files = []
    found_versions = []
    print("Procurando os arquivos NVIDIA DLSS no diretório atual e subpastas...")

    for root, _, files in os.walk(Path.cwd()):
        root_path = Path(root)

        # Ignorar a pasta temp EXATAMENTE e seus arquivos
        if root_path == temp_folder or temp_folder in root_path.parents:
            continue  # Pula a iteração, sem processar nada dessa pasta

        # Ignorar a lixeira do Windows ($RECYCLE.BIN)
        if "$RECYCLE.BIN" in root_path.parts:
            continue

        for file in files:
            if file in dll_names:
                file_path = root_path / file
                version = get_file_version(file_path)
                found_files.append(file_path)
                found_versions.append(version)
                print(f"[{len(found_files)}] Arquivo encontrado: {file_path}, versão: {version}")

    return found_files, found_versions


# Exibir cabeçalho
print_header()
input("Pressione ENTER para continuar...")
os.system('cls' if os.name == 'nt' else 'clear')

# Criar a pasta temporária
temp_folder.mkdir(exist_ok=True)

# Download dos arquivos
print("Iniciando downloads...\n")
for dll in dll_names:
    temp_file = temp_folder / dll
    download_with_progress(f"{download_url_base}/{dll}", temp_file)
    version = get_file_version(temp_file)
    print(f"Concluído. Versão: {version}\n")

# Procurar arquivos DLL no sistema (ignorando temp)
found_files, found_versions = find_existing_files()

if not found_files:
    print("Nenhum arquivo foi encontrado. Finalizando o script.")
    exit()

print("-" * 50)

# Atualização dos arquivos encontrados
for index, (file_path, version) in enumerate(zip(found_files, found_versions), start=1):
    file_name = file_path.name  # Nome do arquivo
    new_version = get_file_version(temp_folder / file_name)  # Nova versão do arquivo baixado

    print(f"Arquivo {index}:")
    print(f"DLL encontrada no local: {file_path}")
    print(f"Nova versão disponível: {new_version}")

    choice = input(f"Deseja atualizar este arquivo?\n"
                   f"De: {version} para: {new_version}\n"
                   f"Entre com [S/N]: ").strip().lower()
    
    if choice == "s":
        backup_name = f"{file_path}.old.{version}"
        try:
            # Criar backup do arquivo atual
            file_path.rename(backup_name)
            # Copiar o arquivo atualizado
            shutil.copy(temp_folder / file_path.name, file_path)
            print(f"Arquivo atualizado com sucesso.\nBackup criado como: {backup_name}")
        except Exception as e:
            print(f"Erro ao atualizar o arquivo: {e}")
    elif choice == "n":
        print("Pulando atualização deste arquivo...")
    else:
        print("Escolha inválida. Pulei este arquivo.")
    
    print("-" * 50)

# Limpeza final
shutil.rmtree(temp_folder, ignore_errors=True)
print("Operação concluída.")
input("Pressione ENTER para fechar.")
