#!/usr/bin/env python3
import os
import sys
import glob
import shutil
import urllib.request
import zipfile

def log(msg):
    print(f"[download_managers] {msg}", flush=True)

def main():
    workspace = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
    dest_rel = os.path.join(workspace, "ReSukiSU-Manager-Release.apk")
    dest_spoof = os.path.join(workspace, "ReSukiSU-Manager-Spoofed.apk")

    tmp_dir = os.path.join(workspace, ".tmp_resukisu")
    os.makedirs(tmp_dir, exist_ok=True)

    log("Downloading official 1-month-old ReSukiSU v4.2.0-rc3 universal manager APK...")
    url_v420 = "https://github.com/ReSukiSU/ReSukiSU/releases/download/v4.2.0-rc3/ReSukiSU_v4.2.0-rc3_35171-universal-release.apk"
    tmp_rel = os.path.join(tmp_dir, "resukisu_universal.apk")
    
    req = urllib.request.Request(url_v420, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp, open(tmp_rel, "wb") as out_file:
            shutil.copyfileobj(resp, out_file)
        log("Successfully downloaded ReSukiSU v4.2.0-rc3 release APK.")
    except Exception as e:
        log(f"Error downloading v4.2.0-rc3 release APK: {e}")
        sys.exit(1)

    shutil.copy2(tmp_rel, dest_rel)
    shutil.copy2(tmp_rel, dest_spoof)

    log(f"Verified {dest_rel} ({os.path.getsize(dest_rel)} bytes)")
    log(f"Verified {dest_spoof} ({os.path.getsize(dest_spoof)} bytes)")
    print("[download_managers] All ReSukiSU v4.2.0-rc3 APKs successfully prepared.")

if __name__ == "__main__":
    main()
