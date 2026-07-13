**Linking (liên kết)** là quá trình gom các mảnh code và dữ liệu để tạo thành 1 file có thể load vào bộ nhớ để thực thi. Quá trình liên kết có thể diễn ra ở thời điểm ==Biên dịch==, khi mà mã nguồn được dịch thành mã máy, có thể ở thời điểm ==Nạp==, khi file chương trình được nạp lên bộ nhớ (được thực thi bởi ==Loader==). Hoặc là khi ==Chạy== (được thực thi bởi chương trình ứng dụng). Với các hệ điều hành hiện đại, **Linking** được tự động hóa bởi các ==Trình liên kết (Linkers).==
![[Pasted image 20260629163709.png]]

**Linkers** đóng vai trò quan trọng trong phát triển phần mềm vì nó cho phép ==Seperate compilation==, nghĩa là thay vì tổ chức chương trình theo cấu trúc nguyên khối, ta có thể chia nhỏ ra thành các ==Module==, chúng có thể được sửa đổi và biên dịch độc lập với nhau. Khi chỉnh sửa 1 ==Module==, ta chỉ cần liên kết và biên dịch lại nó, thay vì phải liên kết và biên dịch lại toàn bộ chương trình.
![[Pasted image 20260629164600.png]]

*1. Compiler Driver (Trình điều khiển biên dịch).*
Hầu hết các hệ thống biên dịch đều cung cấp ==Compiler driver==, nó gọi đến các bộ ==tiền xử lí ngôn ngữ (Language Preprocessor)==, ==trình biên dịch (Compiler)==, và ==trình liên kết (Linker)==, theo nhu cầu của người dùng. Ví dụ, muốn build 1 chương trình C bằng hệ thống biên dịch ==GNU==, chúng ta phải gọi đến trình điều khiển biên dịch ==GCC== bằng lệnh `gcc file.c -o file`.
![[Pasted image 20260629170011.png]]

*Hình 7.2* mô tả quá trình biên dịch file code thành file đối tượng thực thi (trong ví dụ của *hình 7.1*).
![[Pasted image 20260629170220.png]]
- Đầu tiên, driver gọi đến ==C preprocessor (cpp)== để biên dịch file `main.c` thành file trung gian `main.i` 
  `cpp [other arguments] main.c /tmp/main.i`
- Tiếp theo, driver gọi đến ==C compiler (cc1)== để biên dịch file `main.i` thành file hợp ngữ `main.s`  
  `cc1 /tmp/main.i -Og [other arguments] -o /tmp/main.s`
- Sau đó, driver gọi đến ==Assembler (as)== để biên dịch file `main.s` thành file ==đối tượng nhị phân tái định vị (binary relocate object file)== `main.o`.
  `as [other arguments] -o /tmp/main.o /tmp/main.s`
- Driver cũng thực hiện tương tự với file `sum.c`. Sau khi có file main.o và sum.o, ==Linker== sẽ ghép nối 2 file, cùng với các file hệ thống cần thiết khác, để tạo ra file ==đối tượng thực thi (executale object file)==, tên là `prog`.
  `ld -o prog [system object files and args] /tmp/main.o /tmp/sum.o`
- Để chạy file, gõ `./prog` trên Terminal. ![[Pasted image 20260629173417.png]]
- Linux shell sẽ gọi đến 1 chương trình hệ thống gọi là ==Loader==. Nhiệm vụ của nó là sao chép code và dữ liệu trong file thực thi vào bộ nhớ, và chuyển quyền điều khiển vào vị trí bắt đầu của chương trình.

*2. Static Linking (liên kết tĩnh).*
Các ==trình liên kết tĩnh (Static Linkers)== như ==Linux LD== nhận đầu vào là các file ==đối tượng tái định vị== và các ==tham số dòng lệnh== để sinh ra đầu ra là 1 ==chương trình đối tượng thực thi được liên kết đầy đủ==, có thể load và chạy được.
Các file đối tượng đầu vào được tạo thành từ nhiều các ==section== dữ liệu và code, mỗi ==section== là một chuỗi các byte liên tục. Các lệnh ở trong 1 ==section==, các biến khởi tạo toàn cục nằm trong 1 ==section== khác, và các biến chưa được khởi tạo lại nằm trong 1 ==section== khác nữa...
Để build được 1 file thực thi, ==Linker== cần làm 2 việc chính:
- **Phân giải kí hiệu (Symbol Resolution):** Các file đối tượng định nghĩa và tham chiếu các ==Symbol==, mỗi ==Symbol== là tên của 1 hàm, 1 biến... ==Định nghĩa symbol== chính là chỉ đến nơi mà ==symbol== đó được cấp phát bộ nhớ. Còn ==tham chiếu symbol== là những nơi mà nó được gọi. Nhiệm vụ của việc phân giải là tìm địa chỉ định nghĩa ==symbol== đó, để gán vào những nơi tham chiếu ==symbol==.![[Pasted image 20260629175001.png]]
- **Tái định vị (Relocation):** ==Trình biên dịch (Compiler)== và ==trình hợp dịch (Assembler)== có nhiệm vụ sinh ra các section code và dữ liệu bắt đầu từ địa chỉ 0. ==Linker== tái định vị chúng bằng cách gắn mỗi ==địa chỉ section== với 1 ==định nghĩa symbol==. Sau đó chỉnh sửa tất cả các ==tham chiếu symbol== thành địa chỉ trỏ đến vùng nhớ của ==symbol== đó. ==Linker== thực hiện việc này thông qua các ==lệnh thông== tin do ==Assembler== cung cấp. Chúng được gọi là ==Chỉ mục (relocation entry)==, chứa thông tin về địa chỉ, cùng 1 số thông tin khác phục vụ cho việc tái định vị.

*3. Object file (file đối tượng).*
==Object file== có 3 loại:
- ==Relocatable object file:== Chứa mã nhị phân và dữ liệu. Các file này có thể kêt hợp với nhau tại thời điểm biên dịch để tạo ra file ==Executable object file.==
- ==Executable object file:== Chứa mã nhị phân và dữ liệu ở dạng có thể copy trực tiếp vào bộ nhớ để thực thi.
- ==Shared object file:== Một dạng đặc biệt của ==Relocatable object file==. Nó có thể được load vào bộ nhớ và liên kết động (nghĩa là chương trình sẽ gọi nó khi cần thay vì ghép trực tiếp vào file thực thi), ở cả load time và run time.
Compilers và assembler tạo ra ==Relocatable object file== (kể cả ==Shared object file==). Linkers tạo ra ==Executable object file==. Về mặt kỹ thuật, một ==Object module== là một chuỗi các byte liên tục, và ==Object file== là 1 ==Object module== được lưu trên đĩa thành 1 file.
1 ==Object file== được tổ chức dựa trên ==Object file format== (mỗi hệ điều hành có 1 format khác nhau). Hệ điều hành Unix sử dụng format `a.out`, Windows dùng PE, Linux dùng ELF... Mặc dù tài liệu này chỉ tập chung về file ELF, các khái niệm này đối với các format khác cũng tương tự nhau.

*4. Relocatable Object file (File đối tượng tái định vị).*
![[Pasted image 20260630165534.png]]

![[Pasted image 20260630164844.png]]
Trong hình là cấu trúc của 1 ==ELF Relocatable object file== cơ bản **(chi tiết nằm trong file khác, ở đây sẽ không dịch thêm).**

