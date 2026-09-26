Đọc [[COM]] trước để có cái nhìn tổng quát.
==Browser Helper Object (BHO) là 1 thành phần COM nội tiên trình (In-Process COM Server)== chạy dưới dạng thư viện liên kết động (`.dll`), được hệ điều hành nạp trực tiếp vào không gian địa chỉ bộ nhớ ảo của trình duyệt Internet Explorer hoặc Win Explorer mỗi khi tiến trình khởi tạo. Do hoạt động cùng cấp đặc quyền với tiến trình máy chủ, BHO có toàn quyền truy cập bộ nhớ, điều khiển đối tượn tài liệu (DOM) và can thiệp vào toàn bộ luồng dữ liệu mạng trước khi diễn ra quá trình mã hóa.

**Cơ chế đăng kí  và nạp.**
BHOP không sở hữu giao diện đồ họa độc lập, để trình duyệt nhận diện và nạp DLL, BHO phải đăng kí cấu trúc định danh định dạng nhị phân trong Win Registry.
```
[Windows Registry]
  ├── HKCR\CLSID\{GUID}
  │     └── InprocServer32 ──► (Default) = "C:\Path\To\BHO.dll"
  │                           ThreadingModel = "Apartment"
  └── HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Browser Helper Objects\{GUID}
        └── NoExplorer = 1 (Tùy chọn: ngăn nạp vào explorer.exe)
```
Tương tự với các COM khác, quy trình nạp tự động qua các bước: 
- ==Quét cấu hình khởi động:== Khi `iexplore.exe` tạo một cửa sổ hoặc tab mới, nó duyệt qua nhánh Registry `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Browser Helper Objects`.
- ==Nạp DLL:== Trình duyệt lấy danh sách các chuỗi `{GUID}` (CLSID) đã đăng ký, tra cứu đường dẫn tương ứng tại `HKCR\CLSID\{GUID}\InprocServer32` và gọi API Win32:
```cpp
HMODULE hModule = LoadLibraryExW(L"C:\\Path\\To\\BHO.dll", NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
```
- ==Khởi tạo thông qua xưởng đúc (Class Factory):==
    - Trình duyệt tìm hàm xuất `DllGetClassObject` của DLL để xin con trỏ interface `IClassFactory`.
    - Trình duyệt thực thi phương thức `IClassFactory::CreateInstance` để yêu cầu DLL cấp phát thực thể đối tượng BHO trên Heap.
