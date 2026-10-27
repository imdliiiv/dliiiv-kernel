@echo off
echo ========================================================
echo  Nothing Phone (4a) Pro (froggerpro) Fastboot Kernel Flasher
echo ========================================================
echo.
echo Make sure your phone is in Fastboot Mode (Bootloader).
echo.

if not exist "%~1" (
    echo Error: Please drag and drop your patched boot image onto this script!
    echo Usage: flash_fastboot.bat patched_boot.img
    pause
    exit /b 1
)

set BOOT_IMG=%~1

echo Flashing %BOOT_IMG% to boot_a and boot_b...
fastboot flash boot_a "%BOOT_IMG%"
if %errorlevel% neq 0 (
    echo Failed to flash boot_a!
    pause
    exit /b 1
)

fastboot flash boot_b "%BOOT_IMG%"
if %errorlevel% neq 0 (
    echo Failed to flash boot_b!
    pause
    exit /b 1
)

echo.
echo Kernel successfully flashed! Rebooting to system...
fastboot reboot
echo.
echo Done! Once booted, install your BakaSU-Manager.apk.
pause
