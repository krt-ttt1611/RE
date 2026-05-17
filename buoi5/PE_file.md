*1. PE file là gì.* 

PE (Portable Executable file format) là một định dạng file dành riêng cho hệ điều hành Windows, có 2 loại định dạng PE: PE32 (cho kiến trúc CPU 32 bit) và PE32+ (cho kiến trúc CPU 64 bit). Trên Window, có 

*2. PE32.* 

![](../ảnh/Pasted%20image%2020260505090955.png)

Hình trên là minh họa cho cấu trúc cơ bản của 1 PE32 file. 

2.1. DOS MZ Header. 

Tác dụng: Giúp chương trình tương thích ngược với hệ điều hành DOS. Cụ thể, nếu mang một Chương trình định dạng PE32 đem xuống hệ điều hành DOS chạy, hệ điều hành sẽ xem nó là 1 chương trình hợp lệ và chạy DOS Stub (phần kế tiếp). DOS Stub thường sẽ trả về chuỗi "This program must be run under Microsoft Windows" rồi thoát.

DOS Header là cấu trúc _ IMAGE_DOS_HEADER được định nghĩa trong file windows.inc hoặc winnt.h. Nó có tất cả 19 thành phần.

```c
//winnt.h
typedef struct _IMAGE_DOS_HEADER {      // DOS .EXE header

    WORD   e_magic;                     // Magic number

    WORD   e_cblp;                      // Bytes on last page of file

    WORD   e_cp;                        // Pages in file

    WORD   e_crlc;                      // Relocations

    WORD   e_cparhdr;                   // Size of header in paragraphs

    WORD   e_minalloc;                  // Minimum extra paragraphs needed

    WORD   e_maxalloc;                  // Maximum extra paragraphs needed

    WORD   e_ss;                        // Initial (relative) SS value

    WORD   e_sp;                        // Initial SP value

    WORD   e_csum;                      // Checksum

    WORD   e_ip;                        // Initial IP value

    WORD   e_cs;                        // Initial (relative) CS value

    WORD   e_lfarlc;                    // File address of relocation table

    WORD   e_ovno;                      // Overlay number

    WORD   e_res[4];                    // Reserved words

    WORD   e_oemid;                     // OEM identifier (for e_oeminfo)

    WORD   e_oeminfo;                   // OEM information; e_oemid specific

    WORD   e_res2[10];                  // Reserved words

    LONG   e_lfanew;                    // File address of new exe header

  } IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;
```

2.2. PE Header (Nt Header). 

PE Header là 1 struct _ IMAGE_NT_HEADERS có 3 member được định nghĩa trong file windows.inc, chứa các thông tin thiết yếu được sử dụng bởi loader.

```c
//winnt.h
typedef struct _IMAGE_NT_HEADERS {

    DWORD Signature;

    IMAGE_FILE_HEADER FileHeader;

    IMAGE_OPTIONAL_HEADER32 OptionalHeader;

} IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;
```

2.3. Section Header. 

```c
//winnt.h

#define IMAGE_SIZEOF_SHORT_NAME              8

  

typedef struct _IMAGE_SECTION_HEADER {

    BYTE    Name[IMAGE_SIZEOF_SHORT_NAME];

    union {

            DWORD   PhysicalAddress;

            DWORD   VirtualSize;

    } Misc;

    DWORD   VirtualAddress;

    DWORD   SizeOfRawData;

    DWORD   PointerToRawData;

    DWORD   PointerToRelocations;

    DWORD   PointerToLinenumbers;

    WORD    NumberOfRelocations;

    WORD    NumberOfLinenumbers;

    DWORD   Characteristics;

} IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;

  

#define IMAGE_SIZEOF_SECTION_HEADER          40
```

Mỗi phần tử trong Section Headers sẽ chứa thông tin về 1 section. 1 chương trình sau khi được biên dịch sẽ được chia thành nhiều phân vùng chứa dữ liệu, gọi là section

2.4. Sections. 

Phần này chứa nội dung của từng section.

2.5. Overlay. 

Phần này có thể xem như phần mở rộng, vì loader không nạp phần này vào RAM.

*3. Phân tích chi tiết qua demo.*  

Ta sẽ tạo 1 file code c rồi biên dịch sang file thực thi 32 bit của windows.

```c
//test.c
#include <stdio.h>

int main(){
	printf("hello world");
	return 0;
}
```

Sau khi biên dịch xong, dùng PE-Bear để xem và phân tích.

![](../ảnh/Pasted%20image%2020260507225925.png)

3.1. DOS Header.

![](../ảnh/Pasted%20image%2020260507174948.png)

Hình trên là tất cả 19 thành phần của DOS Header. Chúng ta chỉ cần quan tâm đến 2 thành phần sau:

