import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1


def generate_keypair():
    """Sinh cặp khóa RSA 1024-bit với exponent = 17"""
    key = RSA.generate(1024, e=17)
    return key, key.publickey()


def make_license(name: str, private_key) -> str:
    """Tạo License hợp lệ với Private Key mới"""
    lic_type = "Single User License"
    lic_info = "EA7E-888888"  # ID hợp lệ

    payload = f"{name}\n{lic_type}\n{lic_info}".encode("utf-8")

    # Ký RSA PKCS#1 v1.5 + SHA-1
    h = SHA1.new(payload)
    signature = pkcs1_15.new(private_key).sign(h)
    sig_hex = signature.hex().upper()

    # Chia 256 ký tự hex thành 8 dòng, mỗi dòng 32 ký tự
    sig_lines = [sig_hex[i : i + 32] for i in range(0, len(sig_hex), 32)]

    license_body = [
        "----- BEGIN LICENSE -----",
        name,
        lic_type,
        lic_info,
        *sig_lines,
        "------ END LICENSE ------",
    ]
    return "\n".join(license_body)


def export_patch_bytes(public_key):
    """Xuất mảng bytes đã XOR 0xB3 để patch vào Binary"""
    # Xuất ra dạng DER SubjectPublicKeyInfo chuẩn X.509
    der_bytes = public_key.export_key(format="DER")
    assert (
        len(der_bytes) == 160
    ), f"Độ dài DER phải đúng 160 bytes (hiện tại {len(der_bytes)})"

    # Mã hóa XOR 0xB3
    patch_bytes = bytes([b ^ 0xB3 for b in der_bytes])

    # SHA256 trên chuỗi hex viết hoa (ASCII)
    h = hashlib.sha256(der_bytes.hex().upper().encode("ascii")).digest()

    print("\n[+] THÔNG TIN DÙNG ĐỂ PATCH FILE:")
    print("1. 160 bytes mới (XOR 0xB3) để ghi đè vào byte_7FF7A519D3E0:")
    print(patch_bytes.hex())
    print("\n2. 4 giá trị Hash mới cần sửa trong hàm check:")
    print(f"   byte 0  : {hex(h[0])} (gốc là 0xC6)")
    print(f"   byte 18 : {hex(h[18])} (gốc là 0xEA)")
    print(f"   byte 30 : {hex(h[30])} (gốc là 0x56)")
    print(f"   byte 31 : {hex(h[31])} (gốc là 0xEA)")


if __name__ == "__main__":
    priv, pub = generate_keypair()
    lic = make_license("Licensed User", priv)
    print("[+] LICENSE SINH RA TỪ PRIVATE KEY MỚI:\n")
    print(lic)
    export_patch_bytes(pub)