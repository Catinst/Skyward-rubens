"""Check a packed rubens vendor_boot against the supplied original image."""
import hashlib
from pathlib import Path
import struct
import sys

STOCK_SHA256 = "518f97f578fcc096c2eb54ba96e9bc7e37cee8d8b717bf0ae87f19bd3b814758"
SIZE = 64 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse(path):
    data = Path(path).read_bytes()
    require(len(data) == SIZE, f"{path}: expected a full 64 MiB image")
    require(data[:8] == b"VNDRBOOT", f"{path}: not vendor_boot")
    u32 = lambda at: struct.unpack_from("<I", data, at)[0]
    require(u32(8) == 4, f"{path}: expected header v4")
    page = u32(12)
    require(page == 4096, f"{path}: unexpected page size")
    align = lambda size: (size + page - 1) // page * page
    rd = align(u32(2096))
    dtb = rd + align(u32(24))
    table = dtb + align(u32(2100))
    bootconfig = table + align(u32(2112))
    require(u32(2116) == 1 and u32(2120) == 108, f"{path}: expected one v4 fragment")
    footer = data[-64:]
    require(footer[:4] == b"AVBf", f"{path}: no AVB footer")
    original_size, vbmeta_at, vbmeta_size = struct.unpack_from(">QQQ", footer, 12)
    require(bootconfig + align(u32(2124)) <= original_size <= vbmeta_at,
            f"{path}: inconsistent AVB image size")
    require(vbmeta_size > 0 and vbmeta_at + vbmeta_size <= SIZE - 64,
            f"{path}: invalid AVB metadata bounds")
    require(data[vbmeta_at:vbmeta_at + 4] == b"AVB0", f"{path}: missing vbmeta header")
    fragment = data[table:table + 108]
    fragment_size, fragment_offset = struct.unpack_from("<II", fragment)
    require(fragment_offset == 0 and fragment_size == u32(24),
            f"{path}: inconsistent ramdisk fragment")
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "platform_header": data[:24] + data[28:2100] + data[2104:2112],
        "dtb": data[dtb:dtb + u32(2100)],
        "fragment_identity": fragment[8:],
        "bootconfig": data[bootconfig:bootconfig + u32(2124)],
    }


def main():
    require(len(sys.argv) == 3, "usage: verify-rubens-image.py STOCK PACKED")
    stock, packed = map(parse, sys.argv[1:])
    require(stock["sha256"] == STOCK_SHA256, "original image SHA-256 mismatch")
    require(stock["sha256"] != packed["sha256"], "output image was not changed")
    for key in ("platform_header", "dtb", "fragment_identity", "bootconfig"):
        require(stock[key] == packed[key], f"packer changed {key}")
    print("Verified 64 MiB vendor_boot v4, AVB bounds, unchanged DTB and boot configuration")
    print(f"Packed SHA-256: {packed['sha256']}")


if __name__ == "__main__":
    main()
