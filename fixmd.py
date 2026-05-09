import os

def fix_markdown_newlines(content):
    lines = content.split('\n')
    result = []
    in_code_block = False

    for i, line in enumerate(lines):
        # Toggle code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block

        result.append(line)

        # Chỉ thêm dòng trống khi KHÔNG trong code block
        if (not in_code_block and
            i < len(lines) - 1 and
            line.strip() and
            lines[i+1].strip() and
            not lines[i+1].strip().startswith('```')):
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
