__int64 __fastcall main(int a1, char **a2, char **a3)
{
  FILE *file; // rax
  FILE *v1; // rbp
  size_t data; // r12
  char *data_ptr; // rax
  int v7; // edi
  char v8; // dl
  __int64 v9; // rcx
  bool v10; // cc
  char input_data[256]; // [rsp+0h] [rbp-1118h] BYREF
  _BYTE ptr[4120]; // [rsp+100h] [rbp-1018h] BYREF

  file = fopen("program.bin", "rb");
  if ( !file )
  {
    puts("missing program.bin");
    return 1LL;
  }
  v1 = file;
  data = fread(ptr, 1uLL, 0x1000uLL, file);
  fclose(v1);
  puts("vm_branch");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 33 )
    {
      data_ptr = ptr;
      v7 = 0;
      if ( data <= 2 )
        goto correct;
      v8 = ptr[0];
      v9 = ptr[1];
      v10 = ptr[0] <= 0x40u;
      if ( ptr[0] == 64 )
        goto LABEL_13;
ins_case:
      if ( v10 )
      {
        if ( v8 != 32 )
        {
          if ( v8 == 48 )
          {
            v7 += v9;
            goto LABEL_11;
          }
          if ( v8 == 16 )
          {
            v7 = (unsigned __int8)input_data[v9];
            goto LABEL_11;
          }
          goto error;
        }
        v7 ^= v9;
LABEL_11:
        while ( 1 )
        {
          data_ptr += 3;
          if ( (unsigned __int64)&data_ptr[2LL - (_QWORD)ptr] >= data )
            goto correct;
          v8 = *data_ptr;
          v9 = (unsigned __int8)data_ptr[1];
          v10 = (unsigned __int8)*data_ptr <= 0x40u;
          if ( *data_ptr != 64 )
            goto ins_case;
LABEL_13:
          LOBYTE(v7) = __ROL1__(v7, v9);
        }
      }
      if ( v8 != 80 )
      {
        if ( v8 != -1 )
        {
error:
          puts("vm error");
          return 1LL;
        }
correct:
        puts("Correct");
        return 0LL;
      }
      if ( (_BYTE)v9 == (_BYTE)v7 )
        goto LABEL_11;
    }
    puts("Wrong");
  }
  return 1LL;
}