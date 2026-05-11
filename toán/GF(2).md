**GF(2)** (Trường Galois bậc 2) là trường hữu hạn nhỏ nhất và cơ bản nhất trong toán học và tin học. Nó chỉ gồm hai phần tử: **0** và **1**. 

Dưới đây là những đặc điểm chính của nó:

1. Các phép toán cơ bản

Các phép toán trong GF(2) tương ứng trực tiếp với các cổng logic trong máy tính:

- **Phép cộng (+):** Tương đương với phép toán **XOR** (Hoặc loại trừ).
    - 0 + 0 = 0
    - 0 + 1 = 1
    - 1 + 0 = 1
    - 1 + 1 = 0 (vì 2 mod 2 = 0)
- **Phép nhân (×):** Tương đương với phép toán **AND** (Và).
    - 0 × 0 = 0
    - 0 × 1 = 0
    - 1 × 0 = 0
    - 1 × 1 = 1 

2. Tính chất đặc biệt

- **Tự nghịch đảo:** Trong GF(2), phép cộng và phép trừ là một (vì -1 = 1 mod 2). Do đó, \(x + x = 0\) với mọi \(x\).
- **Đặc số bằng 2:** Đây là đặc điểm quan trọng trong lý thuyết mã hóa.

3. Ứng dụng

GF(2) là "ngôn ngữ" cốt lõi của thế giới kỹ thuật số:

- **Khoa học máy tính:** Biểu diễn dữ liệu dưới dạng bit (0 và 1).
- **Mật mã học:** Được sử dụng trong các thuật toán như AES để thực hiện các phép biến đổi trên byte.
- **Lý thuyết mã hóa:** Dùng để tạo ra các mã kiểm tra lỗi như mã CRC (Cyclic Redundancy Check) hoặc mã Hamming.

Nói cách khác, nếu bạn đang sử dụng bất kỳ thiết bị điện tử nào, bạn đang gián tiếp sử dụng các quy tắc của GF(2).