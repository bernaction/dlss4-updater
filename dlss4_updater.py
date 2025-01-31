import os
import shutil
import requests
from pathlib import Path
from tqdm import tqdm
from time import time
from win32api import GetFileVersionInfo, LOWORD, HIWORD
from bs4 import BeautifulSoup

# Configurações
dll_names = ["nvngx_dlss.dll", "nvngx_dlssd.dll", "nvngx_dlssg.dll"]
temp_folder = Path.cwd() / "temp"
raw_base_url = "https://raw.githubusercontent.com/bernaction/dlss4-updater/main/dll"
github_api_url = "https://api.github.com/repos/bernaction/dlss4-updater/contents/dll"
dll_base_path = "/dll/"


def print_header():
    print("=" * 30)
    print(" ATUALIZADOR NVIDIA DLSS4")
    print("=" * 30)
    print("\nDescoberta by Nigro e Caminotti")
    print("Divulgado by CandidoN7")
    print("Script by Berna Cripto")
    print("=" * 30)
    print(f"\nProcedimentos do Script:")
    print("- Download das versões mais atuais dos arquivos NVIDIA DLSS4")
    print("- Procurar em pastas e subpastas seus arquivos DLL atuais")
    print("- Renomear os arquivos atuais para .old e fazer a cópia dos novos para o local")
    print("-" * 30)

def fetch_available_versions():
    response = requests.get(github_api_url)
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a API do GitHub: {response.status_code} - {response.text}")
    items = response.json()
    versions = [item['name'] for item in items if item['type'] == 'dir']
    if not versions:
        raise Exception("Nenhuma versão encontrada no repositório.")
    return versions

def select_version(available_versions):
    print("=" * 30)
    print(" ATUALIZADOR NVIDIA DLSS4")
    print("=" * 30)
    print(f"\n=== Escolha a versão que deseja baixar ===")
    for idx, version in enumerate(available_versions, start=1):
        print(f"[{idx}] {version}")

    while True:
        try:
            choice = int(input("\nDigite o número da versão desejada: "))
            if 1 <= choice <= len(available_versions):
                return available_versions[choice - 1]
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

def get_file_version(file_path):
    try:
        info = GetFileVersionInfo(str(file_path), "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{HIWORD(ms)},{LOWORD(ms)},{HIWORD(ls)},{LOWORD(ls)}"
    except:
        return "Desconhecida"

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

def find_existing_files():
    found_files = []
    found_versions = []
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 30)
    print(" ATUALIZADOR NVIDIA DLSS4")
    print("=" * 30)
    print(f"\n=== Procurando os arquivos NVIDIA DLSS no diretório atual e subpastas... ===")

    for root, _, files in os.walk(Path.cwd()):
        root_path = Path(root)

        # Ignorar a pasta temp
        if root_path == temp_folder or temp_folder in root_path.parents:
            continue

        # Ignorar a lixeira do Windows ($RECYCLE.BIN)
        if "$RECYCLE.BIN" in root_path.parts:
            continue

        for file in files:
            if file in dll_names:
                file_path = root_path / file
                version = get_file_version(file_path)
                found_files.append(file_path)
                found_versions.append(version)
                print(f"[{len(found_files)}] Arquivo encontrado: {file_path}, versão: {version}".replace(',', '.'))

    return found_files, found_versions




print_header()
input("Pressione ENTER para continuar...")
os.system('cls' if os.name == 'nt' else 'clear')

try:
    available_versions = fetch_available_versions()
    selected_version = select_version(available_versions)
    print(f"Escohido: {selected_version}\n".replace(',', '.'))
except Exception as e:
    print(f"Erro ao buscar versões: {e}")
    exit()

temp_folder.mkdir(exist_ok=True)

print("Iniciando downloads...")
for dll in dll_names:
    temp_file = temp_folder / dll
    download_url = f"{raw_base_url}/{selected_version}/{dll}"
    download_with_progress(download_url, temp_file)
    version = get_file_version(temp_file)
    print(f"Concluído. Versão: {version}\n".replace(',', '.'))

found_files, found_versions = find_existing_files()

if not found_files:
    print("Nenhum arquivo foi encontrado. Finalizando o script.")
    exit()

print("-" * 50)

for index, (file_path, version) in enumerate(zip(found_files, found_versions), start=1):
    file_name = file_path.name
    new_version = get_file_version(temp_folder / file_name) 

    print(f"Arquivo {index}:")
    print(f"DLL encontrada no local: {file_path}")

    choice = input(f"Deseja atualizar este arquivo? De: {version} para: {new_version}\n".replace(',', '.') +
                   f"Entre com [S/N]: ").strip().lower()

    if choice == "s":
        backup_name = f"{file_path}.old.{version}"
        try:
            file_path.rename(backup_name)
            shutil.copy(temp_folder / file_path.name, file_path)
            print(f"Arquivo atualizado com sucesso.\nBackup criado como: {backup_name}")
        except Exception as e:
            print(f"Erro ao atualizar o arquivo: {e}")
    elif choice == "n":
        print("Pulando atualização deste arquivo...")
    else:
        print("Escolha inválida. Pulei este arquivo.")

    print("-" * 50)

shutil.rmtree(temp_folder, ignore_errors=True)
print("Operação concluída.")
input("Pressione ENTER para fechar.")