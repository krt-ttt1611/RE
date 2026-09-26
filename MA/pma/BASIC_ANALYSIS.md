# Phần 1: Các Kỹ Thuật Phân Tích Cơ Bản (Basic Analysis)

---

## Chương 1: Kỹ Thuật Phân Tích Tĩnh Cơ Bản (Basic Static Techniques)

Phân tích tĩnh cơ bản (Basic Static Analysis) là phương pháp kiểm tra tệp thực thi độc hại mà không cần chạy mã lệnh thực tế. Kỹ thuật này giúp xác định nhanh chóng:
- Mẫu tệp có thực sự độc hại hay không.
- Mức độ phức tạp và chức năng sơ bộ của mã độc.
- Các chỉ số xâm phạm (Indicators of Compromise - IoC) để phục vụ phòng thủ mạng.

---

### 1.1 Quét bằng Trình Diệt Virus và Nền tảng Tổng hợp (Antivirus Scanning)

Bước đi đầu tiên và đơn giản nhất trong phân tích tĩnh là đưa tệp nghi vấn qua các công cụ Antivirus (AV) hoặc dịch vụ trực tuyến tổng hợp như **VirusTotal**.
- **Cơ chế:** Các công cụ AV sử dụng cơ sở dữ liệu chữ ký (signature-based detection) gồm chuỗi byte, đoạn mã đặc trưng hoặc hàm băm để nhận diện mã độc đã biết. Ngoài ra, cơ chế phỏng đoán (heuristics) quét các tập lệnh bất thường để phát hiện biến thể mới.
- **Hạn chế:** Tác giả mã độc có thể dễ dàng vượt qua chữ ký bằng cách chỉnh sửa nhỏ mã nguồn, biên dịch lại hoặc sử dụng kỹ thuật làm rối (obfuscation/packing). Do đó, kết quả quét sạch từ AV không đồng nghĩa với việc tệp an toàn.

---

### 1.2 Nhận diện Mã độc bằng Hàm băm (Hashing)

Hàm băm mật mã đóng vai trò như một "vân tay số" (fingerprint) duy nhất cho từng tệp thực thi. Việc tính toán mã băm cho phép tra cứu mẫu trên các cơ sở dữ liệu mã độc toàn cầu mà không cần tải toàn bộ tệp lên mạng.

- **Các thuật toán phổ biến:**
  - **MD5 (Message Digest 5):** Tạo chuỗi băm 128-bit (32 ký tự hex). Phổ biến nhất trong báo cáo mã độc cổ điển dù đã có va chạm toán học.
  - **SHA-1 / SHA-256:** Cho độ dài băm 160-bit và 256-bit, an toàn và chống va chạm tốt hơn.
- **Công cụ tính toán:** Trên giao diện đồ họa có thể dùng **WinMD5**, hoặc trên dòng lệnh Windows sử dụng `certutil -hashfile <filename> MD5` hoặc `Get-FileHash` trong PowerShell.

![[PMA_Fig1-1_WinMD5.png]]
*Hình 1.1: Giao diện tính toán mã băm MD5 của tệp thực thi bằng công cụ WinMD5.*

> [!NOTE]
> Khi có mã băm (MD5/SHA-256), việc đầu tiên cần làm là tra cứu trên **VirusTotal** hoặc **MalwareBazaar** để xem phân tích của cộng đồng trước khi bắt tay dịch ngược chi tiết.

---

### 1.3 Trích xuất và Phân tích Chuỗi (Finding Strings)

Tìm kiếm chuỗi ký tự (Strings) là phương pháp trích xuất các chuỗi văn bản ASCII hoặc Unicode nhúng bên trong tệp nhị phân. Các chuỗi này thường tiết lộ:
- Tên tệp tin, đường dẫn thư mục mà mã độc tạo ra.
- Khóa Registry dùng để thiết lập persistence (duy trì khởi động).
- Địa chỉ IP, tên miền (Domain), URL của máy chủ điều khiển (C2 Server).
- Thông điệp tấn công hoặc thông báo lỗi nội bộ.

#### a. Chuỗi ASCII và Chuỗi Unicode
- **ASCII:** Sử dụng 1 byte cho mỗi ký tự, kết thúc bằng một byte NULL (`0x00`).
- **Unicode (UTF-16LE trên Windows):** Sử dụng 2 byte cho mỗi ký tự (ký tự ASCII thông thường sẽ có thêm byte `0x00` xen kẽ), kết thúc bằng hai byte NULL (`0x00 0x00`).

![[PMA_Fig1-2_ASCII_String.png]]
*Hình 1.2: Cấu trúc lưu trữ chuỗi ASCII "BAD" trong bộ nhớ (mỗi ký tự 1 byte kết thúc bởi NULL byte).*

![[PMA_Fig1-3_Unicode_String.png]]
*Hình 1.3: Cấu trúc lưu trữ chuỗi Unicode UTF-16LE của từ "BAD" (mỗi ký tự chiếm 2 byte).*

#### b. Sử dụng công cụ `strings`
Công cụ dòng lệnh `strings` (từ bộ công cụ Microsoft Sysinternals) quét toàn bộ tệp và in ra các chuỗi có độ dài từ 3 hoặc 4 ký tự liên tiếp trở lên:
```bash
strings -a -n 5 malware_sample.exe
```
*(Tham số `-a` quét toàn bộ tệp; `-n 5` chỉ trích xuất các chuỗi dài tối thiểu 5 ký tự).*

