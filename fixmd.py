import os

def fix_markdown_newlines(content):
    lines = content.split('\n')
    result = []
    in_block = False  # Đang trong bất kỳ block nào không được thêm dòng trống

    # Các pattern bắt đầu/kết thúc block (toggle)
    TOGGLE_BLOCKS = [
        '```',   # Code block
        '$$',    # Math block
        '~~~',   # Alt code block
    ]

    # Các pattern prefix - dòng bắt đầu bằng ký tự này thì KHÔNG thêm dòng trống sau
    NO_BREAK_PREFIXES = [
        '#',     # Heading (không thêm dòng trống giữa các heading liên tiếp)
        '- ',    # Unordered list
        '* ',    # Unordered list alt
        '+ ',    # Unordered list alt
        '> ',    # Blockquote
        '| ',    # Table row
        '|',     # Table row (không có space)
        '  ',    # Indented (continuation)
    ]

    # Numbered list: 1. 2. 3. ...
    import re
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

        # Nếu đang trong block → không thêm dòng trống
        if toggle_stack:
            continue

        # Nếu dòng hiện tại hoặc dòng tiếp theo rỗng → không thêm
        if not stripped or not next_stripped:
            continue

        # Nếu dòng tiếp theo là toggle block → không thêm
        if any(next_stripped.startswith(tok) for tok in TOGGLE_BLOCKS):
            continue

        # Nếu dòng hiện tại là toggle block → không thêm
        if any(stripped.startswith(tok) for tok in TOGGLE_BLOCKS):
            continue

        # Nếu cả 2 dòng đều là list item cùng loại → không thêm
        cur_is_list = any(stripped.startswith(p) for p in ['- ', '* ', '+ ']) or bool(NUMBERED_LIST.match(stripped))
        next_is_list = any(next_stripped.startswith(p) for p in ['- ', '* ', '+ ']) or bool(NUMBERED_LIST.match(next_stripped))
        if cur_is_list and next_is_list:
            continue

        # Nếu cả 2 dòng đều là table row → không thêm
        if stripped.startswith('|') and next_stripped.startswith('|'):
            continue

        # Nếu cả 2 dòng đều là blockquote → không thêm
        if stripped.startswith('>') and next_stripped.startswith('>'):
            continue

        # Nếu dòng tiếp theo là separator table (---|---) → không thêm
        if re.match(r'^\|?[\s\-\|:]+\|?$', next_stripped):
            continue

        # Thêm dòng trống
        result.append('')

    return '\n'.join(result)


folder = r'/mnt/c/Users/lethi/Downloads/RE'
count = 0

for root, dirs, files in os.walk(folder):
    for file in files:
        if file.endswith('.md'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                fixed = fix_markdown_newlines(content)

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(fixed)

                print(f"✓ Fixed: {path}")
                count += 1
            except Exception as e:
                print(f"✗ Error {path}: {e}")

print(f"\nDone! Fixed {count} file(s).")