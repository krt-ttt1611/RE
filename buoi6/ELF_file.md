*1. ELF file là gì.*

ELF(Executable and Linkable Format) là một định dạng file dành cho hệ điều hành họ unix như linux, solaris... , có 2 loại: ELF32 dành cho kiến trúc CPU 32 bit và ELF64 dành cho kiến trúc CPU 64 bit. Trên linux, có 3 loại file có định dạng ELF (gọi chung là file đối tượng):

- Relocatable file: File này có nhiệm vụ chứa code và dữ liệu phù hợp để liên kết được với các file đối tượng khác để tạo ra 1 file thực thi hoặc file đối tượng chia sẻ (.so)
- Executable file: File này chứa 1 chương trình sẵn sàng để chạy. File này còn chỉ định chính xác cách hệ điều hành tạo ra 1 ảnh tiến trình (program's process image) trên RAM.
- Shared object file: File này chứa code và dữ liệu phù hợp để liên kết trong 2 trường hợp: Đầu tiên, trình biên dịch liên kết có thể xử lí nó cùng với các relocatable file hoặc shared object file khác để tạo ra 1 file đối tượng khác. Thứ 2, trình liên kết động kết nối nó với 1 executable file khác và các shared object file khác để tạo ra 1 process image.

Trong bài viết này chỉ tập trung về executable file.

*2. ELF32.*

![](../ảnh/Pasted%20image%2020260516075154.png)

Hình trên là cấu trúc của 1 file ELF32 từ 2 góc nhìn: Góc nhìn liên kết (nhìn từ linker) và góc nhìn thực thi (nhìn từ loader). ELF header nằm ở phần đầu của file và chứa các thông tin tổng quát về chương trình. Program header table chứa các thông tin để giúp loader tạo 1 process image. Section header table chứa các thông tin về các section của file. Trong linux, các trường thông tin (trừ section header table) được định nghĩa là các cấu trúc, có thể xem trong file elf.h.
```c
//elf.h

//header
typedef struct
{
  unsigned char e_ident[EI_NIDENT];     /* Magic number and other info */
  Elf32_Half    e_type;                 /* Object file type */
  Elf32_Half    e_machine;              /* Architecture */
  Elf32_Word    e_version;              /* Object file version */
  Elf32_Addr    e_entry;                /* Entry point virtual address */
  Elf32_Off     e_phoff;                /* Program header table file offset */
  Elf32_Off     e_shoff;                /* Section header table file offset */
  Elf32_Word    e_flags;                /* Processor-specific flags */
  Elf32_Half    e_ehsize;               /* ELF header size in bytes */
  Elf32_Half    e_phentsize;            /* Program header table entry size */
  Elf32_Half    e_phnum;                /* Program header table entry count */
  Elf32_Half    e_shentsize;            /* Section header table entry size */
  Elf32_Half    e_shnum;                /* Section header table entry count */
  Elf32_Half    e_shstrndx;             /* Section header string table index */
} Elf32_Ehdr;

//Program table
typedef struct
{
  Elf32_Word    p_type;                 /* Segment type */
  Elf32_Off     p_offset;               /* Segment file offset */
  Elf32_Addr    p_vaddr;                /* Segment virtual address */
  Elf32_Addr    p_paddr;                /* Segment physical address */
  Elf32_Word    p_filesz;               /* Segment size in file */
  Elf32_Word    p_memsz;                /* Segment size in memory */
  Elf32_Word    p_flags;                /* Segment flags */
  Elf32_Word    p_align;                /* Segment alignment */
} Elf32_Phdr;

//Section header
typedef struct
{
  Elf32_Word    sh_name;                /* Section name (string tbl index) */
  Elf32_Word    sh_type;                /* Section type */
  Elf32_Word    sh_flags;               /* Section flags */
  Elf32_Addr    sh_addr;                /* Section virtual addr at execution */
  Elf32_Off     sh_offset;              /* Section file offset */
  Elf32_Word    sh_size;                /* Section size in bytes */
  Elf32_Word    sh_link;                /* Link to another section */
  Elf32_Word    sh_info;                /* Additional section information */
  Elf32_Word    sh_addralign;           /* Section alignment */
  Elf32_Word    sh_entsize;             /* Entry size if section holds table */
} Elf32_Shdr;

```

*3. Phân tích qua demo.*

Ta sẽ tạo 1 file code c rồi biên dịch bằng gcc để tạo ra 1 file elf32. Sau đó, dùng công cụ readelf để đọc các trường thông tin.

**a) ELF Header.**