---

### 1.4 Mã độc bị Đóng gói và Làm rối (Packed & Obfuscated Malware)

Mã độc thường sử dụng các kỹ thuật bảo vệ nhằm chống phân tích tĩnh:
- **Làm rối (Obfuscation):** Tác giả cố tình che giấu logic thực thi bằng cách mã hóa chuỗi, biến đổi lệnh hoặc chèn các lệnh rác (junk instructions).
- **Đóng gói (Packing):** Một dạng nén mã độc. Phần mã gốc và dữ liệu được nén/mã hóa hoàn toàn, chỉ để lại một đoạn giải mã nhỏ gọi là **Unpacker Stub**.

#### a. Cơ chế hoạt động của Packer
Khi một chương trình đóng gói được thực thi:
1. Hệ điều hành nạp Unpacker Stub vào RAM như một tệp PE hợp lệ.
2. Unpacker Stub giải nén và giải mã phần payload thực sự vào bộ nhớ.
3. Stub chuyển quyền điều khiển (nhảy) tới Điểm nhập cảnh gốc (**Original Entry Point - OEP**) của chương trình thật.

![[Pasted image 20260907203702.png]]
*Hình 1.4: Cơ chế đóng gói tệp. Bên trái là tệp gốc chứa đầy đủ chuỗi và mã lệnh; bên phải là tệp bị đóng gói chỉ lộ Unpacker Stub.*

> [!WARNING]
> Nếu tệp thực thi chứa cực ít chuỗi hoặc các chuỗi chỉ liên quan đến cơ chế giải nén (`LoadLibrary`, `GetProcAddress`, tên packer), khả năng rất cao tệp đã bị đóng gói. Phân tích tĩnh bề mặt lúc này sẽ không đem lại hiệu quả.

#### b. Nhận diện Packer bằng PEiD và Detect It Easy (DiE)
- **PEiD:** Công cụ kinh điển sử dụng cơ sở dữ liệu chữ ký byte tại Entry Point để nhận diện packer (như UPX, ASPack, Petite...).

![[Pasted image 20260907203933.png]]
*Hình 1.5: Giao diện nhận diện packer UPX bằng công cụ PEiD.*

- **Công cụ thay thế hiện đại:** PEiD đã ngừng phát triển và gặp khó khăn với các tệp PE 64-bit hoặc packer mới. Khuyến nghị sử dụng **Detect It Easy (DiE)** để phân tích độ hỗn loạn (Entropy), nhận diện chữ ký trình biên dịch và packer chính xác hơn.

---

### 1.5 Cấu trúc Định dạng Tệp PE (Portable Executable Format)

Định dạng PE (Portable Executable) là cấu trúc chuẩn cho các tệp thực thi nhị phân (`.exe`), thư viện liên kết động (`.dll`) và tệp điều khiển (`.sys`) trên hệ điều hành Windows 32-bit và 64-bit.
Cấu trúc tổng quan của tệp PE gồm hai phần chính:
1. **PE Headers (Phần đầu):** Lưu trữ siêu dữ liệu (metadata) chỉ dẫn hệ điều hành cách nạp tệp vào bộ nhớ, bao gồm:
   - `IMAGE_DOS_HEADER`: Chứa chữ ký `MZ` (`0x5A4D`) và trường `e_lfanew` trỏ tới PE Header thực tế.
   - `MS-DOS Stub`: Đoạn mã nhỏ hiển thị thông báo *"This program cannot be run in DOS mode"*.
   - `IMAGE_NT_HEADERS`: Gồm chữ ký `PE\0\0`, `IMAGE_FILE_HEADER` (kiến trúc CPU, số lượng section, timestamp) và `IMAGE_OPTIONAL_HEADER` (địa chỉ AddressOfEntryPoint, ImageBase, Subsystem, Data Directories).
2. **Section Table & Sections (Các phân vùng dữ liệu):** Nơi chứa mã máy thực tế, dữ liệu toàn cục, tài nguyên và thông tin liên kết hàm.

---

### 1.6 Thư viện Liên kết và Hàm API (Linked Libraries and Functions)

Thông tin về các hàm Windows API mà chương trình nhập (Import) hoặc xuất (Export) cung cấp bức tranh rõ ràng nhất về chức năng nội tại của nó.

#### a. Các phương thức liên kết
1. **Liên kết tĩnh (Static Linking):** Mã của thư viện được biên dịch trực tiếp vào tệp thực thi. Hiếm gặp trên Windows đối với mã độc vì làm kích thước tệp phình to.
2. **Liên kết lúc nạp (Dynamic Linking / Load-time Linking):** Các DLL cần thiết được khai báo trong PE Header (bảng Import Address Table - IAT). Khi chương trình khởi chạy, OS Loader tự động nạp các DLL này vào không gian địa chỉ tiến trình.
3. **Liên kết lúc chạy (Runtime Linking):** Chương trình không khai báo DLL trước mà chỉ nạp khi cần thông qua hai API cốt lõi:
   - `LoadLibraryA/W`: Nạp một DLL vào bộ nhớ lúc đang chạy.
   - `GetProcAddress`: Lấy con trỏ địa chỉ của một hàm xuất từ DLL vừa nạp.
   - `FreeLibrary`: Giải phóng DLL khi không còn sử dụng.
   *(Mã độc thường dùng kỹ thuật này để che giấu danh sách các API nhạy cảm khỏi bảng IAT).*

