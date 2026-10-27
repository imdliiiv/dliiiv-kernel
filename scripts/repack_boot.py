#!/usr/bin/env python3
"""
DLIIIV Boot Image Repacker for Android GKI (Boot Header v4 / v3)
Used for Nothing Phone (4a) Pro (froggerpro) and all GKI 2.0 devices.
Swaps the stock kernel with the compiled DLIIIV custom kernel Image.
"""

import sys
import os
import struct

BOOT_MAGIC = b"ANDROID!"
PAGE_SIZE = 4096

def align_to_page(size, page_size=PAGE_SIZE):
    return (size + page_size - 1) & ~(page_size - 1)

def repack(stock_boot_path, new_kernel_path, output_path):
    if not os.path.exists(stock_boot_path):
        print(f"[-] Error: Stock boot image not found: {stock_boot_path}")
        return False
    if not os.path.exists(new_kernel_path):
        print(f"[-] Error: New kernel Image not found: {new_kernel_path}")
        return False

    with open(stock_boot_path, "rb") as f:
        header_data = bytearray(f.read(PAGE_SIZE))

    if not header_data.startswith(BOOT_MAGIC):
        print("[-] Error: Not a valid Android boot image (magic 'ANDROID!' missing).")
        return False

    # Unpack header version
    # Offset 36 contains header_version uint32
    header_version = struct.unpack_from("<I", header_data, 36)[0]
    print(f"[+] Detected Boot Image Header Version: {header_version}")

    if header_version not in (3, 4):
        print(f"[-] Warning: Expected GKI Header v3 or v4, got v{header_version}.")

    orig_kernel_size = struct.unpack_from("<I", header_data, 8)[0]
    orig_ramdisk_size = struct.unpack_from("<I", header_data, 12)[0]
    print(f"[+] Original Kernel Size: {orig_kernel_size} bytes ({orig_kernel_size / 1024 / 1024:.2f} MB)")
    print(f"[+] Original Ramdisk Size: {orig_ramdisk_size} bytes (GKI boot partitions have ramdisk in init_boot)")

    with open(new_kernel_path, "rb") as f:
        new_kernel_data = f.read()

    new_kernel_size = len(new_kernel_data)
    print(f"[+] DLIIIV Kernel Size: {new_kernel_size} bytes ({new_kernel_size / 1024 / 1024:.2f} MB)")

    # Update kernel_size in header at offset 8
    struct.pack_into("<I", header_data, 8, new_kernel_size)

    # Signature handling for Header v4
    signature_data = b""
    if header_version >= 4:
        sig_size = struct.unpack_from("<I", header_data, 40)[0]
        if sig_size > 0:
            print(f"[+] Boot Signature Size: {sig_size} bytes")
            # Extract signature from stock boot
            orig_kernel_aligned = align_to_page(orig_kernel_size)
            orig_ramdisk_aligned = align_to_page(orig_ramdisk_size)
            sig_offset = PAGE_SIZE + orig_kernel_aligned + orig_ramdisk_aligned
            with open(stock_boot_path, "rb") as f:
                f.seek(sig_offset)
                signature_data = f.read(sig_size)

    # Write repacked boot image
    with open(output_path, "wb") as out:
        # 1. Header (4096 bytes)
        out.write(header_data)
        # 2. Kernel Image
        out.write(new_kernel_data)
        # Pad kernel to 4096 alignment
        pad_len = align_to_page(new_kernel_size) - new_kernel_size
        if pad_len > 0:
            out.write(b"\x00" * pad_len)
        # 3. Signature (if any)
        if signature_data:
            out.write(signature_data)
            sig_pad = align_to_page(len(signature_data)) - len(signature_data)
            if sig_pad > 0:
                out.write(b"\x00" * sig_pad)

    total_size = os.path.getsize(output_path)
    print(f"[+] Successfully repacked: {output_path} ({total_size / 1024 / 1024:.2f} MB)")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python repack_boot.py <stock_boot.img> <Image> [output_boot.img]")
        sys.exit(1)

    stock_boot = sys.argv[1]
    new_kernel = sys.argv[2]
    out_boot = sys.argv[3] if len(sys.argv) > 3 else "dliiiv_boot.img"

    success = repack(stock_boot, new_kernel, out_boot)
    sys.exit(0 if success else 1)
