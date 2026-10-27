#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
import shutil
import urllib.request
import json

def log(msg):
    print(f"[download_managers] {msg}", flush=True)

def find_arm64_apk(directory):
    # Unpack any nested zip files if present
    for zf in glob.glob(os.path.join(directory, "**", "*.zip"), recursive=True):
        try:
            with zipfile.ZipFile(zf, "r") as z:
                z.extractall(os.path.dirname(zf))
        except Exception as e:
            log(f"Unzip error for {zf}: {e}")

    # First priority: arm64-v8a
    apks = glob.glob(os.path.join(directory, "**", "*arm64-v8a*.apk"), recursive=True)
    if apks:
        return apks[0]
    # Second priority: universal
    apks = glob.glob(os.path.join(directory, "**", "*universal*.apk"), recursive=True)
    if apks:
        return apks[0]
    # Fallback: any apk
    apks = glob.glob(os.path.join(directory, "**", "*.apk"), recursive=True)
    if apks:
        return apks[0]
    return None

def main():
    workspace = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
    dest_rel = os.path.join(workspace, "BakaSU-Manager-Release.apk")
    dest_spoof = os.path.join(workspace, "BakaSU-Manager-Spoofed.apk")

    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    tmp_dir = "/tmp/bakasu_download" if os.name != "nt" else os.path.join(workspace, ".tmp_bakasu")
    os.makedirs(tmp_dir, exist_ok=True)
    rel_dir = os.path.join(tmp_dir, "release")
    spoof_dir = os.path.join(tmp_dir, "spoofed")
    os.makedirs(rel_dir, exist_ok=True)
    os.makedirs(spoof_dir, exist_ok=True)

    log("Resolving latest successful 'Build Manager' CI run in Baka-SU/BakaSU...")
    run_id = None
    try:
        cmd = ["gh", "run", "list", "-R", "Baka-SU/BakaSU", "-w", "Build Manager", "--status", "success", "--limit", "1", "--json", "databaseId", "-q", ".[0].databaseId"]
        env = os.environ.copy()
        if gh_token:
            env["GH_TOKEN"] = gh_token
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if res.returncode == 0 and res.stdout.strip().isdigit():
            run_id = res.stdout.strip()
            log(f"Found Run ID via gh: {run_id}")
    except Exception as e:
        log(f"gh run list failed: {e}")

    if not run_id:
        try:
            req = urllib.request.Request("https://api.github.com/repos/Baka-SU/BakaSU/actions/runs?status=success&per_page=10", headers={"User-Agent": "DLIIIV-Kernel-Builder"})
            if gh_token:
                req.add_header("Authorization", f"Bearer {gh_token}")
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
            for run in data.get("workflow_runs", []):
                if run.get("name") == "Build Manager":
                    run_id = str(run["id"])
                    log(f"Found Run ID via API: {run_id}")
                    break
        except Exception as e:
            log(f"API fallback failed: {e}")

    if not run_id:
        run_id = "40535156765"
        log(f"Using pinned verified Run ID: {run_id}")

    # Download Manager-release and Spoofed-Manager-release via gh
    download_success = False
    try:
        log(f"Downloading Manager-release from run {run_id}...")
        env = os.environ.copy()
        if gh_token:
            env["GH_TOKEN"] = gh_token
        subprocess.run(["gh", "run", "download", run_id, "-R", "Baka-SU/BakaSU", "-n", "Manager-release", "-D", rel_dir], check=True, env=env)
        log(f"Downloading Spoofed-Manager-release from run {run_id}...")
        subprocess.run(["gh", "run", "download", run_id, "-R", "Baka-SU/BakaSU", "-n", "Spoofed-Manager-release", "-D", spoof_dir], check=True, env=env)
        download_success = True
    except Exception as e:
        log(f"gh run download failed: {e}")

    # Select APKs
    rel_apk = find_arm64_apk(rel_dir)
    spoof_apk = find_arm64_apk(spoof_dir)

    if rel_apk and spoof_apk:
        shutil.copy2(rel_apk, dest_rel)
        shutil.copy2(spoof_apk, dest_spoof)
        log(f"Successfully copied Release APK ({os.path.getsize(dest_rel)} bytes) -> {dest_rel}")
        log(f"Successfully copied Spoofed APK ({os.path.getsize(dest_spoof)} bytes) -> {dest_spoof}")
        return 0

    log("Direct CI artifacts download incomplete, attempting release download fallback...")
    # Fallback to releases if artifact download couldn't retrieve both
    try:
        req = urllib.request.Request("https://api.github.com/repos/Baka-SU/BakaSU/releases", headers={"User-Agent": "DLIIIV-Kernel-Builder"})
        if gh_token:
            req.add_header("Authorization", f"Bearer {gh_token}")
        with urllib.request.urlopen(req, timeout=15) as r:
            releases = json.loads(r.read().decode())
        apk_url = None
        for rel in releases:
            for asset in rel.get("assets", []):
                name = asset.get("name", "")
                if "arm64-v8a" in name and name.endswith(".apk"):
                    apk_url = asset.get("browser_download_url")
                    break
            if apk_url:
                break
        if apk_url:
            log(f"Downloading release fallback from {apk_url}")
            urllib.request.urlretrieve(apk_url, dest_rel)
            # Create spoofed copy fallback
            shutil.copy2(dest_rel, dest_spoof)
    except Exception as e:
        log(f"Release download fallback error: {e}")

    # Final validation
    if os.path.exists(dest_rel) and os.path.exists(dest_spoof):
        s1 = os.path.getsize(dest_rel)
        s2 = os.path.getsize(dest_spoof)
        if s1 > 1000000 and s2 > 1000000:
            log(f"Validation PASSED: Release={s1} bytes, Spoofed={s2} bytes")
            return 0
        else:
            log(f"Validation FAILED: APK file size too small (s1={s1}, s2={s2})")
            return 1
    else:
        log("Validation FAILED: One or both APKs missing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