#### b. Phân tích hàm nhập (Imports) với Dependencies
Công cụ **Dependency Walker** (`depends.exe`) phân tích danh sách DLL và hàm được liên kết lúc nạp. Do bản gốc chạy chậm trên Windows 10/11, nên sử dụng bản viết lại hiện đại là **Dependencies** (mã nguồn mở trên GitHub).

![[Pasted image 20260907212331.png]]
*Hình 1.6: Phân tích các DLL phụ thuộc của tiến trình hệ thống bằng Dependency Walker.*

#### c. Danh mục các DLL thông dụng trên Windows
Mỗi DLL hệ thống đảm nhiệm một vai trò chức năng riêng biệt. Quan sát danh sách DLL nạp vào cho phép suy đoán hành vi của phần mềm:

![[Pasted image 20260907212648.png]]
*Hình 1.7: Bảng 1.1 trong sách PMA liệt kê các DLL Windows phổ biến và chức năng tương ứng.*

| Tên DLL | Mục đích sử dụng phổ biến | Dấu hiệu phân tích mã độc |
| :--- | :--- | :--- |
| `Kernel32.dll` | Quản lý bộ nhớ, tệp tin, phần cứng, tiến trình và luồng | Hầu như mọi chương trình đều dùng. Quan sát các hàm mở process, ghi file, nạp thư viện. |
| `Advapi32.dll` | Quản trị bảo mật, tài khoản, Services và Registry | Thường gặp khi mã độc thao tác Service hoặc can thiệp khóa Registry tự khởi động (`Run`). |
| `User32.dll` | Thành phần giao diện đồ họa (GUI), chuột, bàn phím | Chú ý các hàm theo dõi bàn phím (`SetWindowsHookEx`, `GetAsyncKeyState`) trong Keylogger. |
| `Gdi32.dll` | Giao diện đồ họa thiết bị (Graphics Device Interface) | Hiển thị hoặc thao tác đồ họa, vẽ màn hình. |
| `Ws2_32.dll` / `Wsock32.dll` | Giao diện mạng Windows Sockets | Kết nối mạng, truyền nhận dữ liệu, thiết lập kết nối ra C2. |
| `Wininet.dll` | Giao tiếp mạng cấp cao (HTTP, FTP, HTTPS) | Tải tệp xuống qua HTTP (`InternetOpen`, `InternetReadFile`), tạo kết nối web. |

#### d. Các hàm xuất (Exported Functions)
- Các tệp DLL thường xuất hàm để EXE khác gọi tới. Tệp `.exe` hiếm khi xuất hàm, trừ khi được thiết kế dạng plugin hoặc để hỗ trợ IPC/Callback.
- Nếu một tệp `.exe` có các hàm xuất, đó là thông tin đặc biệt giá trị để xác định danh tính và vai trò của chương trình.

---

### 1.7 Thực hành Phân tích Tĩnh Mẫu Thực tế

#### a. Mẫu PotentialKeylogger.exe (Tệp thực thi không bị đóng gói)

![[Pasted image 20260907213251.png]]
*Hình 1.8: Danh sách hàm import của mẫu PotentialKeylogger.exe trích xuất bằng Dependency Walker.*

Khi phân tích danh sách Import của mẫu này:
1. **Từ `Kernel32.dll`:** Có các hàm mở và điều khiển tiến trình (`OpenProcess`, `GetCurrentProcess`), thao tác tệp (`CreateFile`, `ReadFile`, `WriteFile`) và tìm kiếm tệp (`FindFirstFile`, `FindNextFile`).
2. **Từ `User32.dll`:**
   - `SetWindowsHookExA`: Hàm trọng yếu được dùng để cài đặt hook chặn bắt sự kiện hệ thống. Đây là dấu hiệu đặc trưng hàng đầu của phần mềm gián điệp / Keylogger để ghi nhận thao tác gõ phím.
   - `RegisterHotKey`: Đăng ký tổ hợp phím nóng để kích hoạt ứng dụng ngầm xuất hiện khi người dùng nhấn phím.
3. **Từ `Advapi32.dll`:** Chứa các hàm truy vấn và ghi dữ liệu Registry. Kết hợp kiểm tra chuỗi, phát hiện chuỗi:
   ```text
   Software\Microsoft\Windows\CurrentVersion\Run
   ```
   Đây là khóa Registry kinh điển để chương trình tự động kích hoạt cùng hệ điều hành.
4. **Hàm xuất (Exports):** Mẫu `.exe` này xuất hai hàm bất thường: `LowLevelKeyboardProc` và `LowLevelMouseProc`.

![[Pasted image 20260907223323.png]]
*Hình 1.9: Chi tiết hàm callback LowLevelKeyboardProc dùng làm tham số cho SetWindowsHookEx.*

