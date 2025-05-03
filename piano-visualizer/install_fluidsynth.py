import os
import zipfile
import requests
import shutil

FLUIDSYNTH_URL = "https://github.com/FluidSynth/fluidsynth/releases/download/v2.3.4/fluidsynth-2.3.4-win10-x64.zip"
SOUNDFONT_URL = "https://github.com/urish/cinto/raw/refs/heads/master/media/FluidR3%20GM.sf2"

FLUIDSYNTH_DIR = r"C:\tools\fluidsynth"
SOUNDFONT_DIR = r"C:\ProgramData\soundfonts"
SOUNDFONT_PATH = os.path.join(SOUNDFONT_DIR, "default.sf2")

def download_file(url, output_path):
    print(f"Downloading {url}...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved to {output_path}")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path} to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

def ensure_folders():
    os.makedirs(FLUIDSYNTH_DIR, exist_ok=True)
    os.makedirs(SOUNDFONT_DIR, exist_ok=True)

def setup_fluidsynth():
    fluidsynth_exe = os.path.join(FLUIDSYNTH_DIR, "bin", "fluidsynth.exe")
    if not os.path.exists(fluidsynth_exe):
        zip_path = os.path.join(FLUIDSYNTH_DIR, "fluidsynth.zip")
        download_file(FLUIDSYNTH_URL, zip_path)
        extract_zip(zip_path, FLUIDSYNTH_DIR)
        os.remove(zip_path)
    else:
        print("FluidSynth already installed.")

def setup_soundfont():
    if not os.path.exists(SOUNDFONT_PATH):
        download_file(SOUNDFONT_URL, SOUNDFONT_PATH)
    else:
        print("SoundFont already present.")

def main():
    ensure_folders()
    setup_fluidsynth()
    setup_soundfont()
    print("Setup complete. FluidSynth is ready to use.")

if __name__ == "__main__":
    main()
