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

# Regex match markdown image link chuẩn: ![alt](path)
IMAGE_LINK_RE = re.compile(r'(!\[[^\]]*\])\(([^)]+)\)')

# Regex match Obsidian image embed: ![[filename.ext]] hoặc ![[filename.ext|alt]]
OBSIDIAN_IMAGE_RE = re.compile(
    r'!\[\[([^\]|]+?\.(?:png|jpg|jpeg|gif|svg|bmp|webp))(?:\|([^\]]*))?\]\]',
    re.IGNORECASE
)

# Regex match Obsidian wikilink: [[pagename]] hoặc [[pagename|alias]]
OBSIDIAN_LINK_RE = re.compile(r'\[\[([^\]|#]+?)(?:#([^\]|]*?))?(?:\|([^\]]*?))?\]\]')

# Obsidian callout type → emoji + label
CALLOUT_MAP = {
    'note':      ('📝', 'NOTE'),
    'info':      ('ℹ️', 'INFO'),
    'tip':       ('💡', 'TIP'),
    'hint':      ('💡', 'HINT'),
    'important': ('❗', 'IMPORTANT'),
    'warning':   ('⚠️', 'WARNING'),
    'caution':   ('⚠️', 'CAUTION'),
    'danger':    ('🔴', 'DANGER'),
    'error':     ('❌', 'ERROR'),
    'success':   ('✅', 'SUCCESS'),
    'check':     ('✅', 'CHECK'),
    'done':      ('✅', 'DONE'),
    'question':  ('❓', 'QUESTION'),
    'help':      ('❓', 'HELP'),
    'faq':       ('❓', 'FAQ'),
    'todo':      ('📋', 'TODO'),
    'abstract':  ('📄', 'ABSTRACT'),
    'summary':   ('📄', 'SUMMARY'),
    'tldr':      ('📄', 'TLDR'),
    'cite':      ('📌', 'CITE'),
    'quote':     ('📌', 'QUOTE'),
    'example':   ('📖', 'EXAMPLE'),
    'bug':       ('🐛', 'BUG'),
}


# ============================================================
# Helpers chung
# ============================================================

def get_all_image_files():
    """Lấy tất cả tên file ảnh trong thư mục image/ (và toàn bộ repo)."""
    images = {}  # filename (lowercase) -> full path
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian')]
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp')):
                key = f.lower()
                full = os.path.join(root, f)
                # Ưu tiên file trong IMAGE_DIR
                if key not in images or os.path.dirname(full) == IMAGE_DIR:
                    images[key] = full
    return images


def get_image_files_set():
    """Chỉ lấy tên file (không phân biệt hoa/thường) trong thư mục image/."""
    images = set()
    if os.path.isdir(IMAGE_DIR):
        for f in os.listdir(IMAGE_DIR):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp')):
                images.add(f)
    return images


def url_encode_path(path):
    """Encode spaces → %20, giữ nguyên path separators."""
    parts = path.split('/')
    encoded_parts = []
    for part in parts:
        if part in ('..', '.'):
            encoded_parts.append(part)
        else:
            encoded_parts.append(quote(part, safe=''))
    return '/'.join(encoded_parts)


def make_relative_image_path(md_file_path, image_full_path):
    """Tính relative path từ md_file sang image, encode URL-safe."""
    md_dir = os.path.dirname(md_file_path)
    rel = os.path.relpath(image_full_path, md_dir).replace('\\', '/')
    return url_encode_path(rel)


def protect_code_blocks(content):
    """Lưu code blocks và inline code, trả về (temp_content, blocks_list)."""
    blocks = []

    def save(match):
        blocks.append(match.group(0))
        return f'__PROTECTED_BLOCK_{len(blocks) - 1}__'

    # Fenced code blocks ``` ... ```
    temp = re.sub(r'```[\s\S]*?```', save, content)
    # Fenced code blocks ~~~ ... ~~~
    temp = re.sub(r'~~~[\s\S]*?~~~', save, temp)
    # Inline code `...`
    temp = re.sub(r'`[^`\n]*`', save, temp)
    return temp, blocks


def restore_code_blocks(temp, blocks):
    """Khôi phục code blocks đã được lưu."""
    def restore(match):
        return blocks[int(match.group(1))]
    return re.sub(r'__PROTECTED_BLOCK_(\d+)__', restore, temp)


# ============================================================
# FIX 1: Sửa link ảnh chuẩn ![alt](path) trỏ đúng về image/
# ============================================================