Theo tài liệu Microsoft MSDN, `LowLevelKeyboardProc` là hàm callback được truyền vào `SetWindowsHookEx` để đón bắt các sự kiện bàn phím thô ở cấp độ thấp (`WH_KEYBOARD_LL`).
> [!IMPORTANT]
> **Kết luận phân tích tĩnh:** `PotentialKeylogger.exe` là một phần mềm độc hại thuộc loại Keylogger cục bộ, tự duy trì qua khóa Registry Run, giám sát phím bằng hook cấp thấp và hỗ trợ kích hoạt giao diện qua phím nóng.

#### b. Mẫu PackedProgram.exe (Tệp thực thi bị đóng gói)

![[Pasted image 20260907224220.png]]
*Hình 1.10: Danh sách hàm import cực kỳ nghèo nàn của PackedProgram.exe.*

Ngược lại với mẫu trên, `PackedProgram.exe` chỉ import vỏn vẹn một vài hàm từ `Kernel32.dll` như `LoadLibraryA` và `GetProcAddress`. Một ứng dụng Windows đầy đủ chức năng không thể chạy được nếu chỉ dựa vào vài hàm này.
- **Đánh giá:** Tệp đã bị đóng gói hoặc làm rối mã lệnh.
- **Hướng xử lý:** Không thể tiếp tục mổ xẻ logic bằng phân tích tĩnh thông thường; cần chuyển sang phân tích động hoặc giải nén (unpacking).

---

### 1.8 Khảo sát PE Header và các Section quan trọng

#### a. Các Section phổ biến trong tệp PE
Sau PE Header là danh sách các Section chứa dữ liệu thực tế:
- `.text`: Chứa toàn bộ mã máy (instructions) mà CPU sẽ thực thi. Đây thường là section duy nhất có quyền thực thi (`IMAGE_SCN_MEM_EXECUTE`).
- `.rdata`: Chứa dữ liệu chỉ đọc (read-only data) như bảng Import/Export Directory, chuỗi hằng số.
- `.data`: Chứa các biến và dữ liệu toàn cục (global variables) có thể đọc và ghi.
- `.rsrc`: Chứa toàn bộ tài nguyên của ứng dụng (biểu tượng icon, ảnh, menu, hộp thoại, tệp âm thanh và String Table).

![[Pasted image 20260907230444.png]]
*Hình 1.11: Danh sách các tên section phổ biến của tệp PE trên Windows.*

#### b. Khảo sát cấu trúc PE với PEview, PE-bear, CFF Explorer
Xem xét trực tiếp các cấu trúc nội bộ trong PE Header cung cấp các dữ liệu quan trọng:
- `IMAGE_FILE_HEADER.TimeDateStamp`: Thời điểm tệp được biên dịch. Nếu ngày biên dịch nằm trong tương lai hoặc thuộc thập kỷ trước trong khi phần mềm mới xuất hiện, timestamp có thể đã bị làm giả (timestomping).
- `IMAGE_FILE_HEADER.Characteristics`: Cờ xác định tệp là EXE (`IMAGE_FILE_EXECUTABLE_IMAGE`) hay DLL (`IMAGE_FILE_DLL`).

![[PMA_Fig1-7_PEview_FileHeader.png]]
*Hình 1.12: Khảo sát IMAGE_FILE_HEADER của tệp bằng công cụ PEview.*

- `IMAGE_SECTION_HEADER`: So sánh hai thông số then chốt:
  - `Virtual Size`: Kích thước thực tế mà section sẽ chiếm khi nạp lên bộ nhớ RAM.
  - `Size of Raw Data`: Kích thước của section được lưu trữ trên tệp vật lý ở ổ cứng.

![[PMA_Fig1-8_PEview_SectionHeader.png]]
*Hình 1.13: Khảo sát IMAGE_SECTION_HEADER phân vùng .text trong PEview.*

> [!TIP]
> **Quy tắc vàng phát hiện Packer qua Section:**
> Nếu một section có `Virtual Size` lớn hơn rất nhiều so với `Size of Raw Data` (ví dụ section chỉ chiếm 1 KB trên đĩa nhưng khi nạp đòi tới 100 KB trên RAM), điều đó báo hiệu section này sẽ được Unpacker Stub dùng để bung mã độc đã nén vào bộ nhớ.

#### c. Trích xuất tài nguyên bằng Resource Hacker
Section `.rsrc` có thể được kiểm tra chi tiết bằng **Resource Hacker**. Mã độc thường cất giấu các thành phần nhạy cảm như tệp nén, driver độc hại (`.sys`), DLL phụ hoặc mã khai thác bên trong section tài nguyên này.

![[PMA_Fig1-9_ResourceHacker.png]]
*Hình 1.14: Giao diện Resource Hacker mở tệp calc.exe, hiển thị các tài nguyên nhúng bên trong.*

---

## Chương 2: Thiết lập Môi trường Máy ảo Phân tích (Malware Analysis in Virtual Machines)

Phân tích mã độc đòi hỏi môi trường thực thi hoàn toàn biệt lập để ngăn chặn nguy cơ lây nhiễm sang hạ tầng mạng doanh nghiệp hoặc máy tính cá nhân. Công nghệ ảo hóa (VMware Workstation, VirtualBox) là tiêu chuẩn bắt buộc cho công việc này.

---