*5. Symbol và Synbol Table.*
Mỗi ==Relocatable object module==, `m`, chứa 1 ==Symbol table== bao gồm các thông tin về các module được định nghĩa và tham chiếu bởi `m`. Trong ngữ cảnh của 1 Linker, có 3 loại symbols:
- ==Global symbol:== Được định nghĩa bởi module `m` và có thể được tham chiếu bởi các module khác. ==Global symbol== tương ứng với các hàm được khai báo `nonstatic` và các biến toàn cục.
- ==External symbol:== Là các ==Global symbol== được tham chiếu bởi module `m` nhưng lại được định nghĩa bởi một module khác. ==External symbol== tương ứng với các hàm `nonstatic` và các biến toàn cục nhưng được khai báo ở module khác.
- ==Local symbol:== Được định nghĩa và tham chiếu duy nhất bởi module `m`. Nó tương ứng với các hàm `static` trong C và các biến toàn cục được khai báo bằng `static`. Các symbol này có thể được nhìn thấy từ bất kì đâu trong nội bộ module `m`, nhưng không module nào khác có thể tham chiếu nó.
Cần phân biệt rõ ràng rằng ==Local symbol== khác với ==Local variable==. Section ==.symtab (Symbol table)== không chứa bất kì một biến cục bộ, nonstatic nào. Chúng được quản lí bằng stack khi chạy và không liên quan gì đến linker.
Ngoài ra, các biến cục bộ được khai báo bằng `static` lại không được quản lí bởi stack. Trình biên dịch sẽ cấp phát bộ nhớ cho chúng ở trong section `.bss` và `.data` với mỗi 1 định nghĩa, và tạo ra các ==Local symbol== trong `.symtab` với các tên đặc biệt. 
![[Pasted image 20260630172135.png]]
Như ví dụ trong hình, 2 biến `x` được khai báo cục bộ trong 2 hàm khác nhau với thuộc tính `static`. Trong trường hợp này, Compiler sẽ tạo ra 2 ==Local symbol== với tên khác nhau. VD, nó sẽ dùng `x.1` cho biến `x` trong hàm `f()` và `x.2` cho biến `x` trong hàm `g()`.
![[Pasted image 20260630173810.png]]
VD:
```c
#include <stdio.h>

static int g_static = 100; // STATIC TOÀN CỤC: Chỉ file này dùng được. Sống vĩnh viễn (.data).
int g_normal = 200;        // NON-STATIC TOÀN CỤC: File khác dùng ké được. Sống vĩnh viễn (.data).

void test() {
    static int l_static = 0; // STATIC CỤC BỘ: Giữ nguyên giá trị sau khi thoát hàm. Sống vĩnh viễn (.data).
    int l_normal = 0;        // NON-STATIC CỤC BỘ: Reset về 0 mỗi khi vào hàm. Sống tạm thời (Stack).

    l_static++;
    l_normal++;
    printf("Static: %d | Normal: %d\n", l_static, l_normal);
}

int main() {
    test(); // In ra: Static: 1 | Normal: 1
    test(); // In ra: Static: 2 | Normal: 1
    test(); // In ra: Static: 3 | Normal: 1
    return 0;
}
```
==Symbol table== được tạo ra bới Assembler, sử dụng các symbol được Compiler xuất ra trong file hợp ngữ `.s`. 1 ==ELF symbol table== được lưu trong section `.symtab`. Nó chứa 1 mảng các chỉ mục. Hình 7.4 cho ta thấy định dạng của mỗi chỉ mục.
![[Pasted image 20260630174032.png]]
Mỗi chỉ mục được tổ chức thành 1 cấu trúc với các trường thông tin. 
- `name`: chứa địa chỉ offset trỏ đến tên symbol trong ==String table (.strtab)==. 
- `value` là địa chỉ trỏ đến symbol. Với ==Relocatable object file==, nó là địa chỉ offset so với đầu section chỉ đến nơi symbol được định nghĩa. Còn với ==Executable object file==, nó chính là địa chỉ tuyệt đối trỏ đến nơi symbol đưuọc định nghĩa trong bộ nhớ.![[Pasted image 20260630175202.png]]
- `size` là kích thước của object (là đối tượng được định nghĩa là symbol) đó. ![[Pasted image 20260630180332.png]]
- `type` quy định symbol này định nghĩa 1 hàm, dữ liệu, section...
- `binding` cho biết symbol là local hay global.
- `section` trỏ vào bảng ==Section header table==, cho biết symbol đó đang nằm trong section nào.
==Symbol table== có thể chứa cả chỉ mục đến các section hoặc đường dẫn đến file nguồn gốc. ![[Pasted image 20260630180621.png]]
Mỗi ==symbol== được gán (định nghĩa, tham chiếu) trong nhiều ==section== của 1 file đối tượng, và nó được biểu thị bằng trường `section`, nó chứa chỉ số của ==section== đó trong ==section header table==. Có 3 loại ==pseudosections (giả section)== không có chỉ mục trong section header table:
- ==ABS==: cho các symbol không được cho phép tái định vị.  
- ==UNDEF==: cho các symbol được tham chiếu trong file đối tượng, nhưng được định nghĩa trong file khác.
- ==COMMON==: cho các đối tượng dữ liệu chưa được khởi tạo, nhưng được định nghĩa ở đâu đó trong file đối tượng.
Cần chú ý rằng, ==pseudosections== chỉ có trong file đối tượng tái định vị, chứ không có trong file đối tượng thực thi.
Giữa pseudo section ==COMMON== và section`.bss` có nhiều điểm tương đồng nhất định. Các phiên bản hiện đại của GCC gán symbol trong các file tái định vị cho  ==COMMON== và `.bss` bằng cách sử dụng quy tắc sau:
- ==COMMON:== cho các biến toàn cục chưa khởi tạo.
- `.bss`: cho các biến static chưa khởi tạo, và các biến toàn cục hoặc static được khởi tạo bằng 0.
`READELF` là một công cụ hữu ích trên linux để xem nội dung của file đối tượng. Ví dụ, hình dưới là 3 chỉ mục cuối cùng trong symbol table của 1 file đối tượng tái định vị `main.o`. 8 chỉ mục đầu tiên, chúng không được hiển thị, là các chỉ mục được linker sử dụng nội bộ.
![[Pasted image 20260707161356.png]]

***Bài tập 7.1:*** Chú ý đến module `m.o` và `swap.o` trong hình 7.5. Với mỗi symbol được định nghĩa hoặc tham chiếu trong `swap.o`, chỉ ra liệu nó có một chỉ mục trong section `.symtab` trong module `swap.o`. Nếu có, chỉ ra module định nghĩa symbol đó (`swap.o` hay `m.o`), loại symbol (local, global, hoặc extern), và section (`.text`, `.data`, `.bss` hoặc `COMMON`) mà nó được gán trong module.
![[Pasted image 20260707162336.png]]
![[Pasted image 20260707163203.png]]
***Giải:***
Đầu tiên, đọc logic chương trình:
`m.o`:
- Đầu tiên, nó định nghĩa một nguyên mẫu hàm swap(). Nội dung của hàm đó nằm ở trong file `swap.o`.
- Tiếp đó, nó định nghĩa 1 mảng kiểu `int`, tên là `buf` với 2 phần tử: 1 và 2.
- Sau đó nó định nghĩa hàm `main()`, trong hàm main gọi đến hàm `swap()`. Sau khi thực thi xong hàm `swap()` thì trả về 0.
`swap.o`:
- Đầu tiên, nó khai báo mảng `buf` (mảng này được định nghĩa ở bên file `main.o`).
- Tiếp đó, nó định nghĩa 1 con trỏ kiểu `int`, trỏ đến địa chỉ của phần tử đầu tiên của mảng `buf`.
- Tiếp đến, nó định nghĩa thêm 1 con trỏ kiểu int `bufp1`.
- Cuối cùng, nó định nghĩa hàm `swap()`, đầu tiên, nó khai báo biến `int` tên là `temp`. Tiếp đến nó gán địa chỉ của phần tử thứ 2 trong mảng `buf` cho con trỏ `bufp1`, sao chép giá trị của phần tử đầu tiên vào biến `temp`. Sau đó, phần tử đầu tiên sẽ được thay đổi giá trị thành giá trị của phần tử thứ 2. Cuối cùng gán lại giá trị của phần tử thứ 2 thành giá trị của biến `temp` (chinh là giá trị của phần tử đầu tiên).
Kết quả (bảng).
![[Pasted image 20260707165909.png]]
Giải thích:
- `buf` chỉ được tham chiếu, nên là symbol dạng extern, section sẽ là `UNDEF`, còn nơi định nghĩa là `m.o`.
- `bufp0` được định nghĩa và gán giá trị cụ thể, nên nằm ở `.data`, và là global.
- `bufp1` được định nghĩa, nhưng chưa được gán giá trị. Nhìn lại bên trên, nó sẽ nằm ở `COMMON`.
- `swap` được định nghĩa, là hàm nên nằm ở `.text`, là global.

