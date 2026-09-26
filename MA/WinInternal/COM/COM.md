==COM (Component Object Module)== là chuẩn giao tiếp nhị phân (ABI) cho phép các module phần mềm giao tiếp với nhau bất kể chúng được viết bằng ngôn ngữ nào hay chạy ở các tiến trình khác nhau.
Trong CPP, 2 file nhị phân (exe và dll) gặp rào cản lớn khi muốn dùng chung class của nhau do sự thiếu đồng nhất về ABI:
- Mỗi trình biên dịch có cách mã hóa tên hàm khác nhau.
- Cách bố trí ô nhớ của class (mem layout), bảng ảo (vtable), và cơ chế cấp phát, giải phóng bộ nhớ giữa các compiler cũng khác nhau.
COM giải quyết bằng cách đưa ra 1 quy ước duy nhất ở tầng bộ nhớ nhị phân: Moị giao tiếp đều phải thông qua interface (là bảng con trỏ vtable) và bộ đếm tham chiếu (Reference Counting).
![[Pasted image 20260921150617.png]]
```
mov ecx, [pObject]         ; 1. Lấy địa chỉ đối tượng (con trỏ this)
mov eax, [ecx]             ; 2. Lấy con trỏ trỏ tới bảng Vtable (nằm ở byte đầu tiên của đối tượng)
call dword ptr [eax + 0Ch] ; 3. Bấm vào vị trí thứ 4 (Offset 0x0C = 12 bytes = 3 * 4) để nhảy vào code của SetSite


[Con trỏ đối tượng trên Heap]
      │
      ▼
┌──────────────┐
│ vptr         │ ───► [Bảng Vtable trong .rdata]
├──────────────┤      ┌─────────┬────────────────────────┐
│ Member Vars  │      │ +0x00   │ Con trỏ tới QueryInterface │
└──────────────┘      │ +0x04   │ Con trỏ tới AddRef     │
                      │ +0x08   │ Con trỏ tới Release    │
                      │ +0x0C   │ Con trỏ tới SetSite    │ ──► [Hàm thực thi]
                      └─────────┴────────────────────────┘
```
![[Pasted image 20260921150951.png]]

**Cấu trúc của COM Object**
COM Object trên heap thực chất là 1 cấu trúc dữ liệu gồm 2 phần: ==Con trỏ vtable== `vptr` và ==các biến thành viên==.
```
[Vùng nhớ RAM của COM Object trên Heap (this)]
+--------------------+
| 0x00: vptr         | ──────► [Bảng Vtable nằm ở section .rdata]
+--------------------+         +-------------------------------------+
| 0x04: m_refCount   |         | Slot 0: &MyClass::QueryInterface    |
+--------------------+         | Slot 1: &MyClass::AddRef            |
| 0x08: m_data1      |         | Slot 2: &MyClass::Release           |
+--------------------+         | Slot 3: &MyClass::MethodA           |
| ...                |         | Slot 4: &MyClass::MethodB           |
+--------------------+         +-------------------------------------+
```
- ==Con trỏ this==: luôn trỏ thẳng vào byte đầu tiên của đối tượng (là nơi chứa `vptr`).
- ==Vtable==: Một mảng các con trỏ 4-byte (x86) hoặc 8-byte(x64) trỏ tới các hàm thực thi, thường nằm cố định trong các section read-only (`.rdata`).
- ==Cú pháp gọi hàm==: Client không bao giờ gọi trực tiếp tên hàm, mà gọi qua chỉ số `vtable`:
```
mov ecx, [pObject]        ; truyền con trỏ this vào ECX (__thiscall)
mov eax, [ecx]            ; EAX = lấy con trỏ vtable
call dword ptr [eax + 0Ch]; gọi hàm ở Slot 3 (Offset 0x0C)
```
***Interface:*** là 1 class ảo (cứ tạm hiểu là vậy, sau học oop thì học). 1 Object có thể chứa nhiều interface. Mỗi interface thõa mãn 2 quy tắc:
- Không có biến thành viên nào ngoài con trỏ `vptr`.
- Tất cả các hàm đều là thuần ảo (sau học thì biết).
Cái quan trong nhất: Khi 1 Class có nhiều interface, cấu trúc của nó sẽ có dạng:
```
[Vùng nhớ Object trên Heap (địa chỉ 'this')]
+0x00: vptr 1 ────► Trỏ tới Vtable của IObjectWithSite trong .rdata
+0x04: vptr 2 ────► Trỏ tới Vtable của IDispatch (EventSink) trong .rdata
+0x08: m_cRef       (Biến đếm tham chiếu)
+0x0C: m_pCP        (Con trỏ IConnectionPoint)
+0x10: m_dwCookie   (Mã cookie)
```