![](../ảnh/Pasted%20image%2020260516202857.png)

- `Magic`: Chứa các byte định danh của file: 0x7f, 0x45, 0x4c, 0x46, dịch ra text là '0x7f', E, L, F. Ngoài ra, các byte phía sau còn chứa thêm các thông tin khác như class, data endianness...
- `Class`: ELF32.
- `Data`: Chính là data endianness, dữ liệu trong file được ghi lần lượt từ byte thấp đến byte cao (little endian).
- `Version`: Phiên bản của định dạng ELF, ở đây là 1.
- `OS/ABI`: Cho biết chuẩn giao tiếp nhị phân của file là SYSTEM V.
- `ABI version`: Phiên bản của ABI, ở đây là 0.
- `Type: DYN`, cho biết file này được liên kết động và có bật PIE (Position-Independent Executable).
- `Machine`: Kiến trúc vi xử lí, ở đây là Intel 80386.
- `Entry point address`: Là địa chỉ tương đối của entry point, ở đây là 0x1070.
- `Start of program headers`: Địa chỉ của program headers table, ở đây nó nằm ở byte thứ 52 tính từ đầu file.
- `Start of section header`: Địa chỉ của section header table, ở đây nằm ở byte thứ 13784 tính từ đầu file.
- `Flags`: Các cờ đặc thù của vi xử lý, ở file này thì không có.
- `Size of this header`: Kích thước của phần ELF header này, 52 bytes.
- `Size of program header`: Kích thước của mỗi phần tử trong struct program header, 32 bytes.
- `Number of program header`: 11 segment. Segment gồm các section được gom lại với nhau. Khi loader nạp chương trình sẽ sử dụng segment, là các section được gom lại với nhau, giúp tối ưu hóa quyền truy cập, tiết kiệm số trang nhớ mà hệ điều hành phải cấp phát và quản lý.
- `Size of section headers`: Kích thước mỗi phần tử trong struct section deaer, 40 byte.
- `Number of section header`: 29 section (section 0 là NULL, section 1-27 chứa dữ liệu, section 28 chứa tên các section còn lại).
- `Section header string table index`: Chỉ số của phần tử section header table (phần tử chứa tên của các phần tử còn lại).

**b) Program Header.**

![](../ảnh/Pasted%20image%2020260516214036.png)

Bảng đầu tiên chứa thông tin của các segment:

- 'Type': đây là cột chỉ các loại segment:
	- `PHDR`: Program Header, trỏ ngược lại vào struct program header, để khi nạp lên RAM, có thể soi lại cấu trúc file.
	- `NOTE`: Ghi chú đính kèm với file.
	- `INTERP` và `DYNAMIC`: Hai trường thông tin này thường chỉ xuất hiện khi file sử dụng liên kết động. Chúng có tác dụng gọi Trình liên kết động của hệ điều hành ra làm việc, đồng thời cung cấp các thông tin cấu hình cần thiết để móc nối thư viện và phân giải địa chỉ hàm khi chương trình thực thi. (Cụ thể hơn xem file [Cấu Trúc Liên Kết Tệp Thực Thi & Cơ Chế Phân Giải Thư Viện Động](../documentary/Cấu%20Trúc%20Liên%20Kết%20Tệp%20Thực%20Thi%20&%20Cơ%20Chế%20Phân%20Giải%20Thư%20Viện%20Động.md))
	- `GNU_STACK`: Segment chứa cờ quản lý quyền cho stack. Cụ thể, hệ điều hành sẽ không cấp quyền execute cho stack vì có segment này.
	- `GNU_RELRO`: Cấp quyền cho vùng nhớ tái định vị thành chỉ đọc.
	- `GNU_EH_FRAME`: Xử lí ngoại lệ.
	- `LOAD`: Đây là các segment chứa hầu hết các dữ liệu quan trọng nhất của chương trình như code, data... Và là segment duy nhất được load vào RAM, các segment phía trên buộc phải nằm bên trong các segment LOAD để được load vào RAM.