*7.6. Phân giải symbol (Symbol Resolution).*
Linker phân giải các tham chiếu bằng cách liên kết mỗi tham chiếu với chính xác 1 định nghĩa symbol duy nhất từ symbol table nằm trong file tái định vị. Việc phân giải symbol rất đơn giản đối với những tham chiêu đến các symbol cục bộ, được định nghĩa trong cùng module với tham chiếu. Compiler cho phép 1 định nghĩa duy nhất với mỗi symbol cục bộ trong mỗi module. Compiler cũng đảm bảo rằng các biến static cục bộ, phải có tên duy nhất. 
Phân giải các tham chiếu đến các global symbal phức tạp hơn 1 chút. khi compiler gặp 1 symbol (tên biến hoặc tên hàm) chưa được định nghĩa trong module, nó sẽ cho rằng symbol đó đã được định nghĩa trong module khác, tạo ra 1 chỉ mục trong symbol table (UNDEF), và để cho linker xử lí. Nếu linker không thể tìm thấy định nghĩa cho tham chiếu symbol đó. Nó sẽ báo lỗi. Ví dụ, nếu ta thử biên dịch và liên kết file nguồn dưới đây trên máy linux.
![[Pasted image 20260707203551.png]]
Compiler sẽ chạy mà không có lỗi, nhưng linker sẽ báo lỗi khi nó không thể phân giải symbol `foo`.
![[Pasted image 20260707203636.png]]
Ngoài ra, việc phân giải các global symbol còn phức tạp bởi vì nhiều module có thể định nghĩa các symbol khác nhau với cùng 1 tên. Trong trường hợp này, linker phải báo lỗi hoặc chọn 1 trong số các định nghĩa, đồng thời bỏ qua các định nghĩa còn lại. Phương pháp được áp dụng bởi các hệ thống linux đòi hỏi sự hợp tác giữa compiler, assembler, linker; đôi khi nó còn dẫn đến các lỗi cực kì khó hiểu cho các lập trình viên.
**7.6.1** Cách linker phân giải việc trùng lặp tên symbol.
Đầu vào của linker là một tập hợp các file tái định vị. Mỗi module định nghĩa một tập các symbol. Vài trong số đó là cục bộ, và một vài là toàn cục. Điều gì sẽ xảy ra nếu một vài module cùng định nghĩa các symbol toàn cục với cùng 1 tên? Dưới đây là các mà hệ thống Linux giải quyết.
Ở thời điểm biên dịch, compiler sẽ thêm thông tin về global symbol là mạnh hay yếu cho assembler. Và assembler sẽ mã hóa thông tin đó, đưa vào symbol table. Các hàm và tên biến đã khởi tạo được coi là mạnh, tên biến chưa khởi tạo được coi là yếu. Từ yếu tố trên, Linux giải quyết dựa trên luật sau:
- Không cho phép các symbol mạnh có cùng tên.
- Nếu cùng lúc có 1 mạnh và nhiều yếu có cùng tên -> chọn mạnh.
- Nếu nhiều yếu có cùng tên, chọn 1 trong số đó.
Ví dụ, chúng ta sẽ thử biên dịch và liên kết 2 module trong hình.
![[Pasted image 20260707205221.png|473]]
Trong trường hợp này, linker sẽ báo lỗi vì symbol mạnh được định nghĩa 2 lần.
![[Pasted image 20260707205303.png]]
Tương tự, linker cũng sẽ báo lỗi trong trương hợp dưới vì symbol mạnh `x` được định nghĩa 2 lần.
![[Pasted image 20260707205311.png]]
Nếu x là biến chưa được khởi tạo trong 1 module, linker sẽ chọn symbol mạnh khác đã được định nghĩa.
![[Pasted image 20260707205507.png]]
Khi chạy, hàm f thay đổi giá trị của biến x từ 15213 thành 15212, điều này sẽ dẫn đến kết quả không giống với mong muốn của người viết. Chú ý rằng linker không thông báo rằng nó đã phát hiện nhiều định nghĩa của `x`.
![[Pasted image 20260707205635.png]]
Điều tương tự cũng có thể xảy ra nếu có 2 định nghĩa yếu của `x`.
![[Pasted image 20260707205728.png]]
Việc áp dụng luật 2 và 3 có thể dẫn đến một số lỗi ngầm khi chạy, kể cả khi các symbol trùng tên có khác kiểu dữ liệu. Xem ví dụ dưới đây, x được định nghĩa là `int` ở 1 module và `double` ở một module khác.
![[Pasted image 20260707205929.png]]
![[Pasted image 20260707205935.png]]
Trên x86-64 Linux, `double` là 8 bytes và `int` là 4 byte. Ở hệ thống trong ví dụ, địa chỉ của `x` là `0x601020` và địa chỉ của `y` là `0x601024`. Tuy nhiên, việc đinh nghĩa `x = -0.0` sẽ ghi đè lên bộ nhớ của `y`.
![[Pasted image 20260707212628.png]]
Đây là một lỗi rất tinh vi, bời vì nó chỉ có 1 cảnh báo từ phía linker, và nó chỉ báo muộn tại vị trí cách xa so với nơi mà lỗi xảy ra. Trong một hệ thống lớn, các lỗi kiểu này rất khó để sửa....
Trong phần *7.5* chúng ta đã được thấy cách mà compler gắn symbols vào `COMMON` và `.bss`. Thật ra, quy tắc này là do một vài trường hợp, linker cho phép các module định nghĩa symbol với cùng tên. Khi compiler dịch các module và bắt gặp 1 symbol yếu (giả sử là `x`), nó không biết rằng các module khác có định nghĩa `x` không, và nếu có thì nó cũng không thể dự đoán được linker sẽ chọn định nghĩa nào trong số các định nghĩa của `x`. Nên compiler hoãn lại việc quyết định cho linker bằng cách gắn `x` vào `COMMON`. Mặt khác, nếu `x` được khởi tạo bằng 0, nó sẽ trở thành symbol mạnh (và sẽ phải là tên duy nhất theo luật số 2), nên compiler có thể gắn nó vào `.bss`. Tương tự, static symbol vốn đã là duy nhất nhờ vào bản chất khai báo của chúng. Nên compiler có thể gắn nó vào `.data` hay `.bss`.

***Bài tập 7.2.*** Trong bài tập này, cho rằng `REF(x.i)` -> `DEF(x.k)` biểu thi cho việc linker sẽ kết nối 1 tham chiếu của symbol `x` trong module `i` với định nghĩa của `x` trong module `k`. Với mỗi ví dụ dưới đây, sử dụng công thức trên để chỉ ra cách linker sẽ phân giải tham chiếu cho một symbol được định nghĩa nhiều lần trong mỗi module. Nếu có lỗi, viết "lỗi". Nếu linker chọn 1  trong số các định nghĩa, viết "Unknown".
![[Pasted image 20260707215550.png]]
a) `REF(main.1)` -> `DEF(main.1)`
b) `REF(main.2)` -> `DEF(main.1)`
==Giải thích:== main trong module 1 là tên hàm -> manh, trong module 2 là tên biến chưa khởi tạo -> yếu. Yếu + mạnh -> lấy mạnh.
![[Pasted image 20260707215817.png]]
Lỗi.
==Giải thích:== 2 mạnh -> lỗi.
![[Pasted image 20260707215923.png]]
a) `REF(x.1)` -> `DEF(x.2)`
b) `REF(x.1)` -> `DEF(x.2)`
==Giải thích== x1 yếu, x2 mạnh -> mạnh.

