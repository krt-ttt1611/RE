ALPHABET = 'zph2xg0v1m7q_8n4rj6wcl9k5byaestudiof{}ISPCLUB'
PERM = [0, 7, 14, 21, 28, 35, 4, 11, 18, 25, 32, 1, 8, 15, 22, 29, 36, 5, 12, 19, 26, 33, 2, 9, 16, 23, 30, 37, 6, 13, 20, 27, 34, 3, 10, 17, 24, 31]
EXPECTED = [43, 23, 11, 40, 22, 12, 33, 2, 30, 41, 18, 17, 16, 32, 6, 8, 20, 5, 4, 44, 17, 10, 14, 19, 12, 18, 0, 28, 14, 32, 5, 18, 19, 6, 27, 18, 29, 10]

flag = [''] * len(EXPECTED)

for i in range(len(EXPECTED)):
    # Đảo ngược công thức: pos = (Expected - i*3 - 5) % len(ALPHABET)
    pos = (EXPECTED[PERM[i]] - i * 3 - 5) % len(ALPHABET)
    flag[i] = ALPHABET[pos]

print("".join(flag))