- `offset` : Là địa chỉ tương đối của các segment.
- `VirtAddr`: Là địa chỉ ảo trên RAM.
- `PhysAddr`: Là địa chỉ vật lý trên RAM (giờ không còn dùng nữa).
- `FileSiz`: Kích thước segment khi còn nằm trên ổ cứng.
- `Flg`: Cờ chứa quyền của các segment.
- `Align`: Căn địa chỉ của các segment.

Bảng thứ 2 là ảnh xạ từ segment vào các section. Các số 00, 01... là chỉ số của segment đó, bên cạnh là các section nằm trong segment đó.

**c) Section header.**

![](../ảnh/Pasted%20image%2020260517080105.png)

Như đã nói ở trên, bảng section header gồm tất cả 29 phần tử, trong đó từ 1 đến 27 là thông tin về các section có trong file, section 0 là NULL, và section 28 là bảng tên của tất cả section có trong bảng. `Type` là loại section, `Addr` là địa chỉ trên ổ cứng, `off` là địa chỉ offset trên RAM, `Size` là kích thước, `ES` cho biết với các section được định nghĩa là struct, thì 1 phần tử struct có kích thước bao nhiêu byte. `Flag` là cờ quyền, `Lk` trỏ đến 1 section khác (nếu cần). `Inf` chứa thêm thông tin tùy thuộc vào section. `Al` dùng để căn chỉnh địa chỉ section.

*4. ELF64.*

ELF64 có cấu trúc gần như tương tự như ELF32. Một số điểm khác biệt lớn đó là: Magic byte trên Program Header, và kích thước các trường dữ liệu được mở rộng lên 64 bit...

*5. Quá trình nạp chương trình lên RAM.*

Đầu tiên, kernel đọc ELF Header, kiểm tra magic bytes có đúng là `7F 45 4C 46` không, đọc `e_machine` để kiểm tra tương thích kiến trúc CPU, đọc `e_type` để xác định loại file (executable hay shared library), và đọc `e_entry` để biết địa chỉ Entry Point.

Khác với PE, kernel không dựa vào Section Headers mà dựa vào`Program Headers` để load. Kernel duyệt qua từng Program Header, chỉ load các segment có type là `PT_LOAD` lên RAM bằng `mmap()` — tương tự PE, đây cũng là demand paging, tức là chỉ tạo mapping trước, chưa thực sự đọc dữ liệu từ đĩa, khi CPU truy cập vào địa chỉ nào mới xảy ra page fault và kernel mới load trang đó lên. Địa chỉ load dựa vào `p_vaddr`, căn chỉnh theo `p_align`, phân quyền theo `p_flags` (R/W/X).

Nếu file có segment `PT_INTERP`, kernel sẽ load thêm dynamic linker (`ld-linux.so`). Dynamic linker đọc `PT_DYNAMIC` để tìm các shared library cần thiết, load chúng lên RAM, resolve địa chỉ thực của từng symbol rồi ghi vào GOT — tương tự IAT của PE. Cuối cùng, dynamic linker nhảy vào `e_entry` để bắt đầu thực thi.


*6. Bài tập.*

Đầu tiên, kiểm tra chương tình bằng lệnh `file`.

![](../ảnh/Pasted%20image%2020260517085131.png)

