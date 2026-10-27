# DLIIIV Kernel for Nothing Phone (4a) Pro (froggerpro)

Custom Generic Kernel Image (GKI) 6.6 with **BakaSU**, **SUSFS**, **Bypass Charging**, **Flashlight/Torch Boost**, and **Performance Enhancements** specifically configured for Nothing Phone (4a) Pro (`froggerpro` / `A069P`) running Nothing OS 4.1 (Android 16).

---

## Features
- **Kernel Name:** `DLIIIV Kernel` (`6.6.127-android15-8-DLIIIV-4k`)
- **Kernel Base:** Google Android Common Kernel (ACK) `android15-6.6` (Sublevel `127`)
- **Architecture:** ARM64 with native **4KB Page Size** (`CONFIG_ARM64_4K_PAGES=y`)
- **Root Solution:** **BakaSU** (Kernel-level root with metamodule support)
- **Stealth & Hiding:** **SUSFS** (`susfs4ksu`) inline kernel hooks
- **Bypass Charging (Battery Idle Mode):** Hardware-level charging bypass via `/sys/kernel/dliiiv/bypass_charging`
- **Flashlight / Torch Boost Control:** Enhanced torch current override via `/sys/kernel/dliiiv/torch_boost` and unthrottled LED class
- **Performance Tweaks:**
  - Memory prefetch and 8-byte struct alignment
  - Cache hot buddy latency reduction
  - F2FS congestion reduction & fast fsync
  - S2idle wakeup optimization
- **Qualcomm PAKALA Safe:**
  - **Baseband Guard REMOVED** (Prevents modem panic / bootloop on Qualcomm chips)
  - **KMI generation preserved** (`-android15-8-`)
  - **Module Version Bypass applied** to guarantee all Nothing OS `/vendor_dlkm` drivers load cleanly
- **Automated Root Manager:** Bundles the **exact matching BakaSU Manager APK** (Zero Version Mismatch).

---

## How to Control Custom Features (Termux / Root Shell)

### 1. Bypass Charging (Battery Idle Mode)
Bypass charging allows you to run your device directly from the wall charger without charging or heating the battery (ideal for gaming, emulation, or long navigation).

* **Enable Bypass Charging (Stop battery charging, run from charger):**
  ```bash
  su -c "echo 1 > /sys/kernel/dliiiv/bypass_charging"
  ```
* **Disable Bypass Charging (Restore normal charging):**
  ```bash
  su -c "echo 0 > /sys/kernel/dliiiv/bypass_charging"
  ```
* **Check Status:**
  ```bash
  su -c "cat /sys/kernel/dliiiv/bypass_charging"
  ```
  *(1 = Bypass Active, 0 = Normal Charging)*

---

### 2. Flashlight / Torch Control
* **Set Torch Boost Level (0 - 255):**
  ```bash
  su -c "echo 255 > /sys/kernel/dliiiv/torch_boost"
  ```
* Works seamlessly with apps like **FlashDim** to achieve full unthrottled hardware brightness steps.

---

## How to Build via GitHub Actions

1. Create an empty repository on GitHub named `dliiiv-kernel`.
2. Push this folder to your repository:
   ```bash
   git init
   git add .
   git commit -m "DLIIIV Kernel with BakaSU, SUSFS, Bypass Charging and Torch Control"
   git branch -M main
   git remote add origin https://github.com/<your-username>/dliiiv-kernel.git
   git push -u origin main
   ```
3. Open your repo on GitHub $\rightarrow$ **Actions** tab $\rightarrow$ select **Build DLIIIV Custom Kernel (FroggerPro)** $\rightarrow$ click **Run workflow**.
4. Download the **`DLIIIV-Kernel-FroggerPro-Release`** artifact when complete.

---

## Flashing Instructions

### Method 1: Kernel Flasher App (Recommended if currently rooted)
1. Install **Kernel Flasher** on your device.
2. Select `DLIIIV-Kernel-FroggerPro.zip` and flash to active slot.
3. Reboot and install `BakaSU-Manager.apk`.

### Method 2: Fastboot Repack (Safe Stock Flashing)
1. Extract `Image` from `DLIIIV-Kernel-FroggerPro.zip`.
2. Extract the stock `boot.img` from your Nothing OS firmware (available on [Nothing Archive](https://nothingarchive.tech/docs/firmware#froggerpro)).
3. Using `magiskboot`:
   ```bash
   magiskboot unpack boot.img
   cp Image kernel
   magiskboot repack boot.img new_boot.img
   ```
4. Flash via Fastboot:
   ```bash
   fastboot flash boot_a new_boot.img
   fastboot flash boot_b new_boot.img
   fastboot reboot
   ```
5. Install `BakaSU-Manager.apk`.
