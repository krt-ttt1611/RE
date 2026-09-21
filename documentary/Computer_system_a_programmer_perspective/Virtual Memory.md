*9.1.* Địa chỉ vật lí và địa chỉ ảo.
**a)** Địa chỉ vật lí 
- Bộ nhớ chính của máy tính được tổ chức thành mảng các ô nhớ liên tiếp.
- Mỗi ô nhớ được đánh 1 địa chỉ vật lí, bắt đầu từ 0 và tăng dần liên tục đến hết bộ nhớ. Phương pháp này gọi là ==đánh địa chỉ vât lí (physical addressing)==.
![[Pasted image 20260717082703.png|420]]
- Hình ==9.1== cho ta 1 ví dụ về địa chỉ vật lí trong ngữ cảnh của 1 lệnh `load`, có tác dụng đọc 1 từ 4 bytes bắt đầu từ địa chỉ vật lí 4. 
- Các máy tính đời cũ sử dụng địa chỉ vật lí, và các hệ thống vi xử lí tín hiệu số, vi điều khiển nhúng... vẫn còn sử dụng phương pháp này. Mặc dù vậy, các hệ thống máy tính hiện đại bây giờ sử dụng phương pháp ==đánh địa chỉ ảo (virtual addressing)==, được biểu diễn trong hình ==9.2==.
**b)** Địa chỉ ảo.
![[Pasted image 20260717083136.png]]
- Trong phương pháp này, CPU truy cập vào bộ nhớ chính bằng cách sinh ra 1 địa chỉ ảo. Nó sẽ được chuyển đổi thành địa chỉ vật lí tương ứng trước khi được gửi tới bộ nhớ chính.
- Nhiệm vụ chuyển đổi địa chỉ ảo thành địa chỉ vật lí được gọi là ==dịch địa chỉ (address translation)==.
- Giống như xử lí ngoại lệ, dịch địa chỉ cần sự kết hợp giữa phần cứng CPU và hệ điều hành. Một bộ phận chỉ định trên CPU được gọi là `Memory Management Unit (MMU)` dịch địa chỉ ảo trực tiếp thông qua ==bảng tra cứu (lookup table)== lưu trữ trong bộ nhớ chính, nội dung được quản lí bởi hệ điều hành.
*9.2.* Không gian địa chỉ.
- Một không gian địa chỉ là 1 tập các địa chỉ (số nguyên không âm).
$$\{0,\ 1,\ 2,\ ...\}$$
- Nếu các địa chỉ trong không gian địa chỉ liên tiếp nhau, ta nói nó là ==không gian địa chỉ tuyến tính (linear address space)==. Để đơn giản hóa việc thảo luận, chúng ta sẽ luôn xem xét các vẫn đề với địa chỉ tuyến tính.
- Trong 1 hệ thống sử dụng địa chỉ ảo, CPU sinh ra các địa chỉ ảo từ 1 không gian địa chỉ gồm `N = 2^n` địa chỉ được gọi là ==không gian địa chỉ ảo==. 
$$\{0,\ 1,\ 2,\ ...,\ N\ -\ 1\}$$
- Một hệ thống cũng có 1 ==không gian địa chỉ vật lí== t tương ứng với `M` bytes của bộ nhớ vật lí.
$$\{0,\ 1,\ 2,\ ...,\ M\ -\ 1\}$$
- M không nhất thiết phải là lũy thừa của 2, nhưng để đơn giản hóa, chúng ta sẽ coi như `M = 2^m`.
- Khái niệm về không gian địa chỉ rất quan trọng vì nó cho ta thấy sự khác biệt rõ ràng giữa đối tượng dữ liệu (bytes), và thuộc tính của nó (address). Khi chúng ta nhận ra sự khác biệt này, chúng ta có thể cho phép các đối tượng dữu liệu có nhiều địa chỉ độc lập, được chọn từ không gian địa chỉ. Đây là khái niệm cơ bản của bộ nhớ ảo. Mỗi byte trong bộ nhớ chính có 1 địa chỉ ảo được chọn từ 1 không gian địa chỉ ảo, và 1 địa chỉ vật lí được chọn từ không gian địa chỉ vật lí.

*9.3.* Sử dụng bộ nhớ ảo như công cụ cho caching.
- Khái quát hóa, 1 bộ nhớ ảo được tổ chức gồm 1 mảng `N` byte liên tục được lưu trữ trên đĩa. Mỗi byte có 1 địa chỉ ảo riêng biệt được coi như chỉ số của mảng đó.
- Nội dùng của mảng trên đĩa được cache trên bộ nhớ chính (hiểu nó giống như quan hệ giữa cache với RAM vây, cache chỉ bốc dữ liệu cần thiết từ RAM lên để CPU thực thi, thì RAM cũng chỉ bốc dữ liệu cần thiết từ đĩa lên).
- Giống như bất kì cơ chế cache nào trong hệ thống phân cấp bộ nhớ, dữ liệu trên đĩa được chia thành các block, coi như 1 đơn vị truyền tải giữa đĩa và bộ nhớ chính (mqh giữa cấp thấp và cấp cao). Hệ thống sử dụng VM xử lí việc này bằng cách chia bộ nhớ ảo thành các block kích thước cố định gọi là trang ảo. Mỗi trang ảo có kích thước `P = 2^p`. Tương tự, bộ nhớ vật lí cũng được chia thành các trang vật lí, cũng có kích thước `P` (trang vật lí còn được gọi là khung trang).
- Tại bất kì thời điểm nào, các trang có thể phân loại dựa trên các đặc điểm sau
	- ==Unallocated==: Trang chưa được cấp phát (hoặc tạo ra) bởi hệ thống VM. Các khối chưa được cấp phát không có bất kì dữ liệu nào, và vì thế không tốn dung lượng trên đĩa.
	- ==Cached==: Trang đã được cấp phát và đang được cache trên bộ nhớ vật lí.
	- ==Uncached==: Trang đã được cấp phát nhưng chưa được cache trên bộ nhớ vật lí.
