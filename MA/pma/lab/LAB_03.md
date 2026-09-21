# **Lab_03-1.malware**
1. 
Dùng resourec hacker để xem resource của file, ta tìm được 1 resource khả nghi nằm trong `RC_DATA` (là section `.rsrc`).
![[Pasted image 20260921084455.png]]
Ta có thể nhận diện ngay đây là dữ liệu của 1 file thực thi PE. Để extract nó, trong Resource hacker đã có sẵn chức năng extract rồi.

2. 
![[Pasted image 20260921085139.png]]
Trong số các DLL, chỉ có thằng `KERNEL32.DLL` là có thể có các API đặc trừng cho hành vi của malware, nên ta chỉ cần xét `KERNEL32.DLL`.
![[Pasted image 20260921085315.png]]
Đầu tiên là cụm:
```
GetModuleHandleW
        ↓
FindResourceW
        ↓
LoadResource
        ↓
LockResource
        ↓
SizeofResource
        ↓
CreateFileW
        ↓
WriteFile
        ↓
CloseHandle
```
Tạo ra hành vi extract resource/dropper.
- `GetModuleHandleW`: Lấy handle của 1 module hiện tại hoặc 1 dll đã được nạp, malware thường lấy handle của chính nó để truy cập vào resource của PE.
- `FindSourceW`: Tìm 1 resource trong `.rsrc` của module.
- `LoadResource`: Lấy handle của resource đó.
- `LockResource`: Biến handle thành con trỏ trỏ tới resource.
- `SizeOfResource`: Lấy kích thước của resource.
- `CreateFileW`: Tạo hoặc mở file đích trên ổ đĩa.
- `WriteFile`: Ghi dữ liệu vào file đích.
- `CloseHanlde`: Đóng handle.
Tiếp đến là API antidebug cơ bản: `IsDebuggerPresent`.
Cụm xử lí exception:
```
SetUnhandledExceptionFilter
          ↓
UnhandledExceptionFilter
          ↓
GetCurrentProcess
          ↓
TerminateProcess
```
- `SetUnhandledExceptionFilter`: Đăng kí hàm xử lí exception cuối cùng của tiến trình khi không có hàm nào xử lí được.
- `UnhandledExceptionFilter`: Handler mặc định của Windows khi không có handler nào xử lí được exception nữa.
- `GetCurrentProcess`: Trả về pseudo-handle cho tiến trình hiện tại.
- `TerminateProcess`: Buộc kết thúc 1 tiến trình.

3. 
![[Pasted image 20260921093455.png]]
Đây là những chuỗi khả nghi trong chương trình. 
- Đầu tiên là các URL lạ, phù hợp với trường hợp được ghi nhận trong đề: random popups.
- Tiếp đến là `explorer.exe`, có nhiều hướng để khai thác từ chuỗi này.
- `CLSID...` cái này là định danh