**IUknown**
Mọi interface trong COM đều bắt buộc phải kế thừa từ `IUnknown`. Interface này định nghĩa 3 phương thức nằm ở 3 slot đầu của mọi Vtable.

|**Slot**|**Phương thức**|**Chức năng cốt lõi**|
|---|---|---|
|**0 (`+0x00`)**|**`QueryInterface`**|Hỏi đối tượng: _"Mày có hỗ trợ Interface `IID_X` không?"_. Nếu có, nó trả về con trỏ tới Interface đó; nếu không, trả về lỗi `E_NOINTERFACE`. Đây là cơ chế ép kiểu an toàn (Dynamic Cast) của COM.|
|**1 (`+0x04`)**|**`AddRef`**|Tăng biến đếm tham chiếu (`m_refCount++`) khi có một nơi mới trỏ vào đối tượng.|
|**2 (`+0x08`)**|**`Release`**|Giảm biến đếm (`m_refCount--`). Khi biến đếm về `0`, đối tượng sẽ tự gọi `delete this` để giải phóng chính nó khỏi RAM.|
Nhờ cơ chế này, Caller không bao giờ cần biết kích thước thật của Object hay dùng lệnh `free/delete`, tránh hoàn toàn lỗi xung đột bộ nhớ giữa các thư viện.

**Hệ thống định danh**
COM không dùng chuỗi kí tự hay tên lớp để nhận diện, vì tên chuỗi dễ bị trùng lặp. Thay vào đó, nó dùng GUIP (128 bit ngẫu nhiên):
- ==CLSID (Class ID):== Định danh duy nhất cho 1 class cụ thể.
- ==IID (Interface ID):== Định danh duy nhất cho 1 interface.

**Cách hoạt động**
Khi 1 ứng dụng muốn dùng 1 dịch vụ COM (ví dụ gọi qua hàm Win32 `CoCreateInstance`), hệ thống xử lí theo 4 bước tuần tự:
```
[Ứng dụng] ──(1. CoCreateInstance)──► [COM Subsystem]
                                              │
                                     (2. Tra cứu Registry)
                                              ▼
[COM Object trên Heap] ◄──(4. Tạo mới)── [DLL Server]
```
- ==Tra cứu Registry:== Hệ điều hành lấy `CLSID` tra cứu trong `HKEY_CLASSES_ROOT\CLSID\{GUID}\InprocServer32`. Đường dẫn tới file dll tương ứng được trích xuất (subkey này chứa đường dẫn đến dll).
- ==Nạp Dll:== COM subsystem gọi `LoadLibrary("path_to_dll.dll")`.
- ==Lây xưởng đúc (Class Factory):== Hệ thống gọi hàm export `DllGetClassObject` của DLL để lấy interface `IClassFactory`.
- ==Đúc ra đối tượng:== Gọi hàm `IClassFactory::CreateInstance`. DLL dùng `new` hoặc `HeapAlloc` để dựng Object trên RAM, gán bảng Vtable và trả con trỏ `IUnknown*` về cho ứng dụng.