**7.6.2.** Liên kết với các thư viện tĩnh.
Trước đó, chúng ta đã công nhận rằng linker đọc một tập các file tái định vị và liên kết chúng vào 1 file thực thi đầu ra. Trong thực tế, tất cả các hệ thống biên dịch cung cấp một cơ chế để đóng gói các module liên quan vào 1 file gọi là ==thư viện tĩnh (static library)==, nó có thể làm đầu vào cho linker. Khi linker xây dựng file thực thi, nó chỉ sao chép các module có trong thư viện mà được tham chiếu trong chương trình.
Vì sao hệ thống lại hỗ trợ khai niệm thư viện? Nhìn vào chuẩn ISO C99, nó định nghĩa ra rất nhiều chuẩn I/O, xử lí chuỗi, và các hàm toán họa với số nguyên như `atoi`, `scanf`, `strcpy`... Chúng có thể được sử dụng với tất cả các file chương trình C trong thư viện ==libc.a==. ==ISO C99== còn định nghĩa các hàm tính toán với số thực như `sin`, `cos`... trong thư viện ==libm.a==.
![[Pasted image 20260708082800.png]]
Có nhiều cách khác nhau để nhà phát triển sử dụng để cung cấp các hàm cho người dùng mà không có sự hỗ trợ của thư viện tĩnh. Một phương pháp đó là yêu cầu compiler nhận ra các lệnh gọi hàm chuản và sinh ra mã phù hợp một cách trực tiếp. Pascal, cung cấp một tập nhỏ các hàm tiêu chuẩn, dùng phương pháp này. Nhưng nó sẽ không phù hợp với C, vì C có một số lượng lớn các hàm tiêu chuẩn được định nghĩa theo chuẩn C. Nó sẽ tạo ra một sự phức tạp đáng kể chop compiler và cần cập nhật compiler mỗi khi có một hàm mới được thêm vào. Tuy vậy, đối với người lập trình ứng dụng, cách này lại tương đối tiện lợi vì các hàm chuẩn sẽ luôn sẵn sàng.
Một cách tiếp cận khác đó là đưa toàn bộ các hàm chuẩn C vào 1 file tái định vị khác, gọi là ==libc.o==, mà lập trình viên ứng dụng có thể liên kết vào file thực thi.
![[Pasted image 20260708084006.png]]
Cách này có ưu điểm là nó sẽ tách rời việc triển khai các hàm tiêu chuẩn khỏi việc trển khai của compiler, và vẫn tiện lợi với người lập trình. Tuy nhiên, một bất lợi to lớn đó là mọi file trong hệ thống cần có một bản sao hoàn chỉnh của các hàm tiêu chuẩn. Điều này gây ra lãng phí tài nguyên. Tệ hơn, mỗi lần chạy, chương trình cần có một bản sao của các hàm đó bên trong bộ nhớ. Một điểm bất lợi khác đó là mọi sự thay đổi với các hàm tiêu chuẩn, dù là nhỏ nhất, đều cần người phát triên phải biên dịch lại file. Điều này rất tốn thời gian.
Chúng ta có thể giải quyết vấn đề đó bằng cách tạo ra nhiều file tái định vị độc lập, mỗi file cho 1 hàm chuẩn và lưu chúng trong một thư mục đặc biệt. Mặc dù vậy, cách này cần người lập trình hệ thống liên kết một cách rõ ràng các module được sử dụng vào file thưc thi của họ, điều này rất tốn thời gian và dễ gây sai sót.
![[Pasted image 20260708090757.png|637]]
Khái niệm về thư viện tĩnh được phát triển để giải quyết nhojwc điểm của tất cả các phương pháp trên. Các hàm liên quan sẽ được biên dịch vào các module độc lập, sau đó được đóng gói vào 1 file duy nhất. Chương trình ứng dụng có thể sử dụng các hàm được định nghĩa trong thư viện đó bằng cách chỉ định tên file đó trong command line. Ví dụ, chương trình sử dụng hàm từ thư viện ==C standard== và thư viện ==math== có thể biên dịch và liên kết bằng lệnh có dạng sau.
![[Pasted image 20260708091212.png]]
Tại thời điểm liên kết, linker chỉ cần copy các module được tham chiếu bởi chương trình, điều này giảm kích thước của file thực thi trên đĩa và trong bộ nhớ. Mặt khác, người lập trình chỉ cần khai báo tên của một vài file thư viện (thực tế, thư viên `libc.c` được driver biên dịch truyền trực tiếp vào linker, nên không cần khai báo).
Trên hệ thống Linux, các thư viện tĩnh được lưu trên đĩa ở dạng file nén. Một file nén là tập các file tái định vị gắn kết lại với nhau vào 1 file lớn, với phần header cho biết kích thước và địa chỉ của mỗi đối tượng trong file nén đó. File nén này có phần mở rộng là `.a`.
Để thảo luận về các thư viện chi tiết hơn, hãy xem xét cặp thủ tục xử lí vector trong ==hình 7.6==. Mỗi thủ tục được định nghĩa tròn module của chính nó, thể hiện một toán tử vector với 2 đầu vào và lưu đầu ra vào một vector khác. Mỗi thủ tục lưu lại số lần nó được gọi bằng cách tăng giá trị của 1 biến toàn cục (điều này sẽ hữu ích khi ta phân tích ý tưởng của mã độc lập vị trí trong phần *7.12*).
![[Pasted image 20260708093535.png]]
Để tạo thư viện tĩnh của 2 module, ta dùng lệnh `AR` như bên dưới.
![[Pasted image 20260708093610.png|473]]
Để sử dụng thư viện, chúng ta cần viết 1 chương trình như là `main2.c` trong hình 7.7.
![[Pasted image 20260708093817.png]]
Để tạo file thực thi, chúng ta cần biên dịch và liên kết file `main2.o` và `livector.a`
![[Pasted image 20260708094001.png]]
Sơ đồ quá trình liên kết như sau:
![[Pasted image 20260708095550.png]]
![[Pasted image 20260708100654.png]]Tham số `-static` cho driver biên dịch biết rằng linker phải build một file thực thi liên kết đầy đủ, có thể load vào bộ nhớ và chạy mà không cần liên kêt thêm tại load time.
**7.6.3.** Cách linker sử dụng static library để phân giải tham chiếu.
Static library rất hữu dụng, chũng cũng gây ra nhiều sự khó hiểu cho người lập trình vì cách mà Linux linker sử dụng static library để phân giải các tham chiếu bên ngoài. Trong giai đoạn phân giải symbol, linker scan các file tái định vị và lưu trữ từ trái sang phải theo thứ tự tuyến tính mà nó xuất hiện trên dòng lệnh của driver biên dịch (Driver tự động dịch các file `.c` trên dòng lệnh thành file `.o`).
![[Pasted image 20260708102706.png]]
![[Pasted image 20260708102811.png]]
![[Pasted image 20260708102733.png]]
Trong quá trình quét này, linker sẽ phân ra tập `E` các file tái định vị sẽ được kết hợp với nhau để tạo thành file thực thi, tập `U` các symbol chưa phân giải được (hay còn gọi là symbol được tham chiếu nhưng không tìm thấy định nghĩa), và tập `D` các symbol đã được định nghĩa trong các file input trước đó. Khi khởi tạo, `E`, `U`, `D` rỗng.
- Với mỗi input file `f` trong dòng lệnh, linker xem xét nếu `f` là 1 đối tượng, hay là một tệp nén. Nếu là đối tượng -> đưa vào `E`, cập nhật `U` và `D` để lấy thông tin về các symbol được định nghĩa và tham chiếu trong `f`, và chuyển đến file input tiếp theo.
- Nếu là file nén, linker thử ghép các symbol chưa được định nghĩa trong `U` với các định nghĩa có trong các đối tượng con của file nén. Nếu có đối tượng con `m` định nghĩa symbol trong `U` -> `m` được thêm vào `E`, linker sẽ cập nhật tiếp `U` và `D` để thêm các symbol có trong `m` vào. Còn các đối tượng con còn lại, không định nghĩa symbol nào có trong`U` thì sẽ bị linker bỏ qua và đi đến file input tiếp theo.
- Nếu `U` vẫn còn phần tử dù linker đã hoàn tất việc quét file đầu vào -> báo lỗi. Ngược lại, nó sẽ ghép nối và tái định vị cac sđối tượng có trong `E` để tạo ra file thực thi đầu ra.
Không may, thuật toán này có thể dẫn đến các lỗi link-time, vì thứ tự của các thư viện và file đối tượng trong dòng lệnh là quan trọng. Nếu thư việc định nghĩa symbol xuất hiện ở dòng lệnh trước đối tượng tham chiếu, tham chiếu sẽ không được phân giải và quá trình liên kết sẽ thất bại. Xem ví dụ dưới đây.
![[Pasted image 20260708104228.png]]
Điều gì đã xảy ra? Khi `libvector.a` được xử lí, `U` đang trống rỗng, nên không có đối tương con nào trong `libvector.a` được đưa vào `E`-> tham chiếu tới addvec có trong file `main2.c` sẽ không được phân giải -> báo lỗi.
Các thư viện có thể được lặp lại trong dòng lệnh để thõa mãn phụ thuộc. xem ví dụ dưới:
![[Pasted image 20260708104549.png]]
Ở đây, `foo.c` gọi 1 hàm ở `lix.a`, trong hàm đó lại gọi đến 1 hàm khác ở `liby.a`, và trong `liby.a` lại gọi đến 1 hàm ở `libx.a`. Tuy nhiên, chúng ta nên nối 2 file `libx.a` và `liby.a` thành 1 file duy nhất.
***Bài tập 7.3.*** Cho `a` và `b` chỉ đến các đối tương hoặc là thư viện tĩnh có trong thư mục, và cho `a -> b` chỉ đến việc `a` phụ thuộc vào `b`, hoặc nói cách khác `b` định nghĩa một symbol được tham chiếu trong `a`. Với mỗi ngữ cảnh dưới đây, viết lệnh biên dịch tối giản, có thể cho phép linker phân giải tất cả symbol.
![[Pasted image 20260708105055.png]]
==A.== `gcc -static p.o libx.a`
==B.== `gcc -static p.o libx.a liby.a`
==C.== `gcc - static p.o libx.a liby.a  libx.a`
***Giải thích câu C***.
- Theo quy tắc bên trên, với file tái định vị, thì sẽ mặc định được đưa vào `E`, còn file nén thì mới phải xem xét.
- file `p.o` phụ thuộc vào `libx.a`, nên chắc chắn sẽ là `p.o libx.a`.
- file `libx.a` lại phụ thuộc ngược vào `p.o`. Tuy nhiên toàn bộ file `p.o` đã nằm trong `E` sẵn rồi, nên không cần viết vào dòng lệnh nữa, lệnh vẫn là `p.o libx.a`.
- `libx.a` cũng phụ thuộc vào `liby.a` -> lệnh sẽ là `p.o libx.a liby.a`.
- `liby.a` phụ thuộc vào `libx.a`, khác với `p.o`, file `libx` khi này chỉ có 1 phần nằm trong `E`, nên vẫn cần nạp lại -> `p.o libx.a liby.a libx.a`. 
- `libx.a` lại phụ thuộc vào `p.o`, tương tự khi nãy -> `p.o libx.a liby.a libx.a`.
*7.7.* Tái định vị.
Khi linker hoàn thành bước phân giải symbol, nó đã kết nối mỗi tham chiếu symbol với 1 định nghĩa. Tại thời điểm này, linker biết chính xác kích thước của code và các section dữ liệu trong các module đầu vào. Nó đã sẵn sàn để bước vào giai đoạn tái định vị, nơi mà nó ghép nối các module đầu vào và gán địa chỉ runtime cho mỗi symbol. Tái định vị có thể chia làm 2 bước:
==1. Tái định vị section và các định nghĩa symbol==. Trong quá trình này, linker kết nối tất cả các section cùng kiểu vào 1 section tổng hợp mới. Ví dụ, tất cả section`.data` từ tất cả các module đàu vào sẽ ghép nối lại thành 1 section `.data` mới. Sau đó linker sẽ gán địa chỉ runtime cho section mới, cho mỗi section định nghĩa bởi các module đầu vào, và cho mỗi symbol định nghĩa bởi module đầu vào. Khi bước này hoàn tất, mỗi lệnh và biến toàn cục của chương trình đều có 1 địa chỉ runtime riêng.
==2. Tái định vị tham chiếu symbol bên trong section.== Trong quá trình này, linker chỉnh sửa các tham chiếu symbol trong code và data section để chúng trỏ đến đúng địa chỉ runtime mà symbol đó được định nghĩa. Để thực hiện việc này, linker dựa vào 1 cấu trúc dữ liệu nằm bên trong đối tượng tái định vị, gọi là ==relocation entries==, sẽ được thảo luận sau đây.
**7.7.1.** Chỉ mục tái định vị (relocation entries).
Khi assembler tạo ra 1 module đối tượng, nó không biết nơi nào code và dữ liệu sẽ được lưu trữ trên bộ nhớ, cũng không biết được vị trỉ của các symbol bên ngoài được module tham chiếu. Do đó mỗi khi assembler gặp 1 tham chiếu đến các đối tượng mà không biết địa chỉ gốc của nó, nó tạo ra 1 ==chỉ mục tái định vị== để nói cho linker biết cách để chỉnh sửa tham chiếu khi ghép nối các đối tượng tạo thành file thực thi. ==Chỉ mục tái định vị== cho code nằm trong `.rel.text`, còn cho dữu liệu nằm trong `.rel.data`.
==Hình 7.9== cho biết cấu trúc của 1 ==chỉ mục tái định vị của file ELF==.
![[Pasted image 20260708153338.png]]
- `offset` là độ lệch tính từ đầu section chứa tham chiếu symbol sẽ được tái định vị.
- `symbol` xác đinh symbol mà tham chiếu sau khi sửa sẽ chỉ tới.
- `type` báo cho linker cách sửa tham chiếu.
- `adden` là một hằng số có dấu, được sử dụng bởi một vài kiểu chỉ mục tái định vị để tạo độ lệch giá trị của tham chiếu được sửa đổi.
ELF định nghĩa 32 kiểu chỉ mục tái định vị khác nhau, một số trông khác phức tạp. Chúng ta chỉ cần quan tấm đến 2 loại cơ bản nhất: 
- `R_X86_64_PC32`: Tái định vị một tham chiếu sử dụng địa chỉ tương đối so với thanh ghi PC 32 bit. Khi CPU thực thi 1 lệnh sử dụng địa chỉ tương đối so với PC, nó tạo ra địa chỉ hiệu dụng bằng cách cộng giá trị 32 bit được mã hóa trong lệnh đó với giá trị thời gian chạy hiện tại của PC, mà giá trị này luôn là địa chỉ tiếp theo của lệnh trong bộ nhớ.![[Pasted image 20260708154911.png]]![[Pasted image 20260708154926.png]]![[Pasted image 20260708154936.png]]![[Pasted image 20260708160019.png]]![[Pasted image 20260708160038.png]]![[Pasted image 20260708160050.png]]
- `R_X86_64_32`: Tái định vị 1 tham chiếu sử dụng địa chỉ tuyệt đối 32 bit. Với địa chỉ tuyệt đối, CPU sử dụng trực tiếp 32 bit được mã hóa trong lệnh như là địa chỉ hiệu dụng, mà không cần chỉnh sửa gì thêm.
2 loại chỉ mục tái định vị trên hỗ trợ ==x86-64 small code model==, là cho rằng tổng dung lượng của code và dữ liệu trong file thực thi nhỏ hơn 2gb, cho nên có thể truy cập thông qua địa chỉ 32 bit. ==Small code model== là mặc định của GCC. Chương trình lớn hơn 2GB có thể được biên dịch sử dụng `-mcmodel=medium` (medium code model) hoặc `mcmodel=large` (large code model), nhưng chúng ta sẽ không thảo luận ở đây.
**7.7.2.** Tái định vị tham chiếu symbol.
 Hình ==7.10== cho biết mã giải của thuật toán tái định vị của linker. Dòng 1 và 2 duyệt qua mỗi section `s` và mỗi chỉ mục tái định vị `r` được kết nối với mỗi section. Để chắc chắn, cho rằng mỗi section `s` là một mảng các bytes và mỗi chỉ mục tái định vị `r` là một cấu trúc `Elf64_Rela`, như đã được định nghĩa trong hình ==7.9==. Ngoài ra, cho rằng khi thuật toán chạy, linker đã chon được địa chỉ runtime cho mỗi section (kí hiệu là `ADDR(s)`) và mỗi symbol (`ADDR(r.symbol)`). Dòng 3 tính toán địa chỉ của tham chiếu 4 byte cần tái định vị trong mảng. Nếu tham chiếu dùng chế độ địa chỉ tương đối qua PC, nó sẽ được tái định vị nhờ dòng 5-9. Nếu là địa chỉ tuyệt đối -> 11-13.
 ![[Pasted image 20260708161339.png|623]]
 Hãy xem cách linker sử dụng thuật toán này để tái định vị tham chiếu trong ví dụ chương trình trong hình ==7.11==. Hình 7.11 cho ta thấy mã hợp ngữ của file `main.o`, được tạo ra bằng lệnh`objdump -dx main.o`![[Pasted image 20260708161927.png]]
 Hàm `main` tham chiếu 2 symbol toàn cục: `array` và `sum`. Với mỗi tham chiếu, assembler tạo ra 1 chỉ mục tái định vị, được biểu diễn ở dòng 5 và 7. Chỉ mục tái định vị cho linker biết rằng tham chiếu tới `sum` dùng địa chỉ tương đối qua PC với hệ số `adden` là -0x4, còn tham chiếu tới `array` dùng địa chỉ tuyệt đối. Trong 2 phần kế tiếp sẽ cho biết cách linker tái định vị các tham chiếu này.
 ***Tái định vị địa chỉ tương đối qua PC.***
 Trong dòng 6 của hình ==7.11==, hàm `main` gọi hàm `sum`, được định nghĩa trong module `sum.o`. Lệnh `call` bắt đầu ở offset 0xe và gồm 1 byte opcode 0xe8, sau đó là một cụm placeholder cho tham chiếu địa chỉ tương đối qua thanh ghi 32 bit (chính là cụm `00 00 00 00`).
 4 thanh phần tương ứng của chỉ mục tái định vị `r` như sau:
 - `r.offset = 0xf`.
 - `r.symbol = sum`.
 - `r.type = R_X86_64_PC32`.
 - `r.addend = -4`.