Ngay sau khi `DllGetClassObject` chạy xong, quy trình chuyển tiếp giữa hệ điều hành và BHO diễn ra tuần tự qua các bước sau để đưa đối tượng vào hoạt động:
```
[iexplore.exe]
      │
      ├── 1. Gọi DllGetClassObject(...) ─────────► [DLL trả về con trỏ IClassFactory*]
      │
      ├── 2. Gọi pFactory->CreateInstance(...) ──► [DLL chạy 'new CMyBHO' trên Heap]
      │                                            (Con trỏ 'this' của BHO sinh ra tại đây)
      │
      ├── 3. Gọi pFactory->Release() ────────────► [Hủy bỏ đối tượng Factory vì xong việc]
      │
      ├── 4. Gọi pBHO->QueryInterface(           
      │        IID_IObjectWithSite, &pSite) ─────► [Lấy Vtable IObjectWithSite của BHO]
      │
      ├── 5. Gọi pSite->SetSite(pUnkSite) ───────► [Nhảy vào hàm sub_100020B0]
      │                                                    │
      │                                     (Bên trong SetSite)
      │                                                    ▼
      │                                     - QueryInterface lấy IConnectionPointContainer
      │                                     - FindConnectionPoint lấy IConnectionPoint
      │                                     - Advise để gắn EventSink (&unk_1000658C)
      │                                                    │
      ▼                                                    ▼
[Hoàn tất khởi tạo] ◄─────────────────────── [SetSite trả về S_OK (0)]
```
==Bước 1: `DllGetClassObject` chỉ mới tạo ra "Thợ đúc"==
Hàm này chưa hề tạo ra BHO. Nó chỉ cấp phát đối tượng xưởng đúc `CClassFactory` và trả về con trỏ interface `IClassFactory*` cho IE.
==Bước 2: IE ra lệnh đúc BHO (`CreateInstance`)==
IE dùng con trỏ `IClassFactory*` gọi method ở Slot 3:
```cpp
pFactory->CreateInstance(NULL, IID_IUnknown, (void**)&pBHOUnknown);
```
Bên trong mã nguồn của DLL, hàm này thực thi toán tử `new` của C++:
```cpp
CMyBHO *pNewBHO = new CMyBHO(); // Cấp phát bộ nhớ trên Heap
// Con trỏ this mà bạn thắc mắc chính thức ra đời tại đây
return pNewBHO->QueryInterface(riid, ppvObject);
```
==Bước 3: IE hủy xưởng đúc==
Vì đã có đối tượng BHO trong tay, IE không cần xưởng đúc nữa:
```cpp
pFactory->Release(); // Xóa CClassFactory khỏi RAM để tiết kiệm bộ nhớ
```
==Bước 4: IE hỏi xin quyền gắn Site (`QueryInterface`)==
IE kiểm tra xem con BHO vừa đúc có đúng là một BHO tiêu chuẩn hay không bằng cách truy vấn interface `IObjectWithSite`:
```cpp
IObjectWithSite *pSite = NULL;
pBHOUnknown->QueryInterface(IID_IObjectWithSite, (void**)&pSite);
```
==Bước 5: IE kích hoạt BHO thông qua `SetSite`==
IE gọi phương thức ở Slot 3 của `IObjectWithSite` và chuyển giao quyền điều khiển:
```cpp
pSite->SetSite(pIEUnknown); // pIEUnknown chính là tham số a3 trong sub_100020B0
```
==Bước 6: BHO tự cài cắm hook (Bên trong `SetSite`)==
Đây chính là đoạn mã giả `sub_100020B0` và `sub_10002180` trong IDA của bạn:
- Lấy `IConnectionPointContainer` từ `a3`.
- Tìm `DIID_DWebBrowserEvents2` để lấy `IConnectionPoint`.
- Gọi `Advise` gắn địa chỉ bảng vtable `IDispatch` (`&unk_1000658C`) vào IE.
- Lưu `dwCookie` vào biến thành viên `*(this + 24)`.


Sau khi chuỗi trên kết thúc, hàm `SetSite` trả về `0` (`S_OK`):
- ==BHO rơi vào trạng thái ngủ ngầm hoàn toàn:== Không có thread riêng, không có vòng lặp kiểm tra liên tục.
- ==Chờ sự kiện:== Mỗi khi người dùng gõ phím, click chuột điều hướng hoặc gửi form đăng nhập, IE sẽ tự động kích hoạt ngắt và gọi thẳng vào hàm `Invoke` (`sub_10001810`) của BHO thông qua con trỏ đã đăng ký lúc gọi `Advise`.

**Cầu nối vòng đời: IObjectWithSite**
Một COM Object thông thường chỉ nhận lệnh từ Client. Tuy nhiên BHO là 1 Hosted Object (đối tượng được nhúng) - nó cần 1 cơ chế tương tác ngược để truy vấn trạng thái và điều khiển ứng dụng mẹ (Host). Chuẩn COM giải quyết bài toán này thông qua Interface `IObjectWithSite`.
Vtable của `IObjectWithSite` gồm 5 con trỏ hàm theo thứ tự:
- `0x0`: `QueryInterface`.
- `0x4`: `AddRef`.
- `0x8`: `Release`.
- `0xC`: `SetSite(IUnknown \*pUnkSite)`.
- `0x10`: `GetSite(REFIID riid, void \*\*ppvSite)`.
```
[Internet Explorer (Host)]
                           │
             (1) Gọi SetSite(pUnkSite)
                           │
                           ▼
                 [BHO COM Instance]
                           │
      ┌────────────────────┴────────────────────┐
      ▼                                         ▼
Khi pUnkSite != NULL (Khởi tạo)           Khi pUnkSite == NULL (Đóng tab)
- Tăng refcount IE (AddRef)               - Hủy đăng ký sự kiện (Unadvise)
- Lưu con trỏ Site vào đối tượng          - Giải phóng con trỏ kết nối (Release)
- Thiết lập Connection Point Hooks        - Dọn dẹp tài nguyên Heap
```
Khi IE khởi tạo BHO, nó truyền con trỏ `pUnkSite` (đại diện cho cửa sổ duyệt web) vào hàm `SetSite`. Ngược lại, khi đóng tab hoặc thoát trình duyệt, IE gọi lại `SetSite(NULL)` để ra lệnh cho BHO tháo dỡ toàn bộ liên kết.


