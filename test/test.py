from PIL import Image

# Nhớ cài thư viện Pillow trước (pip install Pillow)
img = Image.open("dance.png").convert("RGB")
width, height = img.size

# Ảnh của mày chia làm 4 cột, 3 hàng
step_x = width // 4
step_y = height // 3

flag = ""

# Quét từng ô từ trái sang phải, từ trên xuống dưới
for y in range(0, height, step_y):
    for x in range(0, width, step_x):
        # Chấm màu ở tọa độ chính giữa mỗi ô cho chuẩn
        r, g, b = img.getpixel((x + step_x//2, y + step_y//2))
        
        # Bỏ qua mấy ô màu đen (RGB = 0,0,0) ở cuối
        if r == 0 and g == 0 and b == 0:
            continue
            
        # Chuyển số RGB thành ký tự ASCII rồi ghép lại
        flag += chr(r) + chr(g) + chr(b)

print("[+] Flag lòi ra nè:", flag)