Các trường thông tin trên cho linker biết cách để chỉ sửa tham chiếu bắt đâu từ địa chỉ `0xf` nên nó sẽ chỉ đến  thủ tục`sum` tại thời điểm chạy. Bây giờ, cho rằng linker công nhận điều này.
- `ADDR(s) = ADDR(.text) = 0x4004d0`.
- `ADDR(r.symbol) = ADDR(sum) = 0x4004e8`.
Sử dụng thuật toán trong hình ==7.10==, linker đầu tiên tính toán địa chỉ runime của tham chiếu (dòng 7):
```
refadr = ADDR(S) + r.offset
	   = 0x4004d0 + 0xf
	   = 0x4004df
```
Sau đó nó sẽ cập nhật tham chiếu sao cho nó sẽ chỉ đến thủ tục `sum` tại thời điểm chạy (dòng 8):
```
*refptr = (unsigned) (ADDR(r.symbol) + r.addend - refaddr)
        = (unsigned) (0x4004e8 + (-4) - 0x4004df)
        = (unsigned) (0x5) 
```
Trong kết quả ở file thực thi, lệnh `call` sẽ có dạng tái định vị sau.
```
4004de: e8 05 00 00 00 callq 4004e8 <sum>  ;sum()
```
Tại thời điểm chạy, lệnh `call` sẽ được định vị tại địa chỉ `0x4004de`. Khi CPU thực thi lệnh `call`, PC có giá trị 0x4004e3, là địa chỉ tuyệt đối của lệnh call. Để thực thi lệnh `call`, CPU sẽ thực hiên 2 bước:
- Đẩy địa chỉ trong PC lên stack.
- PC <- PC + 0x5 = 0x4004e8.
Sau đó, lệnh tiếp theo sẽ thực thi lệnh đầu tiên tại hàm `sum`.
***Tái định vị tham chiếu địa chỉ tuyệt đối.***
Tái định vị tham chiếu địa chỉ tuyệt đối đơn giản hơn. Ví dụ, dòng 4 trong hình ==7.11==, lệnh `mov` sao chép địa chỉ từ `arrray` (giá trị địa chỉ tuyệt đối  32 bit) vào thanh ghi `%edi`. Lệnh `mov` bắt đầu ở offset `0x9` và gồm opcode 1-byte 0xbf, theo sau là placeholder dành cho tham chiếu tuyệt đối 32 bit tuyệt đối đến `array`.
Các trường thông tin tương ứng bên trong chỉ mục tái định vị `r` gồm:
```
r.offset = 0xa
r.symbol = array
r.type = R_X86_64_32
r.addend = 0
```
Các trường thông tin này cho linker biết để sửa chữa địa chỉ tham chiếu tuyệt đối bắt đầu từ độ lệnh `0xa` nên nó sẽ chỉ đến byte đầu tiên của `array` tại thời điểm chạy. Bây giờ, cho rằng linker đã xác định rằng.
```
ADDR(r.symbol) = ADDR(array) = 0x601018
```
Linker sẽ cập nhật địa chỉ tham chiếu sử dụng dòng 13 của thuật toán trong hình ==7.10==:
```
*refptr = (unsigned) (ADDR(r.symbol) + r.addend)
        = (unsigned) (0x601018 + 0)
        = (unsigned) (0x601018)
```
Trong file thực thi kết quả, tham chiếu sẽ có dạng tái định vị như sau.
```
4004d9: bf 18 10 60 00 mov $0x601018, %edi ;%edi = &array
```
Tổng hợp lại tất cả, hình ==7.12== cho thấy 2 section đã được tái định vị `.text` và `.data` trong file thực thi. Tại load time, loader có thể sao chép bytes của các section trực tiếp vào bộ nhớ và thực thi các lệnh mà không cần chỉnh sửa gì thêm.
![[Pasted image 20260708165429.png|473]]
***Bài tập 7.4.*** Sử dụng hình ==7.12(a)== để trả lời câu hỏi.
==A.== Địa chỉ hex tham chiếu của `sum` trong dòng 5?
Địa chỉ hex tham chiếu chính là địa chỉ của vùng nhớ sẽ được linker ghi đè vào sau khi tính toán, ở đây là `0x4004df`.
==B.== Giá trị hex tham chiếu của `sum` trong dòng 5?
Giá trị hex tham chiếu tức là giá trị mà sau khi linker tính toán xong, nó sẽ ghi đè lên placeholder, ở đây là `0x00000005`, trong hình ghi ngược là do quy tắc của ==little-endian==.
***Bài tập 7.5.*** Xem xét lệnh gọi tới hàm `swap` trong file m.o (hình ==7.5==).
![[Pasted image 20260708210007.png]]
Cùng với chỉ mục tái định vị sau.
![[Pasted image 20260708210023.png]]
Cho rằng linker tái định vị section `.text` trong file `m.o` tới địa chỉ `0x4004d0` và `swap` ở `0x4004e8`. Giá trị hex tham chiếu tới `swap` tại lệnh `callq` là bao nhiêu?
Giá trị hex tham chiếu tới `swap` tại lệnh `callq` chính là giá trị sẽ được linker ghi đè vào placeholder sau khi tính toán. Symbol `sum` có loại là `PC32`, đây là tương đối qua PC. 
Ta sẽ có công thức tính.
$$.text\_addr + offset + 4 + value = swap\_addr$$
$$\rightarrow 0x4004d0 + 0xa + 4 + value = 0x4004e8$$
$$\rightarrow value =  0xa$$
`Chú ý: nếu symbol sử dụng địa chỉ gián tiếp qua thanh ghi PC, thì giá trị sau lệnh call là offsec, chứ không phải địa chỉ`.
*7.8.* file đối tượng thực thi.
Chúng ta đã thấy cách linker ghép nối các đối tượng để tạo ra 1 file thưc thi duy nhất. Chương trình C ví dụ, bắt đầu bằng tập các file text ascii, đã biến đổi thành 1 file nhị phần chứa tất cả thông tin cần thiết để load vào mem và thực thi nó. Hình 7.13 tóm tắt lại cấu trúc 1 file thực thi ELF.
![[Pasted image 20260708212404.png]]
Cấu trúc file thực thi tương tự với cấu trúc của 1 file tái định vị. Section `.init` định nghĩa một hàm rất bé, gọi là `_init`, được gọi bởi phần mã khởi tạo chương trình. Bởi vì file này được liên kết đầy đủ, không cần phải có section `.rel`
File thực thi ELF được thiết kế để có thể dễ dàng load vào bộ nhớ , với các chunk của file được ánh xạ liên tục vào các phần đoạn bộ nhớ. Ánh xạ này được mô tả thông quá ==program header table==, hình ==7.14== cho thấy 1 phần nhỏ của ==PHT== trong ví dụ về 1 file thực thi `prog`, được hiển thị thông qua lệnh `objdump`.
![[Pasted image 20260708213607.png]]
Từ ==PHT==, ta thấy rằng 2 phân đoạn bộ nhớ sẽ được khởi tạo, chúng chứa nội dung của file thực thi. Dòng 1 và 2 cho ta biết phân đoạn đầu tiên có quyền r/w, bắt đầu từ địa chỉ `0x400000`, có kích thước tổng là 0x69c bytes, và chứa 0x69c bytes đầu tiên của file thực thi, vao gồm.....
Dòng 3 và 4 cho ta biết phân đoạn thứ 2 có quyền r/w, bắt đầu ở `0x600df8`, có tổng kích thước bộ nhớ `0x230` bytes, và chwuas `0x228` byte trong `.data` section bắt đầu từ offset `0xdf8` trong file đối tượng. 8 bytes còn lại trong phân đoạn tương ứng với `.bss`, sẽ được khởi tạo bằng 0 tại thời điểm chạy.
Với bất kì phân đoạn `s` nào, linker phải chọn 1 địa chỉ bắt đầu `vaddr`, sao cho
$$vaddr\ mod\ align = off\ mod align$$
Với `off` là offset của phân đoạn đầu tiên trong file đối tượng, `align` là trường thông tin có trong program header. Ví dụ, trong phân đoạn dữ liệu trong hình ==7.14==.
.....
Việc yêu cầu căn chỉnh này là một phương pháp tối ưu, nó cho phép phân đoạn có thể được chuyển vào bộ nhớ một cách hiệu quả nhất khi thực thi chương trình. Lí do rất tinh vi và có liên quan đến cách tổ chức bộ nhớ ảo.

