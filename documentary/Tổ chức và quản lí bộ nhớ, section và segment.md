
## 1. Cấu Trúc RAM & Cơ Chế Phân Trang (Paging) Của Hệ Điều Hành

Để hiểu file nhị phân nạp lên RAM như thế nào, ta phải hiểu luật quản lý đất đai của Hệ điều hành (OS).

* **Tầng Phần cứng (Ô nhớ - Memory Cell):** Bộ nhớ RAM vật lý bao gồm hàng tỷ ô nhớ. Mỗi ô nhớ có kích thước đúng **1 Byte** và có một địa chỉ vật lý duy nhất. CPU có thể can thiệp vào từng byte này.
* **Tầng Hệ điều hành (Trang nhớ - Page):** OS không quản lý lẻ tẻ từng byte. Nó sử dụng chip MMU (Memory Management Unit) để gom các ô nhớ liền kề thành các khối gọi là **Page (Trang)**. Ở hầu hết các kiến trúc hiện đại, **1 Page = 4KB (4096 bytes)**.

**Tại sao phải quản lý theo Page?**

1. **Tiết kiệm bảng quản lý:** Thay vì quản lý hàng tỷ dòng địa chỉ byte, OS chỉ cần quản lý hàng triệu dòng địa chỉ Page trong bảng `Page Table`.
2. **Quản lý quyền truy cập (RWX):** Quyền hạn (Read, Write, Execute) được cấp theo đơn vị Page. Nguyên một Page 4KB chỉ được mang MỘT BỘ QUYỀN DUY NHẤT. Không có chuyện nửa Page được Ghi, nửa Page chỉ Đọc.
3. **Tối ưu RAM ảo (Swap):** Dễ dàng hoán đổi các khối 4KB từ RAM xuống ổ cứng khi bộ nhớ bị đầy.

---

## 2. File Nhị Phân ELF & Cú Lừa "Hai Góc Nhìn"

Định dạng ELF (Linux/Unix) được thiết kế với hai nhân cách độc lập, phục vụ cho hai đối tượng khác nhau ở những thời điểm khác nhau:

### 2.1. Linking View (Góc nhìn Liên kết) - Quản lý bằng `Section`

* **Mục đích:** Dành cho lúc biên dịch (Build), liên kết (Link) và gỡ lỗi (Debug / Reverse Engineering).
* **Bản chất:** Chia nhỏ chương trình thành các ngăn kéo (Section) chứa các loại dữ liệu cụ thể.
* **Các Section "giang hồ cộm cán":**
  * `.text`: Chứa mã lệnh Assembly thực thi. Quyền: **R-X** (Đọc + Thực thi).
  * `.rodata`: Chứa hằng số, chuỗi string (Read-only data). Quyền: **R--** (Chỉ đọc).
  * `.data`: Chứa biến toàn cục/biến tĩnh đã được gán giá trị từ đầu. Quyền: **RW-** (Đọc + Ghi).
  * `.bss`: Chứa biến rỗng chưa gán giá trị. Đặc biệt: **Chiếm 0 byte trên ổ cứng**, OS tự động cấp RAM chứa toàn số 0 khi chạy. Quyền: **RW-**.
* **Định vị:** Quản lý bằng mảng `Section Header Table`, thường nằm ở **cuối file**.

### 2.2. Execution View (Góc nhìn Thực thi) - Quản lý bằng `Segment`

* **Mục đích:** Dành cho Hệ điều hành (OS Loader) khi nạp file vào RAM để chạy.
* **Bản chất:** OS lười, nó không nạp lẻ tẻ từng Section. Trình liên kết (Linker) sẽ **GOM CÁC SECTION CÓ CHUNG QUYỀN TRUY CẬP** lại thành các khối to gọi là **Segment** (VD: Gom `.text` và `.rodata` thành một Segment R-X).
* **Sự tối ưu hóa Paging:** * Thay vì cấp phát mỗi Section một Page riêng gây dư thừa và lãng phí RAM, OS chỉ việc bốc nguyên khối Segment ném vào các Page có chung thuộc tính quyền.
  * Giảm số lượng Page cần cấp phát, tiết kiệm RAM tối đa.
* **Định vị:** Quản lý bằng bảng `Program Header Table` (`e_phoff`), luôn nằm ở **đầu file**, ngay sát ELF Header.

---

## 3. Triết Lý Đối Lập: ELF (Linux) vs. PE (Windows)

Hai hệ sinh thái có cách tiếp cận hoàn toàn khác nhau về cấu trúc file:

| Đặc điểm | Định dạng ELF (Linux/Unix) | Định dạng PE (Windows) |
| :--- | :--- | :--- |
| **Góc nhìn (Views)** | Chia làm 2: Linking (Section) và Execution (Segment). | Hợp nhất làm 1 (Chỉ có Section). |
| **Bảng quản lý nạp RAM** | `Program Header Table` | `IMAGE_SECTION_HEADER` (Section tự gánh việc nạp RAM). |
| **Tối ưu RAM** | Gom nhóm thông minh qua Segment, tiết kiệm Page. | Tốn RAM hơn do phải làm tròn kích thước (Alignment) cho từng Section lên RAM. |
| **Bảo mật / Dịch ngược** | Lệnh `strip` dễ dàng chặt bỏ Section Header để