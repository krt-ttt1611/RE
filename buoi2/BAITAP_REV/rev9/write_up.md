![](../../../ảnh/Pasted%20image%2020260426231957.png)
đây là script python, đổi phần mở rộng file thành .py để đọc.
![](../../../ảnh/Pasted%20image%2020260426232046.png)
ord(): chuyển từ text --> dec.

- Đầu tiên, ta biết chuỗi giải mã có độ dài 34. 
- Đọc vòng for từ dòng 14, ta biết rằng chuỗi được đưa vào 1 vòng for và duyệt với bước nhảy bằng 2. Giả sử duyệt tới vị trí i. hàm back_pair sẽ lấy kí tự tại i và kí tự tại i+1, cùng với phần nguyên của phép chia lấy phần nguyên i cho 2 để làm tham số. Giá trị trả về từ hàm back_pair sẽ được so sánh với 1 phần tử trong mảng EXPECTED có chỉ số là phép chia lấy phần nguyên của i cho 2.
- Nhìn vào hàm back_pair, với tham số left (là kí tự chỉ số i) sẽ được chuyển thành mã unicode ở dạng decimal, sau đó xor với (0x21 + tham số index (là i chia lấy phần nguyên cho 2) và được gói gọn trong 1 byte)

Code giải mã:
```python
e = [26641, 30734, 25357, 29720, 18951, 8220, 5351, 15086, 11241, 16333, 3796, 3044, 433, 5006, 57765, 65154, 57999]


text = ''
char1 = ''
char2 = ''
for i in range(0, 34, 2):
	char1 = ((e[i//2] & 130816) >> 8) ^ ((0x21 + (i//2)*7) & 0xff)
	char2 = (e[i//2] & 0xff) ^ ((0x42 + (i//2)*11) & 0xff)
	text += chr(char1) + chr(char2)

print(text)
```
Flag là: ISPCLUB{wide_chars_hide_two_bytes}