Đây là file elf32, không có program header và section header.

Ta sẽ dùng hexedit để thử so sánh 2 file cùng format elf32 (test và prob).

![](../ảnh/Pasted%20image%2020260517092743.png)

File bên trái là file test, bên phải là prob. Bắt đầu từ byte thứ 18, 2 file đã có sự khác biệt: Nếu theo chuẩn ELF32, thì byte 28 (0x1c) đến byte 31 (0x1f) là của trường thông tin `e_phoff` (`e_ident`: 16 bytes,  `e_type`:  2 bytes, `e_machine`: 2 bytes, `e_version`: 4 bytes, `e_entry`: 4 bytes), trong khi đấy ở file prob, từ byte 28 đến 31 toàn bộ đều là 00, nghĩa là vùng này đang nằm ở trường dữ liệu phía trước nó. Trong ELF64, kích thước các trường dữ liệu trước `e_phoff` là:`e_ident`: 16 bytes,  `e_type`:  2 bytes, `e_machine`: 2 bytes, `e_version`: 4 bytes, `e_entry`: 8 bytes, nên file này khả năng cao là file ELF64. Ngoài ra địa chỉ offset của program header trong trường `e_phoff` là 0x40, nghĩa là 64 bytes, đây cũng là chuẩn của ELF64, điều này càng khẳng định giả định trên. Ta sẽ sửa thử byte ở thứ 5 tính từ đầu file thành 02 (là magic byte của ELF64) rồi kiểm tra lại.

![](../ảnh/Pasted%20image%2020260517094204.png)

![](../ảnh/Pasted%20image%2020260517094231.png)

File đã được khôi phục. Dùng IDA để phần tích.
```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  unsigned __int64 count; // [rsp+0h] [rbp-C0h]
  __int64 v5; // [rsp+10h] [rbp-B0h]
  _QWORD v6[3]; // [rsp+18h] [rbp-A8h]
  char input_data[136]; // [rsp+30h] [rbp-90h] BYREF
  unsigned __int64 v8; // [rsp+B8h] [rbp-8h]

  v8 = __readfsqword(0x28u);
  v5 = 0x467774475B8E5B57LL;
  v6[0] = 0x8388858543568685LL;
  *(_QWORD *)((char *)v6 + 5) = 0x9081824487838885LL;
  printf("Flag -> ");
  if ( !fgets(input_data, 128, _bss_start) )
    return 1;
  input_data[strcspn(input_data, "\n")] = 0;
  if ( strlen(input_data) == 21 )
  {
    for ( count = 0LL; count < 21; ++count )
    {
      if ( *((unsigned __int8 *)&v6[-1] + count) - 19 != (unsigned __int8)input_data[count] )
      {
        puts("Acces denied.");
        return 1;
      }
    }
    puts("Access granted!");
    return 0;
  }
  else
  {
    puts("[-] Incorrect Lenght.");
    return 1;
  }
}
```
Cụm lệnh:
```c
v5 = 0x467774475B8E5B57LL;
v6[0] = 0x8388858543568685LL;
*(_QWORD *)((char *)v6 + 5) = 0x9081824487838885LL;
```
Tạo ra một vùng dữ liệu 152 bits, cấu trúc như sau:

![](../ảnh/Pasted%20image%2020260517102419.png)

Sau đó lấy từng byte trong khối dữ liệu, từ đi 19 rồi so sánh với từng kí tự trong chuỗi nhập.

Code giải mã:
```python
data = 0x467774475B8E5B57 | (0x8388858543568685 << 64) | (0x9081824487838885 << 64 + 32 + 8)
data_bytes = data.to_bytes(64*3, byteorder='little')


text = ''
char = 0
for count in range(0, 21):
	char = (data_bytes[count] - 19) & 0xff 
	text += chr(char)

print(text)
```
Flag: DH{H4ad3rsC0rrupt1on}

![](../ảnh/Pasted%20image%2020260517102540.png)