**Cơ chế đánh chặn sự kiện: Connection Point & Event Sinking**
IE hoạt động như 1 nguồn phát tín hiệu. Để nhận thống báo mỗi khi người dùng duyệt web, BHO phải đóng vai trò là 1 điểm tiếp nhận sự kiện (Event Sink) thông qua cơ chế COM Connection Points.
```
[BHO]                                                      [Internet Explorer]
  │                                                                 │
  ├─── 1. QueryInterface(IID_IConnectionPointContainer) ───────────►│
  │◄── Trả về con trỏ IConnectionPointContainer ────────────────────┤
  │                                                                 │
  ├─── 2. FindConnectionPoint(DIID_DWebBrowserEvents2) ─────────────►│
  │◄── Trả về con trỏ IConnectionPoint ─────────────────────────────┤
  │                                                                 │
  ├─── 3. Advise(pEventSinkIDispatch, &dwCookie) ───────────────────►│ (Gắn Hook)
  │◄── Trả về mã Cookie phiên kết nối ──────────────────────────────┤
```
Quy trình thiết lập Hook:
- ==Truy vấn Container:== Từ `pUnkSite`, BHO gọi `QueryInterface` với `IID_IConnectionPointContainer` (`{B196B284-BAB4-101A-B69C-00AA00341D07}`).![[Pasted image 20260921160924.png]]
- ==Tìm cổng kết nối:== BHO gọi method `FindConnectionPoint` trên container vừa nhận, truyền vào GUID của giao diện sự kiện duyệt web `DIID_DWebBrowserEvents2` (`{34A715A0-6587-11D0-924A-0020AFC7AC4D}`). Kết quả trả về một con trỏ `IConnectionPoint`.
- ==Đăng ký lắng nghe (`Advise`):== BHO gọi `IConnectionPoint::Advise`, truyền con trỏ tới một cấu trúc chứa interface `IDispatch` (Event Sink do BHO tự cài đặt). IE trả về một biến nguyên 32-bit (`dwCookie`) dùng làm định danh để gỡ bỏ sau này.
....

**Sự Thoái trào của Công nghệ BHO**
Kiến trúc BHO phản ánh triết lý thiết kế phần mềm thời kỳ đầu của Windows, vốn ưu tiên khả năng can thiệp sâu và tính linh hoạt hơn là sự cô lập an toàn:
- ==Thiếu cơ chế Sandbox:== BHO chạy cùng tiến trình, có toàn quyền đọc ghi vùng nhớ của trình duyệt và kế thừa đầy đủ quyền hạn của tài khoản người dùng đang đăng nhập.
- ==Cơ chế phòng thủ muộn:== Bắt đầu từ Internet Explorer 7 đến 11, Microsoft đưa vào tính năng **Protected Mode** (dựa trên Windows Integrity Mechanism) để ép BHO chạy ở mức quyền hạn thấp (Low Integrity), hạn chế khả năng ghi file ra ổ đĩa và can thiệp sâu vào hệ thống.
- ==Khai tử:== Khi Internet Explorer chính thức ngừng hỗ trợ và Microsoft chuyển hoàn toàn sang trình duyệt Microsoft Edge nền tảng Chromium, công nghệ BHO đã bị loại bỏ. Các phần mở rộng trình duyệt hiện đại chuyển sang kiến trúc ==WebExtensions==, chạy trong tiến trình tách biệt (Process Isolation) và chỉ được giao tiếp qua các API có kiểm soát chặt chẽ về quyền hạn (Permissions Model).