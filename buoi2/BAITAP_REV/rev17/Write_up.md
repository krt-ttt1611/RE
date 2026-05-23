![](../../../image/Pasted%20image%2020260511173815.png)

file python -> đổi phần mở rộng thành .py
```python
#!/usr/bin/env python3
ALPHABET = 'zph2xg0v1m7q_8n4rj6wcl9k5byaestudiof{}ISPCLUB'
PERM = [0, 7, 14, 21, 28, 35, 4, 11, 18, 25, 32, 1, 8, 15, 22, 29, 36, 5, 12, 19, 26, 33, 2, 9, 16, 23, 30, 37, 6, 13, 20, 27, 34, 3, 10, 17, 24, 31]
EXPECTED = [43, 23, 11, 40, 22, 12, 33, 2, 30, 41, 18, 17, 16, 32, 6, 8, 20, 5, 4, 44, 17, 10, 14, 19, 12, 18, 0, 28, 14, 32, 5, 18, 19, 6, 27, 18, 29, 10]

def main() -> None:
    user = input("flag> ")
    if len(user) != len(EXPECTED):
        print("Wrong")
        return
    out = [0] * len(user)
    for i, ch in enumerate(user):
        pos = ALPHABET.index(ch)
        out[PERM[i]] = (pos + i * 3 + 5) % len(ALPHABET)
    if out == EXPECTED:
        print("Correct")
    else:
        print("Wrong")

if __name__ == "__main__":
    main()
```
Logic chương trình:

- Khối if dòng 8 kiểm tra độ dài của chuỗi nhập, nếu khác độ dài mảng expected thì sai
- Sau đó, khởi tạo 1 mảng out toàn các phần từ 0, độ dài bằng độ dài chuỗi nhập.
- Khối for ở dòng 12, i là index, ch là character. biến pos sẽ lấy chỉ số của phần tử ch trong chuỗi alphabet. 
- Mảng out được tạo bằng cách: Phần tử ở có chỉ số là perm[i] sẽ bằng (pos + i * 3 + 5) % chiều dài chuỗi alphabet.
- Nếu out == expected -> đúng.

Code giải mã:
```python
ALPHABET = 'zph2xg0v1m7q_8n4rj6wcl9k5byaestudiof{}ISPCLUB'
PERM = [0, 7, 14, 21, 28, 35, 4, 11, 18, 25, 32, 1, 8, 15, 22, 29, 36, 5, 12, 19, 26, 33, 2, 9, 16, 23, 30, 37, 6, 13, 20, 27, 34, 3, 10, 17, 24, 31]
EXPECTED = [43, 23, 11, 40, 22, 12, 33, 2, 30, 41, 18, 17, 16, 32, 6, 8, 20, 5, 4, 44, 17, 10, 14, 19, 12, 18, 0, 28, 14, 32, 5, 18, 19, 6, 27, 18, 29, 10]



text = ''
for i in range(len(EXPECTED)):
	alpha_copy = ALPHABET
	for j in range(len(ALPHABET)):
		if alpha_copy[j] == '.':
			continue
		elif (j + i * 3 + 5) % len(ALPHABET) == EXPECTED[PERM[i]]:
			text += alpha_copy[j]
			alpha_copy = alpha_copy[:1] + '.' + alpha_copy[2:]
	print(text, end = '')
	text = ''
```
Hoặc:
```python
ALPHABET = 'zph2xg0v1m7q_8n4rj6wcl9k5byaestudiof{}ISPCLUB'
PERM = [0, 7, 14, 21, 28, 35, 4, 11, 18, 25, 32, 1, 8, 15, 22, 29, 36, 5, 12, 19, 26, 33, 2, 9, 16, 23, 30, 37, 6, 13, 20, 27, 34, 3, 10, 17, 24, 31]
EXPECTED = [43, 23, 11, 40, 22, 12, 33, 2, 30, 41, 18, 17, 16, 32, 6, 8, 20, 5, 4, 44, 17, 10, 14, 19, 12, 18, 0, 28, 14, 32, 5, 18, 19, 6, 27, 18, 29, 10]

flag = [''] * len(EXPECTED)

for i in range(len(EXPECTED)):
    # Đảo ngược công thức: pos = (Expected - i*3 - 5) % len(ALPHABET)
    pos = (EXPECTED[PERM[i]] - i * 3 - 5) % len(ALPHABET)
    flag[i] = ALPHABET[pos]

print("".join(flag))
```

Phân tích cách 1: Ban đầu ý tưởng là xây dựng code brute-force, nhưng mà chạy thử thì ra đúng kết quả luôn. Nguyên nhân ở đây là: Phương trình ```out[PERM[i]] = (pos + i * 3 + 5) % len(ALPHABET)```luôn có 1 nghiệm pos duy nhất với mỗi vị trí i đã chọn (vì pos chạy từ 0 đến 44 < len = 45, nên khi chia lấy dư thì kết quả sẽ chạy từ 0 đến 44, không trùng lặp).

Phân tích cách 2: Cách này dùng biến đổi đồng dư thức:

		$out[PERM[i]] = (pos + i * 3 + 5) \bmod len(ALPHABET)$

		$\rightarrow out[PERM[i]] \equiv (pos + i * 3 + 5) \pmod{len(ALPHABET)}$

		$\rightarrow out[PERM[i]] - i * 3 - 5 \equiv (pos) \pmod{len(ALPHABET)}$

		$\rightarrow pos = out[PERM[i]] - i * 3 - 5 \mod len(ALPHABET)$

Kết hợp với việc phương trình chỉ có 1 nghiệm duy nhất nên ta mới có được phép biến đổi trên.

		