*7.9.* Load file thực thi.
Để chạy 1 file đối tượng, ta dùng `./`
![[Pasted image 20260708214625.png]]
Vì `prog` không phải là một lệnh có sẵn, shell sẽ cho rằng `prog` là một file thực thi. Shell sẽ chạy chương trình cho chúng ta bằng cách gọi một đoạn mã thực thi nằm trong bộ nhớ, gọi là `loader`. Bất cứ chương trình Linux nào đều có thể gọi `loader` bằng cách gọi hàm `execve`, sẽ được thảo luận trong phần *8.4.6*. Loader sao chép code và dữ liệu trong file thực thi từ đĩa vào bộ nhớ, rồi chạy chương trình bằng cách nhảy đển lệnh đầu tiên, hay còn gọi là ==entry point==. Qúa trình sao chép chương  trình vào bộ nhớ và chạy còn được gọi là `loading`.
Mõi chương trình Linux đang chạy đều có một ảnh bộ nhớ runtime tương tự như trong hình ==7.15==. Trên x86-64, phân đoạn code bắt đầu ở địa chỉ `0x4000000`, tiếp đó là phân đoạn dữ liệu. vùng nhớ ==heap== ngay sau phân đoạn dữ liệu và lớn dần lên trên thông quá lệnh gọi đến thư viện `malloc`. Đây là vùng nhớ được dành cho các module chia sẻ. Bộ nhớ ==stack== của người dùng bắt đầu từ địa chỉ khả dụng cho người dùng lớn nhất  (2^48 - 1) và lớn dần xuống dưới. Vùng nằm phía trên stack, bắt đầu từ 2^48 được dùng cho dữ liệu và code nằm trong ==kernel==, là phần các chương trình hệ điều hành nằm trên bộ nhớ. ![[Pasted image 20260708215920.png]]
Để đơn giản hóa, chúng tôi đã vẽ heap, phân đoạn dữ liệu và code như thể chúng tiếp xúc với nhau.và chúng tôi đặt đỉnh của stack ở địa chỉ lớn nhất khả dụng với người dùng. Trong thực tế, có một khoảng cách giữa 2 segment do cơ chế căn chỉnh bộ nhớ. Ngoài ra, linker sử dụng cơ chế ngẫu nhiên hóa địa chỉ (address-space layout randomization ASLR) khi nó phân địa chỉ runtime cho stack, thư viện chia sẻ, và bộ nhớ heap. Mặc dùng địa chỉ thay đổi mỗi lần chạy chương trình, địa chỉ tương đổi của chúng không đổi.
Khi loader chạy, nó tạo ra 1 ảnh bộ nhớ giống với hình ==7.15==. Được chỉ dẫn bới PHT, nó sao chép các chunk của file thực thi vào 2 segment code và data. Sau đó, loader nhảy đến entry point, nó luôn nằm trong hàm `_start`. Hàm này được định nghĩa trong file đối tượng hệ thống `crt1.o` và giống nhau với mọi chương trình C. Hàm `_start` gọi đến ==hàm khởi tạo hệ thống==, `__libc_start_main`, được định nghĩa trong `libc.so`. Nó khởi tạo môi trường thực thi, gọi hàm `main` của người dùng, xử lí giá trị trả về, và trả quyền điều khiển về cho kernel khi cần.

