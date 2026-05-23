encrypt_string = "723a147273063915710e01720f711d16721d0116043f"
encrypt_char = list(bytes.fromhex(encrypt_string))
flag = ''
for i in range(len(encrypt_char)):
  char = encrypt_char[i] ^ 0x42
  flag += chr(char)

print(flag)