### 2.1 Kiến trúc máy ảo trong phân tích mã độc
- **Máy chủ vật lý (Host Machine):** Máy tính thực của nhà nghiên cứu. Không bao giờ chạy mẫu độc hại trực tiếp tại đây.
- **Máy khách ảo hóa (Guest VM):** Hệ điều hành ảo chạy trên phần mềm ảo hóa. Đây là nơi chứa các công cụ kiểm thử và mẫu độc hại.
- **Hypervisor:** Lớp trung gian quản lý và điều phối phần cứng giữa Host và Guest.

---

### 2.2 Cấu hình mạng an toàn (Host-Only Networking)

#### a. Cấu hình mạng tùy biến (Custom Virtual Networking)

![[PMA_Fig2-4_VMware_CustomNet.png]]
*Hình 2.2: Thiết lập mạng ảo tùy biến (Custom Networking VMnet) kết nối nhiều máy ảo phân tích trong cùng một phân vùng cô lập.*


Việc cấu hình card mạng của máy ảo quyết định ranh giới an toàn khi kích hoạt mã độc:
1. **Bridged:** Máy ảo nhận một IP trực tiếp trong mạng LAN thật. Tuyệt đối không sử dụng chế độ này khi chạy mã độc nguy hiểm vì mã độc dạng worm có thể quét và lây lan sang toàn mạng nội bộ.
2. **NAT:** Chia sẻ kết nối Internet của máy Host. Chỉ bật khi chủ động cần phân tích hành vi kết nối Internet ra ngoài và đã có các lớp giám sát.
3. **Host-Only Networking (Khuyến nghị chuẩn):** Tạo ra một mạng nội bộ hoàn toàn cô lập giữa máy Host và các máy Guest, không có đường ra Internet bên ngoài.

![[PMA_Fig2-3_VMware_HostOnly.png]]
*Hình 2.1: Kiến trúc mạng Host-Only trong VMware giúp cô lập máy ảo phân tích khỏi mạng Internet vật lý.*

---

### 2.3 Chiến lược quản lý Snapshot

Snapshot là tính năng lưu lại trạng thái toàn vẹn (bộ nhớ RAM, cấu hình phần cứng và dữ liệu đĩa) của máy ảo tại một mốc thời gian cụ thể.
- **Baseline Snapshot (Clean State):** Chụp ngay sau khi cài đặt đầy đủ hệ điều hành và toàn bộ công cụ phân tích (IDA Pro, x64dbg, Wireshark, Process Hacker...).
- **Quy trình chuẩn khi phân tích:**
  1. Khôi phục máy ảo về Clean Snapshot.
  2. Nạp mẫu độc hại vào máy ảo.
  3. Kích hoạt và theo dõi hành vi của mẫu.
  4. Thu thập toàn bộ log và bằng chứng phân tích.
  5. Revert (hoàn nguyên) máy ảo về lại Clean Snapshot để xóa sổ hoàn toàn mọi dấu vết lây nhiễm trước khi phân tích mẫu tiếp theo.

![[PMA_Fig2-5_Snapshot_Timeline.png]]
*Hình 2.3: Dòng thời gian sử dụng tính năng Snapshot để đưa hệ điều hành trở về trạng thái sạch sau khi thử nghiệm mã độc.*

---


![[PMA_Fig2-6_Snapshot_Manager.png]]
*Hình 2.4: Giao diện quản lý cây trạng thái máy ảo VMware Snapshot Manager, cho phép rẽ nhánh và hoàn nguyên về trạng thái sạch.*

### 2.4 Rủi ro và biện pháp phòng ngừa khi sử dụng máy ảo
- **Nguy cơ thoát máy ảo (VM Escape):** Mã độc khai thác lỗ hổng trong hypervisor để thoát khỏi môi trường ảo và tấn công trực tiếp máy Host. Luôn cập nhật phần mềm ảo hóa lên phiên bản an toàn.
- **Tắt chia sẻ thư mục (Shared Folders) và Clipboard:** Vô hiệu hóa tính năng copy/paste kéo thả tự động giữa Host và Guest khi phân tích các mẫu ransomware hoặc mã độc có khả năng quét ổ đĩa mạng.

---

## Chương 3: Kỹ Thuật Phân Tích Động Cơ Bản (Basic Dynamic Analysis)

Phân tích động cơ bản (Basic Dynamic Analysis) là quá trình kích hoạt trực tiếp mẫu mã độc trong môi trường an toàn và ghi nhận toàn bộ tác động của nó lên hệ điều hành: tệp tin tạo mới, khóa Registry biến đổi, tiến trình con được sinh ra và kết nối mạng phát sinh.

---

### 3.1 Môi trường Tự động hóa Sandbox

#### a. Nguyên lý hoạt động của Malware Sandbox
Sandbox tự động là môi trường ảo hóa tích hợp sẵn các công cụ giám sát. Khi người dùng tải tệp lên, Sandbox sẽ tự động thực thi tệp trong vài phút, ghi lại toàn bộ hoạt động và xuất ra báo cáo tóm tắt chi tiết.

![[Pasted image 20260912144527.png]]
*Hình 3.1: Mục lục báo cáo phân tích tự động được xuất ra từ hệ thống Sandbox GFI.*