*7.10.* Liên kết động với thư viện chia sẻ.
Phương pháp liên kết tĩnh chúng ta đã học trong phần 7.6.2 giải quyết được 1 số vấn đề liên quan đến việc cung cấp 1 tập hợp lớn các hàm có liên quan đến chương trình. Tuy vậy, việc liên kết tĩnh vẫn có một số nhược điểm lớn. Thư viện tĩnh, như các loại phần mềm khác, cần được bảo trì và cập nhật thường xuyên. Nếu người lập trình ứng dụng muốn sử dụng các phiên bản mới nhất của 1 thư viện, họ cần để ý xem thư viện có thay đổi gì không, và liên kết lại toàn bộ chương trình.
Một vấn đề khác đó là gần như tất cả các chương trình C đều dùng chuẩn I/O như `printf` và `scanf`. Nếu nhiều chương trình cùng chạy, mã nguồn của các hàm trên bị trùng lặp trong bộ nhớ vì mỗi section `.text` của một chương trình lại chứa một đoạn mã của các hàm đó. Ví dụ với 1 hệ thống có thể chạy cùng lúc 100 tiến trình, điều này sẽ gây ra lãng phí vô cùng lớn về tài nguyên bộ nhớ. 
==Thư viện chia sẻ== là một phương pháp hiện đại giúp giải quyết nhược điểm của các thư viện tĩnh. Một thư viện chia sẻ là một đối tượng, mà cả thời điểm chạy và thời điểm nạp (load), có thể được nạp ở một địa chỉ tùy ý, và liên kết với 1 hoặc nhiều chương trình trong bộ nhớ. Quá trình này gọi là ==liên kết động==, và được thực hiện bởi một chương trình gọi là ==trình liên kết động==. Các ==thư viện chia sẻ== còn được gọi là ==đối tượng chia sẻ==, và trong Linux nó có phần mở rộng là `.so`. Window sử dụng rất nhiều thư viện chia sẻ, nó được dọi là ==DLL (Dynamic Link Library)==. 
Thư viện chia sẻ được "chia sẻ" bằng 2 cách:
- (Trên đĩa) Trong bất kì hệ thống tập tin nào, có 1 và chỉ 1 file `.so` duy nhất cho 1 thư viện. Dữ liệu và code trong file `.so` này được chia sẻ cho tất cả các chương trình tham chiếu đến thư viện đó, trái ngược với các thư viện tĩnh, được sao chép và nhúng trực tiếp vào file thực thi tham chiếu nó.
- (Trong bộ nhớ) Một bản sao chép của section `.text` của 1 file thư viện chia sẻ trên bộ nhớ có thể được chia sẻ với các tiến trình đang chạy. Chúng ta sẽ thảo luận kĩ hơn ở chương 9.
Hình ==7.16== tóm tắt quá trình liên kết động với chương trình ví dụ trong hình ==7.7==. ![[Pasted image 20260709213053.png]]
Để xây dựng 1 thư viện chia sẻ `libvector.so` của các thủ tục vector trong hình ==7.6==. Chúng ta gọi driver biên dịch với một số chỉ hướng đặc biệt cho trình biên dịch và trình liên kết:
![[Pasted image 20260709212725.png]]
Cờ `-fpic` chỉ hướng cho trình biên dịch để sinh ra mã độc lập vị trí (thông tin thêm trong chương 8). Cờ `-shared` chỉ hướng linker để tạo ra đối tượng chia sẻ. Khi chúng ta đã tạo ra được thư viện, chúng ta cần liên kết nó đến chương trình ví dụ trong hình ==7.7==
![[Pasted image 20260709213741.png]]
Nó tạo ra một file thực thi `prog21` ở dạng có thể liên kết với `libvector.so` tại thời điểm chạy. Ý tưởng cơ bản là thực hiện quá trình liên kết 1 cách tĩnh ngay khi file thực thi được tạo ra, sau đó hoàn thành nốt quá trình liên kết động, khi nạp chương trình vào bộ nhớ. Điều quan trọng cần nhận ra đó là không có bất kì phân vùng code hay dữ liệu nào thực sự được sao chép vào file thực thi. Thay vào đó, trình liên kết chỉ sao chép một số thông tin tái định vị và bảng symbol. Những thông tin này giúp chương trình phân giải các tham chiếu đến mã lệnh và dữ liệu bên trong `libvector.so` khi chương trình được nạp.
Khi loader nạp và chạy `prog21`, nó nạp chương trình đã được liên kết 1 phần `prog21` (là chương trình đã có thông tin tái định vị và bảng symbol), sử dụng kỹ thuật đã thảo luận phần ==7.9==. Tiếp đó, nó nhận ra `prog21` có section `.interp`, section này chưa đường dẫn của trình liên kết động, bản chất nó cũng là 1 đối tượng chia sẻ (VD: ld-linux.so). Thay vì chuyển quyền điều khiển cho chương trình như thường lệ, loader nạp và chạy trình liên kết đông. Trình liên kết động sẽ hoàn thiện nối phần liên kết bằng cách thực hiện các công việc sau.
- Tái định vị dữ liệu và text của `libc.so` vào 1 số phân đoạn bộ nhớ (tóm lại là nạp thư viện lên RAM giống nạp chương trình bình thường). 
- Tái định vị text và dữ liệu của `libvector.so` vào 1 số phân đoạn bộ nhớ.
- Tái định vị các tham chiếu có trong `prog21` được định nghĩa bởi `libc.so` và `libvector.so` (ánh xạ các địa chỉ của các thư viện vào trong chương trình thực thi). 
Cuối dùng, trình liên kết động sẽ chuyển quyền điều khiển cho chương trình ứng dụng. Kể từ đây, địa chỉ của các thư viện chia sẻ là cố định và không thay đổi trong suốt quá trình thực thi của chương trình.
(Context: làm sao để chương trình nạp sau biết được vị trí của thư viện chia sẻ để tái sử dụng.)![[Pasted image 20260709221036.png]]![[Pasted image 20260709221056.png]]

*7.11.* Nạp và liên kết các thư viện chia sẻ từ ứng dụng.
Cho tới hiện tại, chúng ta đã thảo luận về kịch bản mà trình liên kết động nạp và liên kết các thư viện chia sẻ khi ứng dụng được nạp, ngay trước khi nó được thực thi. Tuy nhiên, vẫn có thể có trường hợp ứng dụng đang chạy yêu cầu trình liên kết động nạp và liên kết các thư viện chia sẻ tùy ý mà không cần liên kết ứng dụng với các thư viện đó tại thời điểm biên dịch (tức là không cần khai báo tại thời điểm biên dịch, khi chạy nếu cần thì sẽ yêu cầu linker liên kết).
Liên kết động là kỹ thuật cực kì mạnh mẽ và hữu dụng. Dưới đây là một số ứng dụng.
- ==Ứng dụng phân tán==: Các nhà phát triển ứng dụng trên Window thường sử dụng các thư viện chia sẻ để phân phối các cập nhật phần mềm. Họ tạo ra bản sao mới của thư viện chia sẻ, người dùng có thể tải về và thay thế bản cũ. Vào lần tiếp theo chạy app, nó sẽ tự động liên kết và nạp thư viện mới.
- ==Xây dựng các Web server hiệu năng cao==: Một số Web server tạo các ==nội dung động==, như.... (tự đọc đi).

