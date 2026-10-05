# **Lab 1-1**

## 1. 

Bỏ 2 file vào VT:

*Lab01-01.dll* 

![](../../../image/Pasted%20image%2020261004150727.png)

- 40/71 phần mềm nhận diện là virus.
- Label nhận diện phổ biến nhất là `trojan.skeeyah/genericrxfo`.
- VT xếp vào các nhóm: `trojan`, `adware`, `pua`.

*Lab01-01.exe*

![](../../../image/Pasted%20image%2020261004150803.png)

- 56/71 phần mềm nhận diện là virus.
- Label nhận diện phổ biến nhất là `trojan.ulise/aenjaris`.
- VT xếp vào các nhóm: `trojan`, `downloader`, `worm`.

## 2. 

![](../../../image/Pasted%20image%2020261004151343.png)

`Lab01-01.dll` biên dịch vào `2010-12-19 16:16:38 UTC`.

![](../../../image/Pasted%20image%2020261004151440.png)

`Lab01-01.exe` biên dịch vào `2010-12-19 16:16:19 UTC`.

# 3.

*Lab01-01.exe*

![](../../../image/Pasted%20image%2020261004151605.png)

DiE không nhận diện được dấu hiệu file bị packed.

![](../../../image/Pasted%20image%2020261004151654.png)

Bảng import khá rõ ràng, không cho thấy dấu hiệu bị packed.

![](../../../image/Pasted%20image%2020261004151737.png)

Bảng strings cũng không cho thấy dấu hiệu bị packed.

*Lab01-01.dll*

![](../../../image/Pasted%20image%2020261004151820.png)

DiE không nhận diện được dấu hiệu bị packed.

![](../../../image/Pasted%20image%2020261004151933.png)

![](../../../image/Pasted%20image%2020261004151946.png)

Bảng import và strings cũng không cho thấy dấu hiệu quá rõ ràng cho việc file bị packed.

## 4.

*Lab01-01.dll*

![](../../../image/Pasted%20image%2020261004152107.png)

Có API `CreateProcessA`, có tác dụng tạo ra 1 tiến trình mới. Ngoài ra còn sử dụng thư viện `WS2_32.dll` (WinSock), cung cấp các API hỗ trợ giao tiếp mạng.

*Lab01-01.exe*

![](../../../image/Pasted%20image%2020261004152505.png)

- `CreateFileMapping` + `MapViewOfFile` + `UnMapViewOfFile`: Tạo 1 handle và ánh xạ file vào không gian địa chỉ của tiến trình.
- `FindFirst/FindNextFile` + `FindClose`: Tìm kiếm file.

## 5.

*Lab01-01.exe*

![](../../../image/Pasted%20image%2020261004152949.png)

Có 2 dấu hiệu có thể tìm kiếm trên máy bị nhiễm:

- File `Lab01-01.dll`.
- File `kernel132.dll`.
- Chuỗi `WARNING_THIS_WILL_DESTROY_YOUR_MACHINE`

*Lab01-01.exe*

![](../../../image/Pasted%20image%2020261004153215.png)

Có 2 dấu hiệu có thể tìm kiếm trên máy bị nhiễm:

- Chuỗi `sleep`
- Chuỗi `hello`

## 6.

Dấu hiệu mạng có thể tìm trên máy bị nhiễm đó là IP `127.26.152.13`.

## 7.

Back door, tải file từ địa chỉ IP cố định, rồi ghi dữ liệu vào 1 file mới, đổi tên thành `Kerne132.dll` để ẩn mình.

# **Lab1-2**

## 1.

![](../../../image/Pasted%20image%2020261004153953.png)

- 56/71 phần mềm nhận diện là virus.
- Label nhận diện phổ biến nhất là `trojan.ulise/trojanclicker`.
- VT xếp vào các nhóm: `trojan`, `downloader`.

## 2.

![](../../../image/Pasted%20image%2020261004154135.png)

DiE nhận diện upx packer.

![](../../../image/Pasted%20image%2020261004154257.png)

Quá ít API được gọi, đây cũng là 1 dấu hiệu.

![](../../../image/Pasted%20image%2020261004154338.png)