#### b. Hạn chế cốt tử của Sandbox
1. **Thiếu tham số dòng lệnh:** Sandbox chỉ chạy tệp bằng cách nhấn đúp; nếu mã độc yêu cầu tham số đặc thù (VD: `malware.exe -install -key 1234`), nó sẽ lập tức thoát.
2. **Kỹ thuật chống máy ảo (Anti-VM / Evasion):** Mã độc phát hiện môi trường Sandbox (kiểm tra tên driver ảo hóa, độ phân giải màn hình, chuyển động chuột) và từ chối chạy mã độc hại.
3. **Cơ chế chờ đợi (Sleep Timers):** Mã độc chủ động ngủ 20-30 phút trước khi bung payload nhằm vượt qua thời gian chờ giới hạn của Sandbox tự động.
4. **Không tương tác C2:** Nếu máy chủ C2 bị sập hoặc bị chặn, Sandbox không thể ghi nhận các hành vi ở giai đoạn sau.

---

### 3.2 Kỹ thuật Thực thi Mã độc

#### a. Khởi chạy tệp EXE
Tệp thực thi `.exe` có thể chạy trực tiếp từ dấu nhắc lệnh `cmd.exe` hoặc PowerShell để quan sát thông báo lỗi hoặc tham số trợ giúp (`-h`, `--help`).

#### b. Thực thi tệp DLL độc hại với `rundll32.exe`
Windows không cung cấp cách nhấn đúp để chạy tệp `.dll`. Ta sử dụng tiện ích tích hợp sẵn của Windows là `rundll32.exe`:
```bash
rundll32.exe DLLName, ExportName [Arguments]
```

![[Pasted image 20260912145533.png]]
*Hình 3.2: Cú pháp thực thi hàm export của DLL bằng tiện ích rundll32.exe.*

- **Thực thi theo tên hàm:** Nếu tệp `rip.dll` có hàm xuất là `Install`:
  ```bash
  rundll32.exe rip.dll, Install
  ```
- **Thực thi theo số thứ tự (Ordinal):** Nếu hàm xuất không có tên mà chỉ có số thứ tự (ví dụ Ordinal số 5):
  ```bash
  rundll32.exe xyzzy.dll, #5
  ```

#### c. Nạp DLL thông qua chỉnh sửa cờ Characteristics hoặc cài đặt Service
- **Chạy mã trong `DllMain`:** Mã độc dạng DLL thường đặt phần lớn payload trong hàm khởi tạo `DllMain`. Có thể ép Windows chạy DLL này bằng cách dùng trình sửa PE Header để xóa cờ `IMAGE_FILE_DLL` (`0x2000`) khỏi trường `IMAGE_FILE_HEADER.Characteristics`, sau đó đổi đuôi tệp thành `.exe`.
- **Cài đặt dưới dạng Windows Service:** Nhiều DLL mã độc yêu cầu được chạy dưới quyền một dịch vụ:
  ```bash
  rundll32.exe ipr32x.dll, InstallService MyMalwareService
  net start MyMalwareService
  ```

---

### 3.3 Giám sát Hệ thống với Process Monitor (ProcMon)

Process Monitor (ProcMon) thuộc bộ công cụ Sysinternals là công cụ giám sát thời gian thực toàn diện nhất đối với hoạt động của hệ điều hành Windows.

![[PMA_Fig3-2_Procmon_Capture.png]]
*Hình 3.3: Giao diện chụp sự kiện hệ thống của Process Monitor khi mẫu mã độc mm32.exe hoạt động.*

#### a. Bốn nhóm sự kiện chính trong ProcMon
1. **Registry:** Tạo khóa, đọc/ghi giá trị (`RegCreateKey`, `RegSetValue`, `RegQueryValue`).
2. **File System:** Tạo, đọc, ghi và xóa tệp tin trên ổ đĩa (`CreateFile`, `WriteFile`, `SetDispositionInformationFile`).
3. **Process & Thread:** Tạo tiến trình con, nạp thư viện DLL, kết thúc luồng.
4. **Network:** Ghi nhận các kết nối TCP/UDP cơ bản (chỉ ghi nhận sự kiện mở socket/port, không ghi nhận nội dung gói tin).

#### b. Thiết lập bộ lọc (Filter) tối ưu
Hệ điều hành Windows sinh ra hàng trăm nghìn sự kiện mỗi phút. Nếu không lọc, ProcMon sẽ tiêu tốn toàn bộ RAM và làm sập máy ảo.
- Nhấn tổ hợp phím `Ctrl + L` để mở hộp thoại cấu hình Filter.
- Đặt điều kiện lọc trọng tâm:
  - `Process Name is <ten_malware.exe> then Include`
  - Hoặc `Operation is SetDispositionInformationFile then Include` (bắt hành vi tự xóa tệp).

![[PMA_Fig3-3_Procmon_Filter.png]]
*Hình 3.4: Thiết lập bộ lọc sự kiện theo Process Name trong Process Monitor.*

#### c. Chuyển đổi nhóm sự kiện và kiểm soát dung lượng bộ nhớ
Thanh công cụ của ProcMon cung cấp năm biểu tượng nút bấm để bật/tắt nhanh các nhóm sự kiện tương ứng:

![[PMA_Fig3-4_Procmon_FilterButtons.png]]
*Hình 3.5: Các nút bật/tắt nhanh bộ lọc sự kiện trên thanh công cụ ProcMon (Registry, File System, Network, Process, Profiling).*

