![](../../../ảnh/Pasted%20image%2020260513065344.png)

Đây là dạng bài máy ảo, tác giả sẽ tạo ra 1 máy ảo, tự định nghĩa các tập lệnh, thanh ghi. Chương trình sẽ đóng vai trò như phần cứng dùng để chạy máy ảo này.
```cpp
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  FILE *data; // rax
  FILE *v4; // rdi
  unsigned int check; // ebx
  _BYTE *ins; // rax
  char v8; // cl
  __int64 v9; // rsi
  char input_data[256]; // [rsp+0h] [rbp-918h] BYREF
  _BYTE ins_ptr[2072]; // [rsp+100h] [rbp-818h] BYREF

  data = fopen("ram.bin", "rb");
  if ( data )
  {
    v4 = data;
    if ( fread(ins_ptr, 1uLL, 2048uLL, data) == 2048 )
    {
      fclose(v4);
      ins = ins_ptr;
      v8 = 0;
      while ( 2 )
      {
        v9 = (unsigned __int8)ins[513];
        switch ( ins[512] )
        {
          case 0:
            puts("vm_note");
            fwrite("flag> ", 1uLL, 6uLL, stdout);
            if ( !fgets(input_data, 256, stdin) )
              return 1;
            input_data[strcspn(input_data, "\r\n")] = 0;
            if ( strlen(input_data) == 36 )
            {
              check = memcmp(input_data, ins_ptr, 0x24uLL);
              if ( !check )
              {
                puts("Correct");
                return check;
              }
            }
            puts("Wrong");
            break;
          case 1:
            ins_ptr[v9] = ins[514];
            goto LABEL_13;
          case 2:
            v8 = ins_ptr[v9];
            goto LABEL_13;
          case 3:
            ins_ptr[v9] ^= v8;
            goto LABEL_13;
          case 4:
            ins_ptr[v9] = __ROL1__(ins_ptr[v9], v8);
LABEL_13:
            ins += 3;
            continue;
          default:
            puts("vm error");
            return 1;
        }
        break;
      }
    }
    else
    {
      fclose(v4);
      puts("bad ram.bin");
    }
  }
  else
  {
    puts("missing ram.bin");
  }
  return 1;
}
```
Phân tích logic chương trình:

- Đầu tiên, chương trình sẽ đọc 2048 bytes của file ram.bin, rồi lưu con trỏ vào biến ins_ptr.
- Sau đó, nhảy vào khối switch với điều kiện là byte thứ 512 của khối dữ liệu trong file bin. Check thử file bin bằng hexedit, ta thấy byte đó bằng 1, nên sẽ bỏ qua case 0, là case check flag.

![](../../../ảnh/Pasted%20image%2020260513080349.png)

- Đọc các case còn lại thì ta có thể đoán được là chúng có tác dụng gen flag. Sau khi gen xong thì mới gọi đến case input và check flag.
-  Ở đây, biến ins đóng vai trò như 1 con trỏ lệnh, kết hợp với chỉ số sẽ trỏ lần lượt đến các byte cách nhau 3 đơn vị. Sau đó, switch có tác dụng kiểm tra xem byte đó nằm trong các giá trị từ 0 đến 4, và quyết định xem sẽ thực thi case nào (là thực thi các lệnh).
- Phân tích lần lượt các case.
	- Nếu ins[512] = 1 -> ins_ptr[ins[512 + 1]] = ins[512 + 2] và tăng ins thêm 3
	- Nếu ins[512] = 2 -> v8 = ins_ptr[ins[512 + 1]] và tăng ins thêm 3
	- Nếu ins[512] = 3 -> ins_ptr[ins[512 + 1]] ^= v8 và tăng ins thêm 3
	- Nếu ins[512] = 4 -> ins_ptr[ins[512 + 1]] = rol1(ins_ptr[v9], v8)
- Các case này có tác dụng ghi đè flag lên các byte dữ liệu phía trên của file.

 Ta còn phát hiện ra 1 điểm đặc biệt của chương trình nữa, đó là sau khi thực hiện xong việc ghi đè, flag sẽ được lưu ở dạng bản rõ ngay trong file. Nên ý tường ở đây là ta sẽ đặt 1 breakpoint ở chỗ check flag sau đó chạy chương trình. Khi chạy đến đoạn check flag thì ta chỉ cần đọc dữ liệu ở vùng nhớ chứa flag là được.

 ![](../../../ảnh/Pasted%20image%2020260513083320.png)

 Đã thấy flag.

 flag: ISPCLUB{vm_bytecode_can_be_emulated}