Bảng strings có nhiều chuỗi bị lỗi, đây cũng là 1 dấu hiệu.

Có thể unpack bằng tool.

## 3.

![](../../../image/Pasted%20image%2020261004154759.png)

- `GetModuleFileName`: Dùng để lấy handle của 1 module đã được load vào không gian địa chỉ của tiến trình. Trong unpacking, API này thường được gọi để lấy handle của chính file thực thi, để phục vụ unpack.
- `ExitProcess`: Thoát chính tiến trình đang chạy, trong packing, API này dùng để kết thúc tiến trình unpack để chạy tiến trình mới với file được pack.

![](../../../image/Pasted%20image%2020261004155356.png)

- `OpenSCManagerA` +`CreateServiceA` + `StartServiceCtrlDispatcherA`: Mở 1 service handle -> tạo 1 service mới -> kết nối tiến trình dịch vụ với SCM (Service Control Manager). 

![](../../../image/Pasted%20image%2020261004155812.png)

- Thư viện này cũng là 1 thư viện phục vụ kết nối mạng.

## 4.

![](../../../image/Pasted%20image%2020261004155850.png)

*Host:*

- Dịch vụ `MalService`.

*Network:*

- URL `http://www.malwareanalysisbook.com`.
- IE 8.0.

# **Lab 1-3**

## 1.

![](../../../image/Pasted%20image%2020261004160207.png)

 - 61/71 phần mềm nhận diện là virus.
- Label nhận diện phổ biến nhất là `trojan.graftor/genome`.
- VT xếp vào các nhóm: `trojan`.

## 2.

![](../../../image/Pasted%20image%2020261004160319.png)

![](../../../image/Pasted%20image%2020261004160332.png)

![](../../../image/Pasted%20image%2020261004160350.png)

Dấu hiệu bị packed rất rõ ràng.

## 3.

# 4.

# **Lab 1-4**

# 1.

![](../../../image/Pasted%20image%2020261004163111.png)

- 63/71 phần mềm nhận diện là virus.
- Label nhận diện phổ biến nhất là `trojan.cerbu/gofot`.
- VT xếp vào các nhóm: `trojan`, `downloader`, `dropper`.

## 2.

![](../../../image/Pasted%20image%2020261004163255.png)

![](../../../image/Pasted%20image%2020261004163257.png)![](../../../image/Pasted%20image%2020261004163303.png)

Không có dấu hiệu bị packed.

## 3.

## 4.

![](../../../image/Pasted%20image%2020261004163415.png)

- `FindResource` + `LoadResource` + `SizeOfReousrce`: Kết hợp với việc có 1 resource nằm trong file, đây là các API thể hiện hành vi đặc trưng của dropper. Nó thực hiện load 1 resource vào trong không gian bộ nhớ của tiến trình.
- `WinExec`: Thực thi 1 ứng dụng hoặc 1 tiến trình khác.
- `CreateFile` + `WriteFile`: Tạo hoặc mở 1 file rồi ghi vào đó.
- `GetTempPath`: Lấy đường dẫn đến Temporary Folder của hệ thống.
- `LoadLib`: Liên quan đến cơ chế Dynamic API Resolve.

![](../../../image/Pasted%20image%2020261004164738.png)

- `OpenProcessToken` + `LookupPrivilegeValueA` + `AdjustTokenPrivileges`: Mở Acess Token của 1 tiến trình, Acess Token chứa thông tin về các quyền mà tiến trình đang có ->Thực hiện tra cứu các quyền mà tiến trình có -> Chỉnh sửa (bật hoặc tắt) các quyền.

## 5.

![](../../../image/Pasted%20image%2020261004165106.png)

*Host*

- `\winup.exe`, `\system32\wupdmgrd.exe`: Giả mạo.
- `<not real>`.
- `Winlogon.exe`.

*Network*

- `http://www.practicalmalwareanalysis.com/updater.exe`

## 6.

Dump resource ra bằng Resource Hacker.

![](../../../image/Pasted%20image%2020261004170926.png)

 - `URLDownLoadToFileA`, thực hiện download dữ liệu từ 1 URL.