![[Pasted image 20260719081124.png]]
- Hình ==9.3== cho ta thấy 1 bộ nhớ ảo nhỏ với 8 trang ảo. Trang 0 và 3 chưa được cấp phát, nên chúng không tồn tại trên đĩa. Trang 1, 4, 6 được cache trong bộ nhớ vật lí. Trang 2, 5, 7 được cấp phát nhưng chưa được cache lên bộ nhớ vật lí.
**9.3.1.** Tổ chức Cache DRAM.
Để giúp phân biệt các loại cache khác nhau trên.... (phần này nói khá rõ trong giáo trình ktmt&hđh, bỏ qua).
**9.3.2., 9.3.3, 9.3.4, 9.3.5, 9.3.6.** (cũng có trong ktmt&hđh, bỏ qua).

*9.5* VM sử dụng như là công cụ bảo vệ bộ nhớ.
- Bất kì hệ thống máy tính hiện đại nào đều phải cung cấp 1 cơ chế cho hệ điều hành để kiểm soát truy cập tới hệ thống bộ nhớ. 1 tiến trình người dùng không được cho phép sửa đổi trong phân đoạn chỉ đọc, không được đọc hoặc sửa đổi mã trong nhân, không được đọc hoặc ghi và bộ nhớ riêng tư của tiến trình khác....
- Như chúng ta đã biết, việc cung cấp cơ chế phân tách không gian địa chỉ ảo khiến việc cung cấp không gian bộ nhớ riêng tư cho các tiến trình khác nhau trở nên dễ dàng hơn. Nhưng cơ chế dịch địa chỉ có thể được mở rộng 1 cách tự nhiên để cung cấp khả năng kiểm soát truy cập chi tiết hơn nữa. Vì phần cứng dịch địa chỉ đọc PTE (chỉ mục bảng trang - Page Table Entry) mỗi khi CPU tạo ra 1 địa chỉ, nó rất dễ dang để kiểm soát truy cập tới nội dung của 1 trang ảo bằng cách thêm vào các bit thông tin về quyền vào PTE. Hình ==9.10== cho ta thấy ý tưởng này.
![[Pasted image 20260719084422.png]]
- Trong ví dụ này, chúng tôi đã thêm vào 3 bit quyền với mỗi PTE: `SUP` chỉ ra nếu tiến trình phải được chạy dưới kerner mode (supervisor) để có thể truy cập trang. `READ` và `WRITE` kiểm soát quyền đọc và ghi của trang.
- Nếu 1 lệnh trong 1 tiến trình nào đó vi pham quyền, CPU sẽ thông báo 1 lỗi bảo vệ, chuyển quyền điều khiển cho bộ phận xử lí ngoại lệ ở kernel, bộ phận này gửi 1 tín hiệu SIGSEGV (Signal Segment Violation). tới tiến trình. Linux shell báo cáo ngoại lệ này như là `segmentation fault`.

*9.6.* Dịch địa chỉ.
- Hỉnh ==9.11== tóm tắt các kí hiệu chúng ta sẽ sử dụng xuyên suốt phần này.
![[Pasted image 20260719085240.png]]
- Thông thường, dịch địa chỉ là việc ánh xạ 1 nguyên tố trong không gian địa chỉ ảo N nguyên tố (VAS) vào không gian địa chỉ vật lí M nguyên tố.
$$MAP:\ VAS\ \rightarrow\ PAS\ \cup\ \emptyset $$
- Trong đó: `MAP(A)` = `A'` nếu dữ liệu trong địa chỉ ảo `A` đang có trên địa chỉ vật lí `A'` trong PAS. Bằng rỗng khi chưa có trên địa chỉ vật lí.
- Hình ==9.12== cho ta thấy cách mà MMU sử dụng bảng trang để thực hiện việc ánh xạ này. 1 thanh ghi điều khiển trong CPU, ==PTBR (Page Table Base Register)== chỉ tới bảng trang hiện tại. 
![[Pasted image 20260719091943.png]]
- 1 địa chỉ ảo n-bit gồm 2 thành phần chính: ==p-bit Virtual Page Offset (VPO) và (n-p)-bit Virtual Page Number (VPN)==. MMU sử dụng VPN để chọn PTE tương ứng.Ví udj VPN `0` chọn PTE `0`. Địa chỉ vật lí tương ứng là sự kết hợp giữa ==Physical Page Number (PPN)== từ PTE và VPO từ địa chỉ ảo. Chú ý rằng vì trang vật lý và trang ảo đều có kích thước `P`, Physical Page Offset PPO sẽ bằng với VPO.
(Phần này thiên về cấu trúc phần cứng hơn, t bỏ qua vì nó không giúp được quá nhiều trong CTF).
*9.7.* Case study (core i7) (bỏ qua)


