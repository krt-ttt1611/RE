bool __fastcall sub_7FF7AE67EB20(__int64 a1, __int64 a2, char a3)
{
  char v5; // r9
  int v6; // ecx
  BOOL v7; // r8d
  DWORD v8; // r15d
  DWORD v9; // r12d
  const WCHAR *v10; // rcx
  char *FileW; // rdi
  DWORD LastError; // r14d
  const WCHAR *v13; // rcx
  WCHAR *v14; // rcx
  __m128i v15; // xmm0
  FILETIME LastAccessTime; // [rsp+40h] [rbp-89h] BYREF
  __int128 v18; // [rsp+50h] [rbp-79h]
  __m128i si128; // [rsp+60h] [rbp-69h]
  __int128 v20; // [rsp+80h] [rbp-49h]
  __int64 v21; // [rsp+90h] [rbp-39h]
  LPCWSTR lpFileName[2]; // [rsp+C0h] [rbp-9h] BYREF
  __m128i v23; // [rsp+D0h] [rbp+7h]

  *(_DWORD *)(a1 + 88) = 0;
  if ( *(_BYTE *)(a1 + 48) || (v5 = 0, (a3 & 4) != 0) )
    v5 = 1;
  v6 = (a3 & 2) != 0 ? 0x40000000 : 0x80000000;
  if ( (a3 & 1) != 0 )
    v6 = (a3 & 2) != 0 ? 0x40000000 : -1073741824;
  v7 = (a3 & 8) == 0;
  v8 = v7 | 2;
  if ( !v5 )
    v8 = v7;
  v18 = 0LL;
  si128 = _mm_load_si128((const __m128i *)&xmmword_7FF7AE7982C0);
  LOWORD(v18) = 0;
  v20 = 0LL;
  v21 = 0LL;
  v9 = v6 | 0x100;
  if ( !*(_BYTE *)(a1 + 35) )
    v9 = v6;
  v10 = (const WCHAR *)a2;
  if ( *(_QWORD *)(a2 + 24) > 7uLL )
    v10 = *(const WCHAR **)a2;
  FileW = (char *)CreateFileW(v10, v9, v8, 0LL, 3u, 0x8000000u, 0LL);
  if ( FileW == (char *)-1LL )
  {
    LastError = GetLastError();
    *(_OWORD *)lpFileName = 0LL;
    v23 = _mm_load_si128((const __m128i *)&xmmword_7FF7AE7982C0);
    LOWORD(lpFileName[0]) = 0;
    if ( (unsigned __int8)sub_7FF7AE698860(a2, lpFileName) )
    {
      v13 = (const WCHAR *)lpFileName;
      if ( v23.m128i_i64[1] > 7uLL )
        v13 = lpFileName[0];
      FileW = (char *)CreateFileW(v13, v9, v8, 0LL, 3u, 0x8000000u, 0LL);
      if ( GetLastError() == 2 )
        LastError = 2;
    }
    if ( v23.m128i_i64[1] > 7uLL )
    {
      v14 = (WCHAR *)lpFileName[0];
      if ( (unsigned __int64)(2 * v23.m128i_i64[1] + 2) >= 0x1000 )
      {
        v14 = (WCHAR *)*((_QWORD *)lpFileName[0] - 1);
        if ( (unsigned __int64)((char *)lpFileName[0] - (char *)v14 - 8) > 0x1F )
          invoke_watson(0LL, 0LL, 0LL, 0, 0LL);
      }
      j_j_j__free_base(v14);
    }
    v15 = _mm_load_si128((const __m128i *)&xmmword_7FF7AE7982C0);
    v23 = v15;
    LOWORD(lpFileName[0]) = 0;
    if ( FileW == (char *)-1LL && LastError == 2 )
      *(_DWORD *)(a1 + 88) = 1;
  }
  else
  {
    v15 = _mm_load_si128((const __m128i *)&xmmword_7FF7AE7982C0);
  }
  if ( *(_BYTE *)(a1 + 35) && FileW != (char *)-1LL )
  {
    LastAccessTime.dwLowDateTime = -1;
    LastAccessTime.dwHighDateTime = -1;
    SetFileTime(FileW, 0LL, &LastAccessTime, 0LL);
    v15 = _mm_load_si128((const __m128i *)&xmmword_7FF7AE7982C0);
  }
  *(_BYTE *)(a1 + 32) = 0;
  *(_DWORD *)(a1 + 20) = 0;
  *(_BYTE *)(a1 + 25) = 0;
  if ( FileW != (char *)-1LL )
  {
    *(_QWORD *)(a1 + 8) = FileW;
    sub_7FF7AE5A4E38((void *)(a1 + 56));
    *(_BYTE *)(a1 + 36) = 0;
    v15 = _mm_load_si128((const __m128i *)&xmmword_7FF7AE7982C0);
  }
  si128 = v15;
  LOWORD(v18) = 0;
  return FileW + 1 != 0LL;
}