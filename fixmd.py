import os
import re
import sys
from urllib.parse import unquote, quote

# Fix Windows console encoding cho tên file tiếng Việt
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
# Tự động detect thư mục gốc repo từ vị trí file script
# ============================================================
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(REPO_ROOT, 'image')

# Regex match markdown image link: ![alt](path)
IMAGE_LINK_RE = re.compile(r'(!\[[^\]]*\])\(([^)]+)\)')


# ============================================================
# FIX 1: Sửa link ảnh trỏ đúng về thư mục image/
# ============================================================

def get_all_image_files():
    """Lấy tất cả tên file ảnh trong thư mục image/."""
    images = set()
    if os.path.isdir(IMAGE_DIR):
        for f in os.listdir(IMAGE_DIR):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp')):
                images.add(f)
    return images


def url_encode_path(path):
    """Encode spaces -> %20, giữ nguyên path separators."""
    parts = path.split('/')
    encoded_parts = []
    for part in parts:
        if part in ('..', '.'):
            encoded_parts.append(part)
        else:
            encoded_parts.append(quote(part, safe=''))
    return '/'.join(encoded_parts)


def fix_image_links(content, md_file_path, image_files):
    """Sửa tất cả link ảnh trong content để trỏ đúng về image/."""
    changes = 0

    def replace_image_link(match):
        nonlocal changes
        alt_part = match.group(1)   # ![alt text]
        original_path = match.group(2)  # path trong ()

        # Lấy tên file thật (decode %20 -> space)
        filename = os.path.basename(unquote(original_path))

        # Nếu ảnh tồn tại trong image/ -> tính lại relative path
        if filename in image_files:
            md_dir = os.path.dirname(md_file_path)
            image_full = os.path.join(IMAGE_DIR, filename)
            rel = os.path.relpath(image_full, md_dir).replace('\\', '/')
            encoded_rel = url_encode_path(rel)

            new_link = f'{alt_part}({encoded_rel})'
            if match.group(0).rstrip() != new_link.rstrip():
                changes += 1
            return new_link

        # Ảnh không tìm thấy -> giữ nguyên
        return match.group(0)

    new_content = IMAGE_LINK_RE.sub(replace_image_link, content)
    return new_content, changes


# ============================================================
# FIX 2: Thêm dòng trống giữa các block markdown (GitHub render)
# ============================================================

def fix_markdown_newlines(content):
    lines = content.split('\n')
    result = []

    # Các pattern bắt đầu/kết thúc block (toggle)
    TOGGLE_BLOCKS = [
        '```',   # Code block
        '$$',    # Math block
        '~~~',   # Alt code block
    ]

    # Numbered list: 1. 2. 3. ...
    NUMBERED_LIST = re.compile(r'^\d+\.\s')

    toggle_stack = []  # Stack để track block đang mở

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Kiểm tra toggle block
        for tok in TOGGLE_BLOCKS:
            if stripped.startswith(tok):
                if toggle_stack and toggle_stack[-1] == tok:
                    toggle_stack.pop()   # Đóng block
                else:
                    toggle_stack.append(tok)  # Mở block
                break

        result.append(line)

        if i >= len(lines) - 1:
            continue

        next_line = lines[i + 1]
        next_stripped = next_line.strip()

        # Nếu đang trong block -> không thêm dòng trống
        if toggle_stack:
            continue

        # Nếu dòng hiện tại hoặc dòng tiếp theo rỗng -> không thêm
        if not stripped or not next_stripped:
            continue

        # Nếu dòng tiếp theo là toggle block -> không thêm
        if any(next_stripped.startswith(tok) for tok in TOGGLE_BLOCKS):
            continue

        # Nếu dòng hiện tại là toggle block -> không thêm
        if any(stripped.startswith(tok) for tok in TOGGLE_BLOCKS):
            continue

        # Nếu cả 2 dòng đều là list item cùng loại -> không thêm
        cur_is_list = any(stripped.startswith(p) for p in ['- ', '* ', '+ ']) or bool(NUMBERED_LIST.match(stripped))
        next_is_list = any(next_stripped.startswith(p) for p in ['- ', '* ', '+ ']) or bool(NUMBERED_LIST.match(next_stripped))
        if cur_is_list and next_is_list:
            continue

        # Nếu cả 2 dòng đều là table row -> không thêm
        if stripped.startswith('|') and next_stripped.startswith('|'):
            continue

        # Nếu cả 2 dòng đều là blockquote -> không thêm
        if stripped.startswith('>') and next_stripped.startswith('>'):
            continue

        # Nếu dòng tiếp theo là separator table (---|---) -> không thêm
        if re.match(r'^\|?[\s\-\|:]+\|?$', next_stripped):
            continue

        # Thêm dòng trống
        result.append('')

    return '\n'.join(result)


# ============================================================
# FIX 3: Sửa ==text== thành chữ màu xanh lá cây
# ============================================================

def fix_highlight_green(content):
    changes = 0
    code_blocks = []
    
    def save_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    # Lưu lại code blocks để tránh replace nhầm
    temp = re.sub(r'```.*?```', save_block, content, flags=re.DOTALL)
    # Lưu lại inline code
    temp = re.sub(r'`[^`\n]*`', save_block, temp)
    
    # Tìm và thay thế ==text==
    # (?!\s) : không bắt đầu bằng khoảng trắng
    # (?<!\s) : không kết thúc bằng khoảng trắng
    pattern = r'==(?!\s)(.+?)(?<!\s)=='
    
    # Dùng MathJax để đổi màu trên GitHub, chú ý double backslash để tránh escape \t
    replacement = r'$\\color{green}{\\text{\1}}$'
    
    new_temp, n = re.subn(pattern, replacement, temp)
    changes += n
    
    if changes > 0:
        # Khôi phục code blocks
        def restore_block(match):
            idx = int(match.group(1))
            return code_blocks[idx]
            
        final_content = re.sub(r'__CODE_BLOCK_(\d+)__', restore_block, new_temp)
        return final_content, changes
    
    return content, 0


# ============================================================
# MAIN: Chạy cả 3 fix cho tất cả file .md trong repo
# ============================================================

def main():
    image_files = get_all_image_files()
    print(f"[*] Repo root  : {REPO_ROOT}")
    print(f"[*] Image dir  : {IMAGE_DIR}")
    print(f"[*] Images found: {len(image_files)}")
    print()

    file_count = 0
    img_link_fixed = 0
    highlight_fixed = 0

    for root, dirs, files in os.walk(REPO_ROOT):
        # Bỏ qua .git, .obsidian
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian')]

        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, REPO_ROOT)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Fix 1: image links
                    content, img_changes = fix_image_links(content, path, image_files)

                    # Fix 2: newlines
                    content = fix_markdown_newlines(content)

                    # Fix 3: green highlight
                    content, hl_changes = fix_highlight_green(content)

                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    status = []
                    if img_changes:
                        status.append(f"{img_changes} image link(s)")
                        img_link_fixed += img_changes
                    if hl_changes:
                        status.append(f"{hl_changes} highlight(s)")
                        highlight_fixed += hl_changes

                    if status:
                        print(f"  [FIXED] {rel_path} - {', '.join(status)}")
                    else:
                        print(f"  [OK]    {rel_path}")

                    file_count += 1
                except Exception as e:
                    print(f"  [ERR]   {rel_path}: {e}")

    print()
    print("=" * 50)
    print(f"Done! Processed {file_count} file(s), fixed {img_link_fixed} image link(s), {highlight_fixed} highlight(s).")


if __name__ == '__main__':
    main()