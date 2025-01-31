import os
import sys
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


def print_header():
    print("=" * 30)
    print(" NVIDIA DLSS4 UPDATER")
    print("=" * 30)
    print("\nDiscovered by Nigro and Caminotti")
    print("Published by CandidoN7")
    print("Script by Berna Cripto")
    print("=" * 30)
    print(f"\nScript Procedures:")
    print("- Download the latest versions of NVIDIA DLSS4 files")
    print("- Search for your current DLL files in folders and subfolders")
    print("- Restore backups if necessary")
    print("- Rename current files to .old and copy the new versions to the location")
    print("-" * 30)

def end_script():
    shutil.rmtree(temp_folder, ignore_errors=True)
    input("Press ENTER to exit.")
    sys.exit()

def fetch_available_versions():
    response = requests.get(github_api_url)
    if response.status_code != 200:
        raise Exception(f"Error accessing the GitHub API: {response.status_code} - {response.text}")
    items = response.json()
    versions = [item['name'] for item in items if item['type'] == 'dir']
    if not versions:
        raise Exception("No versions found in the repository.")
    return versions


def select_version(available_versions):
    print(f"\n=== Choose the version you want to download ===")
    print("[0] Exit")  # Adds option 0 to exit
    for idx, version in enumerate(available_versions, start=1):
        print(f"[{idx}] {version}".replace(',', '.'))

    while True:
        try:
            choice = int(input("\nEnter the number of the desired version: "))
            if choice == 0:
                print("Exiting the script...")
                end_script()
            if 1 <= choice <= len(available_versions):
                return available_versions[choice - 1]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def get_file_version(file_path):
    try:
        info = GetFileVersionInfo(str(file_path), "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{HIWORD(ms)},{LOWORD(ms)},{HIWORD(ls)},{LOWORD(ls)}"
    except:
        return "Unknown"


def download_with_progress(url, dest_file):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB

    with open(dest_file, "wb") as f, tqdm(
        desc=f"Downloading {dest_file.name}",
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
                bar.set_postfix(speed=f"{(bar.n / 1024) / elapsed_time:.2f} KB/s")


def find_existing_files():
    found_files = []
    found_versions = []
    print("=" * 30)
    print("=== Searching for NVIDIA DLSS files in the current directory and subfolders... ===")

    for root, _, files in os.walk(Path.cwd()):
        root_path = Path(root)

        if root_path == temp_folder or temp_folder in root_path.parents:
            continue

        if "$RECYCLE.BIN" in root_path.parts:
            continue

        for file in files:
            if file in dll_names:
                file_path = root_path / file
                version = get_file_version(file_path)
                found_files.append(file_path)
                found_versions.append(version)
                print(f"[{len(found_files)}] File found: {file_path}, version: {version}".replace(',', '.'))

    return found_files, found_versions


def find_backups():
    backup_files = []
    print("=" * 30)
    print(" NVIDIA DLSS4 UPDATER")
    print("=" * 30)
    print("Searching for backup files (.old)...")
    for root, _, files in os.walk(Path.cwd()):
        for file in files:
            if ".old." in file:
                backup_files.append(Path(root) / file)
    if not backup_files:
        print("No backup files found.")
    else:
        print(f"Total backup files found: {len(backup_files)}")
    return backup_files


def restore_backup(backup_files):
    grouped_backups = {}

    for backup in backup_files:
        folder = backup.parent
        base_name, version = backup.name.rsplit(".old.", 1)  
        if folder not in grouped_backups:
            grouped_backups[folder] = {}
        if base_name not in grouped_backups[folder]:
            grouped_backups[folder][base_name] = []
        grouped_backups[folder][base_name].append((backup, version))

    for folder, files in grouped_backups.items():
        for base_name, backups in files.items():
            print(f"\nIn folder: {folder}")

            all_backups = ", ".join(backup[0].name for backup in backups)
            print(f"Found files: {all_backups}")

            print("Available versions for restoration:")
            print("[0] Ignore this file")  
            for idx, (backup, version) in enumerate(backups, start=1):
                print(f"[{idx}] {version}".replace(',', '.'))

            while True:
                try:
                    choice = int(input("\nEnter the number of the version you want to restore (or 0 to ignore): "))
                    if choice == 0:
                        print("Skipping restoration of this file...")
                        break
                    elif 1 <= choice <= len(backups):
                        selected_backup, _ = backups[choice - 1]
                        original_file = folder / base_name
                        print(f"Restoring backup: {selected_backup.name}")
                        print(f"Original file will be restored as: {original_file.name}")

                        try:
                            if original_file.exists():
                                print(f"Removing current file: {original_file.name}")
                                original_file.unlink()
                            selected_backup.rename(original_file)
                            print(f"Backup successfully restored: {original_file.name}")
                        except Exception as e:
                            print(f"Error restoring backup: {e}")
                        break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a valid number.")

            print("-" * 50)


print_header()
input("Press ENTER to continue...")
os.system('cls' if os.name == 'nt' else 'clear')

backup_files = find_backups()
if backup_files:
    print("\n=== Options ===")
    print("[0] Exit script")
    print("[1] Restore backups")
    print("[2] Continue to download")
    while True:
        try:
            initial_choice = int(input("\nChoose an option: "))
            if initial_choice == 0:
                print("Exiting the script...")
                end_script()
            if initial_choice == 1:
                restore_backup(backup_files)
                break
            elif initial_choice == 2:
                break
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")

try:
    available_versions = fetch_available_versions()
    selected_version = select_version(available_versions)
    print(f"Selected version: {selected_version}\n".replace(',', '.'))
except Exception as e:
    print(f"Error fetching versions: {e}")
    exit()

temp_folder.mkdir(exist_ok=True)

print("Starting downloads...")
for dll in dll_names:
    temp_file = temp_folder / dll
    download_url = f"{raw_base_url}/{selected_version}/{dll}"
    download_with_progress(download_url, temp_file)
    version = get_file_version(temp_file)
    print(f"Completed. Version: {version}\n".replace(',', '.'))

found_files, found_versions = find_existing_files()

if not found_files:
    shutil.rmtree(temp_folder, ignore_errors=True)
    print("No files were found. Exiting the script.")
    end_script()

print("-" * 50)

for index, (file_path, version) in enumerate(zip(found_files, found_versions), start=1):
    file_name = file_path.name
    new_version = get_file_version(temp_folder / file_name)

    print(f"\n[{index}] In folder:\n{file_path.parent}")
    print(f"Found file: {file_name}")
    print(f"Current version: {version}".replace(',', '.'))
    print(f"New available version: {new_version}")

    choice = input("\nDo you want to update this file? [Y/N]: ").strip().lower()

    if choice == "y":
        backup_name = f"{file_path}.old.{version}"
        backup_file = file_path.parent / f"{file_name}.old.{version}"  # File name only

        if backup_file.exists():
            print(f"Backup already exists. Skipping backup creation: {backup_file.name}")
        else:
            try:
                file_path.rename(backup_file)
                print(f"Backup created as: {backup_file.name}")
            except Exception as e:
                print(f"Error creating backup: {e}")

        try:
            shutil.copy(temp_folder / file_name, file_path)
            print(f"File successfully updated: {file_name}")
        except Exception as e:
            print(f"Error updating the file: {e}")
    elif choice == "n":
        print("Skipping update for this file...")
    else:
        print("Invalid choice. Skipped this file.")

    print("-" * 50)

end_script()




