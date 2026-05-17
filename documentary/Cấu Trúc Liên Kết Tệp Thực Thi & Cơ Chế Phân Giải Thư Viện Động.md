## 1. Trình Liên Kết: Tĩnh (Static) vs Động (Dynamic)

Quá trình biên dịch (Compilation) sinh ra hai loại Trình liên kết hoạt động ở hai mốc thời gian hoàn toàn khác biệt:

| Tiêu chí | Trình liên kết tĩnh (Static Linker - `ld`) | Trình liên kết động (Dynamic Linker - `ld-linux.so`) |
| :--- | :--- | :--- |
| **Thời điểm chạy** | Lúc biên dịch code (Compile Time) | Ngay trước khi chạy hàm `main` (Runtime) |
| **Cơ chế hoạt động** | Sao chép vật lý toàn bộ mã lệnh từ thư viện tĩnh (`.a`) và gắn thẳng vào bên trong tệp thực thi. | Bỏ qua việc sao chép. Nạp thư viện động (`.so`) lên RAM và phân giải địa chỉ ảo (Virtual Address). |
| **Đặc điểm tệp** | Kích thước lớn, tự cung tự cấp (Standalone). | Kích thước cực nhẹ, phụ thuộc vào môi trường OS. |
| **Tối ưu RAM** | Không. Các tiến trình chạy độc lập tốn tài nguyên riêng. | Có (Shared Memory). Nhiều tiến trình xài chung một vùng RAM chứa thư viện. |

---

## 2. Cặp Bài Trùng Phân Giải Địa Chỉ: PLT & GOT

Để thực thi việc gọi hàm từ thư viện động (như `printf`), tệp ELF sử dụng cơ chế **Lazy Binding (Liên kết trễ)** thông qua hai cấu trúc dữ liệu cốt lõi:

* **GOT (Global Offset Table - nằm tại Section `.got.plt`):** Bảng lưu trữ địa chỉ thực tế (trên RAM) của các hàm ngoại tuyến. Phân vùng này bắt buộc phải có quyền Ghi (`RW-`) để có thể cập nhật địa chỉ.
* **PLT (Procedure Linkage Table - nằm tại Section `.plt`):** Bảng chứa các đoạn mã ngắn (trampoline code) làm trung gian chuyển tiếp cuộc gọi hàm.

---

## 3. Bản Chất Mối Quan Hệ Giữa INTERP, DYNAMIC và PLT/GOT

Quá trình quản lý, khởi tạo và ghi đè dữ liệu lên PLT/GOT không tự diễn ra, mà là sự phối hợp chặt chẽ giữa hai Segment hệ thống:

### 3.1. `PT_INTERP` (Chủ thể quản lý thực tế)

* **Bản chất:** Chứa đường dẫn đến **Dynamic Linker** (Trình liên kết động - `ld-linux.so`).
* **Vai trò:** Đây chính là **"Thằng quản lý"** tối cao của PLT và GOT. Khi chương trình khởi chạy, Kernel trao quyền cho Dynamic Linker chạy trước để nó toàn quyền khởi tạo, kiểm soát và trực tiếp ghi đè địa chỉ hàm vào bảng GOT.

### 3.2. `PT_DYNAMIC` (Sổ tay hướng dẫn cho Thằng quản lý)

* **Bản chất:** Chứa siêu dữ liệu (Metadata) phục vụ cho quá trình liên kết tại Runtime.
* **Vai trò đối với PLT/GOT:** Thằng quản lý (Dynamic Linker) khi vừa cấu hình hệ thống sẽ đọc ngay Segment `PT_DYNAMIC` này để tìm các cờ (Tags) chỉ đường:
  * `DT_PLTGOT`: Cung cấp địa chỉ chính xác của bảng **GOT** trên RAM cho Dynamic Linker biết nơi để ghi đè dữ liệu.
  * `DT_JMPREL`: Chỉ định vị trí các mục từ tái định vị (Relocation Entries), giúp Dynamic Linker biết hàm nào (ví dụ: `printf`) ứng với dòng nào trong bảng GOT.

---

## 4. Vòng Đời Phối Hợp Khi Gọi Hàm Ngoại Tuyến (Lazy Binding Flow)

Khi chương trình gọi hàm `printf` lần đầu tiên, toàn bộ 5 thành phần phối hợp theo tiến trình sau:

1. **Chương trình nhảy vào PLT:** Mã nguồn gọi `printf` -> Luồng thực thi nhảy vào mục `printf@plt` trong bảng **PLT**.
2. **PLT tra cứu GOT:** `printf@plt` đọc địa chỉ tại mục tương ứng trong bảng **GOT**. 
3. **Kích hoạt Thằng quản lý:** Vì là lần đầu, mục GOT chưa có địa chỉ thật của hàm mà đang trỏ ngược lại một đoạn code trong PLT. Đoạn code này lập tức triệu hồi **Dynamic Linker** (được nạp từ `PT_INTERP`).
4. **Thực thi phân giải (Tái định vị):** Dynamic Linker đọc bảng **`PT_DYNAMIC`** để biết cấu hình, định vị file `libc.so` trên hệ điều hành, tìm ra địa chỉ thực tế của hàm `printf` trên RAM.
5. **Cập nhật và Đóng dấu:** Dynamic Linker **ghi đè địa chỉ thật** vừa tìm được vào đúng ô nhớ của `printf` trong bảng **GOT** (nhờ địa chỉ dẫn đường từ thẻ `DT_PLTGOT`).
6. **Từ lần gọi thứ hai:** Chương trình gọi `printf` -> Nhảy vào PLT -> PLT đọc GOT -> GOT lúc này đã có địa chỉ thật do Dynamic Linker ghi từ trước -> Nhảy thẳng đến hàm thực thi, bỏ qua bước gọi Dynamic Linker.

---

## 5. Sự Biến Đổi Cấu Trúc Khi Biên Dịch Tĩnh (Static Linking)

* **Chế độ Tĩnh thuần túy (`-static`):** Thằng Static Linker sao chép toàn bộ code vào file. Do chương trình tự trị, không cần nạp thư viện ngoài nên **`PT_INTERP` và `PT_DYNAMIC` bị xóa sổ hoàn toàn**. Bảng PLT và GOT cũng không còn lý do tồn tại.
* **Chế độ Static-PIE (`-static-pie`):** Tệp biên dịch tĩnh nhưng chạy địa chỉ ngẫu nhiên. `PT_INTERP` vẫn bị xóa (không cần thợ ngoài), nhưng **`PT_DYNAMIC` được giữ lại**. Tệp thực thi đóng vai trò là "Dynamic Linker của chính nó", tự đọc `PT_DYNAMIC` để tự cập nhật địa chỉ nội bộ (Self-Relocation) trước khi vào hàm `main`.