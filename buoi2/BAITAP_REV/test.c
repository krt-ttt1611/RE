//main
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  __int64 v3; // rbx
  __int64 v4; // rdx
  __int64 v5; // rcx
  __int64 v6; // r8
  __int64 v7; // r9
  __m128i data_1; // [rsp+0h] [rbp-138h]
  __m128i data_2; // [rsp+10h] [rbp-128h]
  char input_data[280]; // [rsp+20h] [rbp-118h] BYREF

  data_1 = _mm_unpacklo_epi64(_mm_loadl_epi64((const __m128i *)&off_3DD0), (__m128i)(unsigned __int64)sub_12A0);
  data_2 = _mm_unpacklo_epi64(_mm_loadl_epi64((const __m128i *)&off_3DD8), (__m128i)(unsigned __int64)sub_12C0);
  puts("dispatch_garden");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    v3 = 0LL;
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 42 )
    {
      while ( ((unsigned __int8 (__fastcall *)(_QWORD, __int64, __int64, __int64, __int64, __int64, __int64, __int64, __int64, __int64))data_1.m128i_i64[v3 & 3])(
                (unsigned __int8)input_data[v3],
                v3,
                v4,
                v5,
                v6,
                v7,
                data_1.m128i_i64[0],
                data_1.m128i_i64[1],
                data_2.m128i_i64[0],
                data_2.m128i_i64[1]) == byte_2040[v3] )
      {
        if ( ++v3 == 42 )
        {
          puts("Correct");
          return 0LL;
        }
      }
    }
    puts("Wrong");
  }
  return 1LL;
}