def fix_image_links(content, md_file_path, all_images):
    """Sửa link ảnh markdown chuẩn trỏ sai đường dẫn."""
    changes = 0

    def replace_image_link(match):
        nonlocal changes
        alt_part = match.group(1)        # ![alt text]
        original_path = match.group(2)   # path trong ()

        # Bỏ qua URL tuyệt đối (http/https/ftp)
        if re.match(r'^https?://', original_path.strip()):
            return match.group(0)

        # Lấy tên file thật (decode %20 → space)
        filename = os.path.basename(unquote(original_path))
        key = filename.lower()

        if key in all_images:
            image_full = all_images[key]
            encoded_rel = make_relative_image_path(md_file_path, image_full)
            new_link = f'{alt_part}({encoded_rel})'
            if match.group(0).rstrip() != new_link.rstrip():
                changes += 1
            return new_link

        # Ảnh không tìm thấy → giữ nguyên
        return match.group(0)

    new_content = IMAGE_LINK_RE.sub(replace_image_link, content)
    return new_content, changes


# ============================================================
# FIX 2: Thêm dòng trống giữa các block markdown (GitHub render)
# ============================================================

def fix_markdown_newlines(content):
    lines = content.split('\n')
    result = []

    TOGGLE_BLOCKS = ['```', '$$', '~~~']
    NUMBERED_LIST = re.compile(r'^\d+\.\s')
    toggle_stack = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        for tok in TOGGLE_BLOCKS:
            if stripped.startswith(tok):
                if toggle_stack and toggle_stack[-1] == tok:
                    toggle_stack.pop()
                else:
                    toggle_stack.append(tok)
                break

        result.append(line)

        if i >= len(lines) - 1:
            continue

        next_line = lines[i + 1]
        next_stripped = next_line.strip()

        if toggle_stack:
            continue
        if not stripped or not next_stripped:
            continue
        if any(next_stripped.startswith(tok) for tok in TOGGLE_BLOCKS):
            continue
        if any(stripped.startswith(tok) for tok in TOGGLE_BLOCKS):
            continue

        cur_is_list = (any(stripped.startswith(p) for p in ['- ', '* ', '+ '])
                       or bool(NUMBERED_LIST.match(stripped)))
        next_is_list = (any(next_stripped.startswith(p) for p in ['- ', '* ', '+ '])
                        or bool(NUMBERED_LIST.match(next_stripped)))
        if cur_is_list and next_is_list:
            continue

        if stripped.startswith('|') and next_stripped.startswith('|'):
            continue
        if stripped.startswith('>') and next_stripped.startswith('>'):
            continue
        if re.match(r'^\|?[\s\-\|:]+\|?$', next_stripped):
            continue

        result.append('')

    return '\n'.join(result)


# ============================================================
# FIX 3: Sửa ==text== thành chữ màu xanh lá cây (MathJax)
# ============================================================

def fix_highlight_green(content):
    changes = 0
    temp, blocks = protect_code_blocks(content)

    pattern = r'==(?!\s)(.+?)(?<!\s)=='
    replacement = r'$\\color{green}{\\text{\1}}$'

    new_temp, n = re.subn(pattern, replacement, temp)
    changes += n

    if changes > 0:
        return restore_code_blocks(new_temp, blocks), changes

    return content, 0


# ============================================================
# FIX 4: Convert Obsidian image embed ![[file.png]] → ![](path)
# ============================================================

def fix_obsidian_image_embeds(content, md_file_path, all_images):
    """
    Chuyển ![[image.png]] hoặc ![[image.png|alt text]] sang
    ![alt text](relative/path/to/image.png) chuẩn GitHub.
    """
    changes = 0

    def replace_obsidian_img(match):
        nonlocal changes
        filename = match.group(1).strip()
        alt_text = match.group(2).strip() if match.group(2) else filename
        key = filename.lower()

        if key in all_images:
            image_full = all_images[key]
            encoded_rel = make_relative_image_path(md_file_path, image_full)
            changes += 1
            return f'![{alt_text}]({encoded_rel})'

        # Ảnh không tìm thấy → chuyển sang standard syntax với path gốc
        changes += 1
        encoded = url_encode_path(filename)
        return f'![{alt_text}]({encoded})'

    new_content = OBSIDIAN_IMAGE_RE.sub(replace_obsidian_img, content)
    return new_content, changes


# ============================================================
# FIX 5: Convert Obsidian wikilink [[page]] → [page](page.md)
# ============================================================

def fix_obsidian_wikilinks(content, md_file_path):
    """
    Chuyển [[PageName]] → [PageName](PageName.md)
    Chuyển [[PageName|Alias]] → [Alias](PageName.md)
    Chuyển [[PageName#Heading]] → [PageName](PageName.md#heading)
    Bỏ qua nếu đã được xử lý bởi fix_obsidian_image_embeds (image embed).
    """
    changes = 0

    # Lấy danh sách tất cả file .md trong repo để tìm file đích
    md_files = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian')]
        for f in files:
            if f.endswith('.md'):
                key = os.path.splitext(f)[0].lower()
                full = os.path.join(root, f)
                if key not in md_files:
                    md_files[key] = full

    def replace_wikilink(match):
        nonlocal changes
        page = match.group(1).strip()      # tên page
        heading = match.group(2)           # heading sau #
        alias = match.group(3)             # alias sau |

        display = alias.strip() if alias else page
        page_key = page.lower()

        # Tính đường dẫn đến file md đích
        if page_key in md_files:
            target_full = md_files[page_key]
            md_dir = os.path.dirname(md_file_path)
            rel = os.path.relpath(target_full, md_dir).replace('\\', '/')
            encoded_rel = url_encode_path(rel)
        else:
            # File không tồn tại → dùng tên file đơn giản
            encoded_rel = url_encode_path(page + '.md')

        if heading:
            # Chuẩn hoá heading anchor: chữ thường, thay space → -
            anchor = heading.strip().lower().replace(' ', '-')
            anchor = re.sub(r'[^\w\-]', '', anchor)
            encoded_rel = f'{encoded_rel}#{anchor}'

        changes += 1
        return f'[{display}]({encoded_rel})'

    new_content = OBSIDIAN_LINK_RE.sub(replace_wikilink, content)
    return new_content, changes