*7.12.* Mã độc lập vị trí (Position-Independent Code - PIC).
Mục đích chính của các thư viện chia sẻ là cho phép các tiến trình đang chạy chia sẻ các thư viện trên bộ nhớ và từ đó tiết kiệm được tài nguyên vộ nhớ. Vậy thì làm sao để các tiến trình chia sẻ 1 thư viện? 1 phương pháp đó là gán trước 1 không gian địa chỉ cho các thư viện dùng chung, sau đó yêu cầu loader luôn load các thư viện chia sẻ vào không gian này. Tuy là đơn giả, cách này tạo ra một số vấn đề nghiêm trọng. Việc sử dụng không gian địa chỉ có hiệu suât không cao bởi vì bắt buộc phải cấp phát 1 vùng bộ nhớ cho dù tiến trình không dùng thư viện. Và nó cũng rất khó để quản lí. Chúng ta phải đảm bảo răng không có phần nào bị ghi chồng chập lên nhau. Mỗi khi có 1 thư viện được sửa đổi, chúng ta cần chắc chắn là nó vẫn phải vừa với không gian được gán trước. Nếu không, chúng ta phải tìm một không gian mới phù hợp hơn. Dần dần, sẽ xảy ra hiện tượng phân mảnh ngoài. Tệ hơn, mỗi hệ thống có cách gán không gian cho thư viện khác nhau, điều này tạo ra nhiều vấn đề về quản lí hơn.
Để khắc phục vấn đề này, các hệ thống hiện đại biên dịch từng phân đoạn code của đối tượng chia sẻ nhằm mục đích chúng có thể nạp bất cứ đâu trên bộ nhớ mà không bị sửa đổi bởi linker. Với phương pháp này, một bản sao phân đoạn code của của đối tượng chia sẻ có thể được chia sẻ với không giới hạn các tiến trình (tuy nhiên mỗi tiến trình vẫn cần có một phần phân đoạn dữ liệu đọc/ghi riêng biệt).
Mã mà có thể được nạp mà không cần tái định vị được gọi là PIC. Người dùng có thể định hướng cho hệ thông biên dịch GNU tạo ra PIC bằng cách dùng cờ `-fptc` cho GCC. Thư viện chia sẻ phải luôn được biên dịch với cờ này.
Trên hệ thống x86-64, tham chiếu đến symbol ở trong cùng 1 đối tượng không cần PIC. Các tham chiếu này có thể biên dịch sử dụng địa chỉ gián tiêp qua PC và tái định vị bằng linker tĩnh khi nó build file. Tuy nhiên, nếu tham chiếu đến các đối tượng bên ngoài, hoặc các biến toàn cụ được định nghĩa bằng các đối tượng chia sẻ cần một số kỹ thuật đặc biệt, sẽ được giới thiệu tiếp theo.
**Tham chiếu dữ liệu PIC**
Trình biên dịch tạo ra các them chiếu PIC đến biến toàn cục bằng cách khai thác sự thật thú vị sau: Cho dù chúng ta nạp 1 đối tượng ở bát kì đâu (kể cả đối tượng chia sẻ) trong bộ nhớ, phân đoạn dữ liệu sẽ luôn ở cùng khoảng cách tới phân đoạn code, và do đó khoảng cách từ lệnh đến dữ liệu luôn là 1 hằng số tại thời gian chạy, hoàn toàn độc lập với vị trí của các phân đoạn code và dữ liệu.
Trình biên dịch muốn tạo tham chiếu PIC tới các biến toàn cục bằng cách tạo ra bảng gọi là ==Global Offset Table (GOT)== ở vị trí bắt đầu phân đoạn dữ liệu. ==GOT== chứa 1 chỉ mục 8 byte với mỗi đối tượng dữ liệu toàn cục (thủ tục hoặc biến toàn cục). được tham chiếu bởi module đối tượng. Trình biên dịch cũng tạo ra các bản ghi tái định vị cho mỗi chỉ mục để chứa địa chỉ tuyệt đối của đối tượng. Mỗi đối tượng tham chiếu để đối tượng toàn cục đều có ==GOT==.
![[Pasted image 20260713090123.png]]
![[Pasted image 20260713091003.png]]
![[Pasted image 20260713091020.png]]
![[Pasted image 20260713091039.png]]
![[Pasted image 20260713091049.png]]
![[Pasted image 20260713091058.png]]
Hình ==7.18== cho ta thấy ==GOT== trong ví dụ thư viện chia sẻ `libvector.so`. Thủ tục `addvec` nạp địa chỉ của biến toàn cục `addcnt` gián tiếp thông qua `GOT[3]` và tăng biến `addvnt` lên 1. Ý tưởng chính ở đây là offset trong tham chiếu gián tiếp qua PC của `GOT[3]` là bất biến trong thời gian chạy.
Vì `addcnt` được định nghĩa bởi `libvector.so module`, trình biên dịch có thể khai thác khoảng cách bất biến giữa 2 phân đoạn code và dữ liệu bằng cách tạo ra tham chiếu PC-Relative tới `addcnt` và thêm vào 1 tái định vị để linker phân giải khi nó build module chia sẻ. Mặc dù vậy, nếu `addcnt` được định nghĩa bởi 1 module chia sẻ khác, việc truy cập gián tiếp thông qua ==GOT== là cần thiết. Trong trường hợp này, trình biên dịch đã sử dụng cách giải quyết đơn giản nhất, dùng GOT cho tất cả tham chiếu 
![[Pasted image 20260713094006.png]]
![[Pasted image 20260713094017.png]]
![[Pasted image 20260713094028.png]]
![[Pasted image 20260713094051.png]]
![[Pasted image 20260713094103.png]]
![[Pasted image 20260713094126.png]]
![[Pasted image 20260713094136.png]]
![[Pasted image 20260713094145.png]]
![[Pasted image 20260713094201.png]]
**Gọi hàm PIC**
Giả sử 1 chương trình gọi 1 hàm được định nghĩa bởi thư viện chia sẻ. Trình biên dịch không có cách nào để đoán trước địa chỉ của hàm tại thời điểm chạy, bởi vì các module chia sẻ có thể nạp vào bất cứ đâu tại thời điểm chạy. Phương pháp thông thường đó là tạo ra một bản ghi tái định vị cho tham chiếu, để trình liên kết động có thể phân giải khi chương trình nạp. Tuy nhiên cách này không phải PIC, bởi vì nó yêu cầu linker phải sửa đổi phân đoạn code của module gọi. Hệ thống biên dịch GNU giải quyết vấn đề này bằng cách sử dụng 1 kỹ thuật rất thú vị, gọi là ==lazy binding==, ám chỉ việc ràng buộc các địa chỉ thủ tục cho tới khi thủ tục được gọi lần đầu.
![[Pasted image 20260713100258.png]]
![[Pasted image 20260713100309.png]]
Ý tưởng của ==LB== đó là 1 chương trình có thể gọi từ vài trăm đến vài nghìn hàm từ các thư viện chia sẻ. Bằng cách không cho phân giải hàm cho tới khi nó được gọi, trình biên dịch động có thể tránh việc tái định vị cho rất nhiều hàm không cần thiết tại thời điểm nạp. 
==LB== được triển khai với sự kết hợp và tương tác phức tạp của 2 cấu trúc dữ liệu: ==GOT== và ==Procedure Linkage Table (PLT)==. Nếu 1 đối tượng gọi bất kì hàm nào được định nghĩa trong thư viện chia sẻ, đối tượng đó sẽ có bảng ==PLT== và ==GOT== riêng biệt. ==GOT== là 1 phần của phân đoạn dữu liệu, còn ==PLT== là 1 phần của phân đoạn code.
![[Pasted image 20260713101100.png]]
Hình ==7.19== cho ta thấy cách mà ==PLT== và ==GOT== phối hợp với nhau để phân giải địa chỉ của hàm tại thời điểm chạy. Đầu tiên, hãy xem nội dung của mỗi bảng.
- ==PLT==: là 1 bảng chứa các chỉ mục 16 byte của code. `PLT[0]` là 1 chỉ mục đăc biệt mà nó trỏ đến trình liên kết động. Mỗi hàm của thư viện chia sẻ mà được gọi bởi chương trình thực thi sẽ có 1 chỉ mục PLT riêng. Mỗi chỉ mục này có trách nhiệm gọi hàm được chỉ định trên. `PLT[1]` (không được vẽ trong hình) gọi hàm khởi động hệ thống `__libc_start_main`, có tác dụng khởi tạo môi trường thực thi, và xử lí giá trị trả về. Các chỉ mục bắt đầu từ 2 gọi các hàm được gọi bởi code của người dùng. VD, `PLT[2]` gọi hàm `addvec`.
- ==GOT==: Như chúng ta đã biết, GOT là 1 mảng các chỉ mục 8 byte. Khi sử dụng trong việc phối hợp với ==PLT==, `GOT[0]` và `GOT[1]` chứa các thông tin mà trình liên kêt động sử dụng khi nó phân giải địa chỉ hàm. `GOT[2]` là chỉ mục trỏ đến trình liên kết động trong module `ld-linux.so`. Các chỉ mục còn lại tương ứng với các hàm được gọi mà địa chỉ cần phải được phân giải tại thời điểm chạy. Mỗi chỉ mục có 1 chỉ mục ==PLT== tương ứng. VD: `GOT[4]` và `PLT[2]` tương ứng với `addvec`. Khi khởi tạo, mỗi chỉ mục ==GOT== đều trỏ vào lệnh thứ 2 của chỉ mục ==PLT== tương ứng
Cách mà ==PLT== và ==GOT== phối hợp trong lần đầu hàm được gọi như sau (==7.19 a)==):
- Thay vì gọi `addvec`, chương trình gọi `PLT[2]`, là entry của `addvec`.
- Lệnh PLT đầu tiên thực hiện 1 nhảy gián tiếp thông qua `GOT[4]`. Bởi vì mỗi chỉ mục GOT khi bắt đầu đều trỏ đến lệnh thứ 2 trong PLT tương ứng. lệnh nhảy gián tiếp chuyển quyền điều khiển lại cho lệnh kế tiếp trong `PLT[2]`.
- Sau khi đẩy ID của `addvec` (`0x1`) lên stack, `PLT[2]` nhảy đến `PLT[0]`.
- `PLT[0]` đẩy 1 tham số cho dynamic linker (thông tin về chỉ mục tái định vị) thông qua `GOT[1]` và nhảy đến dynamic linker gián tiếp qua `GOT[2]`. Dynamic linker sử dụng 2 chỉ mục stack để xác định địa chỉ runtime của addvec, sau đó ghi đè lên `GOT[4]`, và chuyển quyền điều khiển cho `addvec`.
Trong những lần gọi hàm tiếp theo, ==PLT== và ==GOT== phối hợp như sau (==7.19 b)==):
- Chuyển quyền điều khiển cho `PLT[2]` như trước.
- Lần này, lệnh nhảy gián tiếp qua `GOT[4]`sẽ đẩy thẳng đến `addvec` (đơn giản bởi vì sau lần đầu tiên, `GOT[4]` đã  bị ghi đè thành địa chỉ của `addvec` thay vì trỏ đến lệnh thứ 2 trong PLT như lúc đầu).
