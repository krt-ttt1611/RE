data = 0x467774475B8E5B57 | (0x8388858543568685 << 64) | (0x9081824487838885 << 64 + 32 + 8)
data_bytes = data.to_bytes(64*3, byteorder='little')


text = ''
char = 0
for count in range(0, 21):
	char = (data_bytes[count] - 19) & 0xff 
	text += chr(char)

print(text)