- Magic number (e_magic): Chứa 2 bytes 4D 5A, là M, Z, kí hiệu tên của 1 trong số những người sáng lập ra MS-DOS.

- File address of new exe header (e_lfanew): Nằm ở cuối cấu trúc, chứa địa chỉ của PE Header. Khi thực thi, loader khi có được địa chỉ sẽ nhảy thẳng đến PE Header, bỏ qua toàn bộ phần liên quan đến DOS.

3.2. PE Header.

a) Signature.

![](../ảnh/Pasted%20image%2020260507192924.png)

Phần này chỉ gồm 4 bytes: 0x50, 0x45, 0x00 và 0x00, dịch ra lần lượt là P, E, 0 , 0.

b) File Header.

Trong winnt.h, File Header được định nghĩa là _ IMAGE_FILE_HEADER

```c
//winnt.h
typedef struct _IMAGE_FILE_HEADER {

    WORD    Machine;

    WORD    NumberOfSections;

    DWORD   TimeDateStamp;

    DWORD   PointerToSymbolTable;

    DWORD   NumberOfSymbols;

    WORD    SizeOfOptionalHeader;

    WORD    Characteristics;

} IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;
```

![](../ảnh/Pasted%20image%2020260507202938.png)

- Machine: Khai báo kiến trúc CPU mà file được thiết kế để chạy. Loader sẽ kiểm tra thôn tin này trước khi chạy để xem có tương thích không.

- Sections Count (NumberOfSections): Số lượng Sections của file.

- Time Date Stamp (TimeDateStamp): Thời gian tạo file.

- Ptr to Symbol Table (PointerToSymbolTable): Con trỏ trỏ đến bảng Symbol. Bảng Symbol chứa các thông tin gỡ lỗi (debug) như tên biến gốc, tên hàm gốc trong code của chương trình.

- Num. of Symbols (NumberOfSymbols): Số lương Symbols có trong bảng.

- Size of OptionalHeader (SizeOfOptionalHeader): Báo trước kích thước của Optional Header.

- Characteristics: Chứa các bit cờ cho biết thông tin của file:

	- 1: File này không có phần .reloc. Khi nạp vào RAM, nó phải nằm ở đúng địa chỉ ImageBase.

	- 2: File này có thể thực thi được.

	- 4: Số thứ tự dòng code bị xóa.

	- 100: Chương trình 32 bit.

c) Optional Header.

```c
//winnt.h
typedef struct _IMAGE_OPTIONAL_HEADER {

    //

    // Standard fields.

    //

  

    WORD    Magic;

    BYTE    MajorLinkerVersion;

    BYTE    MinorLinkerVersion;

    DWORD   SizeOfCode;

    DWORD   SizeOfInitializedData;

    DWORD   SizeOfUninitializedData;

    DWORD   AddressOfEntryPoint;

    DWORD   BaseOfCode;

    DWORD   BaseOfData;

  

    //

    // NT additional fields.

    //

  

    DWORD   ImageBase;

    DWORD   SectionAlignment;

    DWORD   FileAlignment;

    WORD    MajorOperatingSystemVersion;

    WORD    MinorOperatingSystemVersion;

    WORD    MajorImageVersion;

    WORD    MinorImageVersion;

    WORD    MajorSubsystemVersion;

    WORD    MinorSubsystemVersion;

    DWORD   Win32VersionValue;

    DWORD   SizeOfImage;

    DWORD   SizeOfHeaders;

    DWORD   CheckSum;

    WORD    Subsystem;

    WORD    DllCharacteristics;

    DWORD   SizeOfStackReserve;

    DWORD   SizeOfStackCommit;

    DWORD   SizeOfHeapReserve;

    DWORD   SizeOfHeapCommit;

    DWORD   LoaderFlags;

    DWORD   NumberOfRvaAndSizes;

    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];

} IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;
```

![](../ảnh/Pasted%20image%2020260507205648.png)

![](../ảnh/Pasted%20image%2020260507223215.png)

Phần này chứa tất cả 224 bytes dữ liệu:

- Magic: Chứa 2 bytes 0B, 01.

- Linker Ver: Phiên bản của Linker, 2.22.

- Size of code (SizeOfCode): Tổng dung lượng các section chứa mã máy (như .text), 0x1800 bytes.

- Size of initialized data (SizeOfInitializedData): Tổng dung lượng các sections chứa dữ liệu đã khởi tạo (như .data, .rdata), 0x2a00 bytes.

- Size of uninitialized data (SizeOfUninitializedData): Tổng dung lượng các sections chứa dữ liệu chưa khởi tạo (như .bss), 0x400 bytes.

- Entry Point (AddressOfEntryPoint): Địa chỉ offset của entry point, là địa chỉ dòng lệnh mã máy đầu tiên được thực thi, 0x14c0.

