**Endianness** là quy tắc định nghĩa thứ tự mà một vi xử lý (CPU) hoặc hệ thống mạng sử dụng để sắp xếp các **Byte** của một kiểu dữ liệu lớn (như số nguyên 32-bit, 64-bit) vào không gian bộ nhớ (RAM).

## 1. Quy Luật Thép (Cốt lõi để không bao giờ lú)

Trước khi phân biệt các loại Endian, phải nắm vững 2 nguyên lý bất di bất dịch:

1. **Thao tác trên CỤC, không thao tác trên HẠT:** Endianness chỉ thay đổi thứ tự của các **Byte** (khối 8-bit). Thứ tự của các **Bit** bên trong 1 Byte đó là **TUYỆT ĐỐI KHÔNG BAO GIỜ THAY ĐỔI**.
2. **Kích thước một "Nhát xẻng":** Các biến như `int` (32-bit / 4 Bytes) hay `long long` (64-bit / 8 Bytes) cần nhiều địa chỉ RAM liên tiếp để lưu trữ. Endianness quyết định việc nhét Byte nào vào địa chỉ thấp, Byte nào vào địa chỉ cao.

---

## 2. Little Endian (Kiến trúc x86, AMD64)

Đây là chuẩn phổ biến nhất trên các máy tính cá nhân hiện nay.

* **Định nghĩa:** Byte thấp nhất (Least Significant Byte - **LSB**) được lưu ở địa chỉ bộ nhớ **thấp nhất**.
* **Đặc điểm:** "Đầu nhỏ đi trước". Dữ liệu xếp trên RAM bị ngược so với cách con người đọc một con số, nhưng lại rất tối ưu cho vi xử lý khi làm toán (vì nó luôn tính toán từ hàng đơn vị trở lên).

### Ví dụ minh họa:

Lưu số nguyên 32-bit (Hệ Hex): `0x11223344`

* **Nhận diện Byte:** `11` là MSB (Cao nhất), `44` là LSB (Thấp nhất - Hàng đơn vị).

| Địa chỉ RAM | Chứa Byte (Little Endian) | Giải thích |
| :--- | :---: | :--- |
| `0x1000` | **`44`** | LSB (Byte thấp) nằm ở địa chỉ thấp nhất |
| `0x1001` | **`33`** | ... |
| `0x1002` | **`22`** | ... |
| `0x1003` | **`11`** | MSB (Byte cao) nằm ở địa chỉ cao nhất |

---

## 3. Big Endian (Kiến trúc Mạng, Motorola)

Thường được dùng trong các giao thức mạng (TCP/IP) hoặc các dòng chip kiến trúc cũ.

* **Định nghĩa:** Byte cao nhất (Most Significant Byte - **MSB**) được lưu ở địa chỉ bộ nhớ **thấp nhất**.