# ============================================================
# FIX 6: Convert Obsidian callouts → GitHub-compatible blockquote
# ============================================================

def fix_obsidian_callouts(content):
    """
    Chuyển Obsidian callout:
        > [!NOTE] Title
        > body text
    Thành GitHub blockquote với label in đậm:
        > **📝 NOTE: Title**
        > body text
    """
    changes = 0
    lines = content.split('\n')
    result = []

    # Pattern: dòng bắt đầu bằng > [!TYPE] optional_title
    CALLOUT_RE = re.compile(r'^(>\s*)\[!(\w+)\]([-+]?)(?:\s+(.*))?$')

    i = 0
    while i < len(lines):
        line = lines[i]
        m = CALLOUT_RE.match(line)
        if m:
            prefix = m.group(1)    # "> " phần blockquote
            ctype = m.group(2).lower()
            # group(3) là foldable marker (- hoặc +), bỏ qua
            title = (m.group(4) or '').strip()

            emoji, label = CALLOUT_MAP.get(ctype, ('📌', ctype.upper()))

            if title:
                header = f'{prefix}**{emoji} {label}: {title}**'
            else:
                header = f'{prefix}**{emoji} {label}**'

            result.append(header)
            changes += 1
        else:
            result.append(line)
        i += 1

    return '\n'.join(result), changes


# ============================================================
# MAIN: Chạy tất cả fix cho toàn bộ file .md trong repo
# ============================================================

def main():
    all_images = get_all_image_files()
    print(f'[*] Repo root    : {REPO_ROOT}')
    print(f'[*] Image dir    : {IMAGE_DIR}')
    print(f'[*] Images found : {len(all_images)}')
    print()

    file_count = 0
    total_img_standard = 0
    total_img_obsidian = 0
    total_wikilinks = 0
    total_callouts = 0
    total_highlights = 0

    for root, dirs, files in os.walk(REPO_ROOT):
        # Bỏ qua .git, .obsidian
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian')]

        for file in files:
            if not file.endswith('.md'):
                continue

            path = os.path.join(root, file)
            rel_path = os.path.relpath(path, REPO_ROOT)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # FIX 4 trước: chuyển ![[...]] → ![](...) để FIX 1 có thể pick up
                content, n4 = fix_obsidian_image_embeds(content, path, all_images)
                total_img_obsidian += n4

                # FIX 1: sửa link ảnh chuẩn
                content, n1 = fix_image_links(content, path, all_images)
                total_img_standard += n1

                # FIX 5: chuyển wikilink [[...]]
                content, n5 = fix_obsidian_wikilinks(content, path)
                total_wikilinks += n5

                # FIX 6: chuyển Obsidian callout
                content, n6 = fix_obsidian_callouts(content)
                total_callouts += n6

                # FIX 2: thêm dòng trống giữa các block
                content = fix_markdown_newlines(content)

                # FIX 3: ==text== → màu xanh
                content, n3 = fix_highlight_green(content)
                total_highlights += n3

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

                status = []
                if n4:
                    status.append(f'{n4} obsidian img embed(s)')
                if n1:
                    status.append(f'{n1} image link(s)')
                if n5:
                    status.append(f'{n5} wikilink(s)')
                if n6:
                    status.append(f'{n6} callout(s)')
                if n3:
                    status.append(f'{n3} highlight(s)')

                if status:
                    print(f'  [FIXED] {rel_path}')
                    for s in status:
                        print(f'          • {s}')
                else:
                    print(f'  [OK]    {rel_path}')

                file_count += 1
            except Exception as e:
                print(f'  [ERR]   {rel_path}: {e}')

    print()
    print('=' * 60)
    print(f'Done! Processed {file_count} file(s):')
    print(f'  • {total_img_obsidian} Obsidian image embed(s)  ![[...]] converted')
    print(f'  • {total_img_standard}  standard image link(s)   ![](path) fixed')
    print(f'  • {total_wikilinks}  wikilink(s)              [[...]] converted')
    print(f'  • {total_callouts}  callout(s)               > [!TYPE] converted')
    print(f'  • {total_highlights}  highlight(s)             ==text== converted')


if __name__ == '__main__':
    main()