- Base of Code (BaseOfCode): Địa chỉ offset bắt đầu của khối code trên RAM.

- Base of Data (BaseOfData): Địa chỉ offset bắt đầu của khối data trên RAM.

- Image Base (ImageBase): địa chỉ cơ sở của chương trình trên RAM.

- Section Alignment: Bất kì section nào khi nạp lên RAM cũng phải căn chỉnh sao cho bằng với bội số của độ lớn section alignment, ở đây là 0x1000 (4096) byte.

- OS Ver: 4.0 (Win NT 95/4.0).

- Subsystem Ver: 4.0 (Win NT 95/4.0), là phiên bản windows core tối thiểu để chạy file.

- Size of Image (SizeOfImage): Tổng dung lượng của chương trình ở trên RAM, 0x4b000 bytes.

- Checksum (CheckSum): 0x52f45.

- Subsystem: 3, cờ 3 cho biết đây là ứng dụng windows console. 

- DLL Characteristics: Trường này chứa các cờ liên quan đến các cơ chế bảo mật như ASLR, DEP..., ở đay bằng 0 nghĩa là không có cơ chế bảo mật nào được bật.

- SizeOfStackReserve: 2MB, là dung lượng bộ nhớ stack ảo mà chương trình đăng kí trước, chưa tốn dung lượng thật.

- SizeOfStackCommit: 4KB, là dung lượng bộ nhớ stack mà chương trình được cấp phát ban đầu.

- SizeOfHeapReserve/Commit: Tương tự stack.

- Number of RVAs and Sizes: Số lượng chỉ mục trong data directory (phần bên dưới), 16 chỉ mục. Tuy nhiên, chỉ có 3 chỉ mục có tác dụng:

	- Import Directory: Danh sách các hàm được gọi từ hệ điều hành.

	- Import Address Table: Chứa địa chỉ của các hàm gọi từ hệ điều hành. Khi nạp chương trình, windows sẽ tìm địa chỉ thực của các hàm này và ghi vào IAT.

	- TLS Directory: Lưu dữ liệu riêng cho từng luồng của chương trình.

3.4. Section Headers.

![](../ảnh/Pasted%20image%2020260507224933.png)

Phần này chứa thông tin về các section của file:

- Name: Tên sections (tối đa 8 ký tự).

- Raw Addr: Địa chỉ offset của section trên ổ đĩa.

- Raw Size: Kích thước của section trên ổ đĩa.

- Virtual Addr: Địa chỉ offset của section sau khi nạp vào RAM.

- Virtual Size: Kích thước của section sau khi nạp vào RAM.

- Characteristic: Cờ chứa thông tin về quyền của section.


Cuối cùng là dữ liệu của các section và phần overlay. 

*4. PE32+.*

PE32+ gần như tương tự với PE32, chỉ khác ở một số điểm:

- Phần magic ở Optional Haeder đổi thành 0x20B (PE32 là 0x10B)

![](../ảnh/Pasted%20image%2020260507231025.png)

- Thông tin về địa chỉ Base of Code không còn.

- Kích thước  các trường dữ liệu mở rộng lên 64bit.
- ...

*5. Quá trình load chương trình vào RAM.* 

Đầu tiên, loader đọc DOS Header, kiểm tra magic bytes có đúng là `4D 5A` không, sau đó đọc `e_lfanew` để lấy offset của PE Header rồi nhảy đến đó. Tại PE Header, loader kiểm tra Signature (`50 45 00 00`), đọc `Machine` trong File Header để xác nhận tương thích kiến trúc CPU, rồi đọc `ImageBase` và `SizeOfImage` trong Optional Header để cấp phát vùng nhớ ảo. Loader sẽ ưu tiên cấp phát tại địa chỉ `ImageBase`, nếu vùng đó đã bị chiếm thì sẽ tìm vùng khác và thực hiện relocation dựa vào bảng `.reloc` (nếu có).

Tiếp theo, dựa vào Section Headers, loader copy từng section từ ổ đĩa lên RAM theo cơ chế memory-mapped file — tức là chưa copy thật sự ngay mà chỉ tạo mapping, khi nào CPU truy cập mới thực sự đọc từ đĩa lên (demand paging). Địa chỉ bắt đầu của mỗi section được căn chỉnh theo `SectionAlignment`, phần dư được padding bằng 0. Quyền truy cập từng section được thiết lập dựa trên `Characteristics`. Sau đó loader đọc Import Directory, tìm và load các DLL cần thiết, resolve địa chỉ thực của từng hàm rồi ghi vào IAT. Cuối cùng, loader nhảy đến `ImageBase + AddressOfEntryPoint` để bắt đầu thực thi.