> [!TIP]
> Trong menu `Filter`, hãy bật tùy chọn **Drop Filtered Events**. Tính năng này chỉ lưu trữ các sự kiện khớp với bộ lọc vào RAM, loại bỏ toàn bộ dữ liệu thừa nhằm tránh tràn bộ nhớ khi chạy lâu.

---

### 3.4 Khảo sát Tiến trình Chuyên sâu với Process Explorer

Process Explorer (PE) cung cấp cây phân cấp tiến trình (Process Tree) trực quan, cho thấy chính xác tiến trình cha nào đã sinh ra tiến trình con độc hại.

![[Pasted image 20260912153226.png]]
*Hình 3.6: Cửa sổ chính của Process Explorer hiển thị cây tiến trình và chỉ số hệ thống.*

#### a. Tính năng xác minh chữ ký số (Verify Image)
Trong cửa sổ thuộc tính của tiến trình (Process Properties -> tab Image), nút **Verify** cho phép xác minh chữ ký số của tệp nhị phân trên đĩa với Microsoft.

![[Pasted image 20260912153936.png]]
*Hình 3.7: Kiểm tra thuộc tính tiến trình svchost.exe nghi vấn trong Process Explorer.*

> [!WARNING]
> **Điểm mù của nút Verify:** Nút Verify chỉ xác thực tệp nhị phân lưu trên đĩa cứng. Nếu mã độc sử dụng kỹ thuật **Process Hollowing** (rút ruột tiến trình) hoặc **DLL Injection** (tiêm mã độc vào tiến trình hệ thống hợp lệ `svchost.exe`), nút Verify vẫn báo chữ ký hợp lệ của Microsoft dù mã đang chạy trên RAM thực chất là mã độc!

#### b. So sánh chuỗi bộ nhớ với chuỗi tệp trên đĩa (Disk vs. Memory Strings)
Tab **Strings** trong Process Explorer cho phép chuyển đổi giữa hai chế độ:
- **Image:** Đọc các chuỗi từ tệp tĩnh trên đĩa cứng.
- **Memory:** Đọc các chuỗi đang nằm trực tiếp trong không gian bộ nhớ ảo của tiến trình đang chạy.

![[Pasted image 20260912154322.png]]
*Hình 3.8: So sánh danh sách chuỗi trên đĩa (trái) và chuỗi trong bộ nhớ RAM (phải) để phát hiện mã độc nạp ngầm.*

Nếu danh sách chuỗi trong Memory xuất hiện hàng loạt chuỗi mới (như URL, hàm API độc hại, khóa registry) hoàn toàn không có trong Image trên đĩa, tiến trình đó chắc chắn đã bị tiêm mã độc hoặc vừa tự giải nén payload vào RAM.

#### c. Truy vết Handle và nạp thư viện ngầm
Process Explorer cho phép tìm kiếm bất kỳ Handle (tệp, mutex, event) hoặc DLL nào bằng tổ hợp phím `Ctrl + F`:
- Rất hữu dụng khi cần tìm tiến trình nào đang chiếm giữ một tệp bị khóa trên ổ đĩa.
- Giúp phát hiện các DLL lạ được nạp ngầm vào tiến trình hệ thống.

#### d. Phân tích tài liệu độc hại (PDF, Office Documents)
Khi mở một tệp tài liệu nghi vấn (Word, PDF), hãy quan sát cây tiến trình trong Process Explorer. Nếu việc mở tệp Word làm sinh ra một tiến trình lạ như `cmd.exe`, `powershell.exe` hoặc `wscript.exe`, tài liệu đó chắc chắn chứa mã khai thác (exploit) hoặc mã macro độc hại.

---

### 3.5 Theo dõi Thay đổi Hệ thống với Regshot

Regshot là công cụ mã nguồn mở so sánh ảnh chụp cấu trúc Windows Registry và hệ thống tệp trước và sau khi thực thi mã độc.

![[Pasted image 20260912155814.png]]
*Hình 3.9: Báo cáo kết quả so sánh Registry do Regshot tạo ra, phát hiện khóa tự khởi động vừa được thêm mới.*

- **Quy trình sử dụng:**
  1. Mở Regshot, bấm **1st shot** để chụp trạng thái hệ thống ban đầu.
  2. Kích hoạt mẫu mã độc và chờ vài phút để mẫu thực hiện hành vi.
  3. Bấm **2nd shot** để chụp trạng thái sau khi nhiễm.
  4. Bấm **Compare** để xuất báo cáo so sánh chi tiết dạng văn bản hoặc HTML.

---

### 3.6 Giả lập Dịch vụ Mạng Cục bộ

Mã độc thường cố gắng kết nối ra ngoài để báo cáo tín hiệu (beacon) hoặc nhận lệnh từ máy chủ C2. Khi phân tích trong mạng cô lập (Host-only), ta phải sử dụng các công cụ giả lập để đáp ứng các yêu cầu này.

#### a. Giả lập phản hồi DNS bằng ApateDNS
Mã độc thường gửi truy vấn phân giải tên miền trước khi gửi dữ liệu. **ApateDNS** lắng nghe trên cổng UDP 53 của máy phân tích và tự động phản hồi mọi truy vấn DNS bằng một địa chỉ IP cục bộ được cấu hình trước.

![[Pasted image 20260912161941.png]]
*Hình 3.10: ApateDNS giả lập phân giải tên miền evil.malwar3.com về IP máy cục bộ.*

#### b. Lắng nghe và chặn bắt kết nối ngược bằng Netcat
Sau khi ApateDNS điều hướng lưu lượng về máy phân tích, ta dùng **Netcat** (`nc`) để lắng nghe kết nối đến trên cổng tương ứng:
```bash
nc -l -p 80
```
*(Tham số `-l` bật chế độ lắng nghe; `-p 80` chỉ định cổng 80).*

![[Pasted image 20260912161954.png]]
*Hình 3.11: Bắt và tương tác với phiên kết nối Reverse Shell của mã độc RShell bằng Netcat.*

---

### 3.7 Bắt gói tin và Phân tích Luồng Mạng với Wireshark

Wireshark là công cụ giám sát và phân tích lưu lượng gói tin mạng chuyên sâu.

![[PMA_Fig3-10_Wireshark_DNS_HTTP.png]]
*Hình 3.12: Bắt và phân tích chi tiết cấu trúc gói tin HTTP GET của mã độc trong Wireshark.*

#### a. Bắt và phân tích các giao thức mạng
- **DNS Request:** Xem mã độc cố gắng tìm kiếm tên miền nào.
- **HTTP/HTTPS Traffic:** Kiểm tra `User-Agent`, đường dẫn URL, tham số GET/POST và dữ liệu mà mã độc gửi lên server.

#### b. Tái tạo luồng dữ liệu TCP với Follow TCP Stream
Khi mã độc trao đổi dữ liệu qua giao thức tùy biến, việc đọc từng gói tin đơn lẻ rất rời rạc. Nhấp chuột phải vào một gói tin TCP và chọn **Follow -> TCP Stream** để Wireshark tự động ghép nối toàn bộ cuộc hội thoại truyền nhận hai chiều giữa client và server.

![[PMA_Fig3-11_Wireshark_Follow_TCP_Stream.png]]
*Hình 3.13: Cửa sổ Follow TCP Stream trong Wireshark tái tạo nguyên vẹn nội dung phiên truyền dữ liệu TCP.*

---

### 3.8 Mô phỏng Toàn diện Dịch vụ Mạng với INetSim

Trong khi ApateDNS và Netcat chỉ hỗ trợ đơn giản, **INetSim** là một bộ công cụ mô phỏng dịch vụ mạng hoàn chỉnh chạy trên máy ảo Linux.

![[Pasted image 20260912163358.png]]
*Hình 3.14: Bảng danh sách các dịch vụ mạng mà INetSim có khả năng mô phỏng mặc định.*

- **Ưu điểm vượt trội của INetSim:**
  - Tự động mô phỏng cùng lúc: HTTP, HTTPS, FTP, IRC, DNS, SMTP, POP3, TFTP.
  - **Phản hồi dữ liệu thông minh:** Nếu mã độc gửi yêu cầu tải một tệp `.exe` hoặc ảnh `.jpg`, INetSim sẽ tạo và trả về một tệp thực thi hoặc hình ảnh giả lập hoàn chỉnh, giúp mã độc tin rằng nó đang ở trên Internet thật để tiếp tục thực thi các giai đoạn sau.

---

### 3.9 Thực hành Phối hợp Công cụ Phân tích Động

Để đạt hiệu quả tối đa, các công cụ phân tích động luôn được phối hợp theo một quy trình tuần tự khép kín:

![[PMA_Fig3-12_Virtual_Network_Setup.png]]
*Hình 3.15: Mô hình thiết lập mạng phân tích động kết hợp giữa máy ảo Windows (chạy mẫu mã độc) và máy ảo Linux INetSim (giả lập toàn bộ dịch vụ mạng).*


![[PMA_Fig3-16_Wireshark_CustomProto.png]]
*Hình 3.16: Bắt và phân tích cấu trúc giao thức mạng tùy biến của mã độc qua cổng 443 bằng Wireshark.*

#### Quy trình phân tích động 7 bước chuẩn:
1. **Chuẩn bị:** Chụp Snapshot sạch cho toàn bộ các máy ảo kiểm thử.
2. **Kích hoạt mạng giả:** Khởi động máy ảo INetSim hoặc chạy ApateDNS + Netcat trên máy phân tích.
3. **Chụp mốc ban đầu:** Chạy Regshot và lấy ảnh chụp đầu tiên (**1st shot**).
4. **Bật giám sát thời gian thực:** Khởi động Wireshark để bắt gói tin mạng; bật Process Monitor (đã cấu hình bộ lọc) và mở Process Explorer.
5. **Kích hoạt mẫu:** Chạy tệp mã độc (bằng cmd hoặc `rundll32.exe`).
6. **Thu thập và phân tích:**
   - Quan sát cây tiến trình và so sánh chuỗi trong Process Explorer.
   - Dừng bắt sự kiện trong ProcMon (`Ctrl + E`) và lọc ra các khóa Registry, tệp tin bị sửa đổi.
   - Bấm **2nd shot** trong Regshot và đối chiếu thay đổi.
   - Kiểm tra log DNS và các luồng TCP Stream trong Wireshark.
7. **Hoàn nguyên:** Lưu trữ báo cáo, sau đó Revert máy ảo về Snapshot ban đầu.
