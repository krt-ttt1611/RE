#!/usr/bin/env python3
"""
fixmd.py - Tự sửa & format lại file Markdown từ Obsidian để GitHub đọc được hoàn chỉnh.

Cách dùng (chạy ở BẤT KỲ folder nào, kể cả copy file này đi nơi khác):
    python fixmd.py                  # xử lý folder hiện tại (cwd) + mọi folder con
    python fixmd.py D:/notes         # xử lý folder chỉ định
    python fixmd.py a.md docs/       # có thể truyền nhiều file/folder
    python fixmd.py D:/notes --dry-run   # chỉ báo cáo, không ghi file

Script an toàn khi chạy nhiều lần (idempotent): chạy lại không làm hỏng kết quả cũ.

Các việc script làm:
  1. ![[img.png|300]]          -> ![img.png](đường/dẫn/img.png)   (relative, %20)
  2. ![alt](đường dẫn sai)     -> sửa lại đúng đường dẫn tới ảnh thật trong repo
  3. [[Page|Alias#Heading]]    -> [Alias](Page.md#heading)
  4. > [!type] Title (Obsidian) -> GitHub Alerts (> [!NOTE] ...)
  5. ==text==                  -> chữ màu xanh (MathJax, GitHub + Obsidian đều hiển thị)
  6. %%comment%%               -> xoá (Obsidian comment, GitHub sẽ hiện nguyên văn)
  7. Thêm dòng trống giữa các block để GitHub render đúng (bảng, list, quote...)
Không đụng vào: code block, inline code, công thức $...$ / $$...$$, YAML frontmatter.
"""
import os
import re
import sys
from urllib.parse import unquote, quote

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SKIP_DIRS = {'.git', '.obsidian', '.trash', 'node_modules', '.venv', 'venv', '__pycache__'}
IMG_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp', '.avif')

# ![alt](path) - cho phép path có khoảng trắng và 1 cấp ngoặc đơn lồng nhau
IMAGE_LINK_RE = re.compile(r'(!\[[^\]]*\])\(((?:[^()\n]|\([^()\n]*\))+)\)')
# ![[file|alt]] (ảnh hoặc note)
EMBED_RE = re.compile(r'!\[\[([^\]|#]+?)(?:#([^\]|]*))?(?:\\?\|([^\]]*))?\]\]')
# [[page#heading|alias]]  (cho phép \| trong bảng)
WIKILINK_RE = re.compile(r'(?<!!)\[\[([^\]|#]+?)(?:#([^\]|]*?))?(?:\\?\|([^\]]*?))?\]\]')
CALLOUT_RE = re.compile(r'^((?:>[ \t]*)+)\[!(\w+)\][-+]?(?:[ \t]+(.*))?$')
COMMENT_RE = re.compile(r'%%[\s\S]*?%%')
HIGHLIGHT_RE = re.compile(r'==(?=\S)([^=\n]+?)(?<=\S)==')
FRONTMATTER_RE = re.compile(r'\A---[ \t]*\n[\s\S]*?\n(?:---|\.\.\.)[ \t]*(?:\n|\Z)')

# Obsidian callout type -> (GitHub alert | None, emoji, label)
CALLOUT_MAP = {
    'note': ('NOTE', '📝'), 'info': ('NOTE', 'ℹ️'), 'todo': ('NOTE', '📋'),
    'question': ('NOTE', '❓'), 'help': ('NOTE', '❓'), 'faq': ('NOTE', '❓'),
    'abstract': ('NOTE', '📄'), 'summary': ('NOTE', '📄'), 'tldr': ('NOTE', '📄'),
    'tip': ('TIP', '💡'), 'hint': ('TIP', '💡'), 'success': ('TIP', '✅'),
    'check': ('TIP', '✅'), 'done': ('TIP', '✅'),
    'important': ('IMPORTANT', '❗'),
    'warning': ('WARNING', '⚠️'), 'caution': ('WARNING', '⚠️'), 'attention': ('WARNING', '⚠️'),
    'danger': ('CAUTION', '🔴'), 'error': ('CAUTION', '❌'), 'failure': ('CAUTION', '❌'),
    'fail': ('CAUTION', '❌'), 'missing': ('CAUTION', '❌'), 'bug': ('CAUTION', '🐛'),
    'quote': (None, '📌'), 'cite': (None, '📌'), 'example': (None, '📖'),
}
GITHUB_ALERTS = {'NOTE', 'TIP', 'IMPORTANT', 'WARNING', 'CAUTION'}


# ============================================================
# Index file trong repo
# ============================================================

class Index:
    def __init__(self, root):
        self.root = root
        self.images = {}   # tên lower -> full path
        self.files = {}    # tên lower (kèm đuôi) -> full path (mọi loại file)
        self.notes = {}    # tên note lower (không đuôi) -> full path .md
        for r, dirs, files in os.walk(root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                full = os.path.join(r, f)
                low = f.lower()
                self.files.setdefault(low, full)
                if low.endswith(IMG_EXT):
                    # ưu tiên ảnh nằm trong folder tên "image"/"images"/"attachments"
                    pref = os.path.basename(r).lower() in ('image', 'images', 'attachments', 'assets')
                    if low not in self.images or pref:
                        self.images[low] = full
                elif low.endswith('.md'):
                    self.notes.setdefault(os.path.splitext(low)[0], full)


def enc(path):
    """Encode URL-safe cho từng đoạn path (space -> %20, giữ / . ..)."""
    return '/'.join(p if p in ('.', '..') else quote(p, safe='') for p in path.split('/'))


def rel_link(md_path, target):
    return enc(os.path.relpath(target, os.path.dirname(md_path)).replace('\\', '/'))


def is_external(p):
    return bool(re.match(r'^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|#|//)', p.strip()))


# ============================================================
# Bảo vệ vùng không được sửa
# ============================================================

def protect(content):
    blocks = []

    def save(m):
        blocks.append(m.group(0))
        return f'\uE000{len(blocks) - 1}\uE001'

    t = re.sub(r'(?m)^[ \t]*(`{3,}|~{3,})[^\n]*\n[\s\S]*?(?:^[ \t]*\1[`~]*[ \t]*$|\Z)', save, content)
    t = re.sub(r'\$\$[\s\S]+?\$\$', save, t)
    t = re.sub(r'(`+)(?!`)[^\n]*?(?<!`)\1(?!`)', save, t)
    t = re.sub(r'(?<![\\$\w])\$(?![\s$])[^$\n]+?(?<![\s\\])\$(?![\d$])', save, t)
    return t, blocks


def restore(t, blocks):
    # lặp vì placeholder có thể lồng nhau
    for _ in range(3):
        t = re.sub(r'\uE000(\d+)\uE001', lambda m: blocks[int(m.group(1))], t)
    return t


# ============================================================
# Các bước sửa
# ============================================================

def fix_embeds(t, md, idx, stats):
    """![[file|alt]] -> ![alt](path); ![[note]] -> [note](note.md)"""
    def rep(m):
        name = m.group(1).strip()
        heading, extra = m.group(2), (m.group(3) or '').strip()
        low = os.path.basename(name).lower()
        stats['embed'] += 1
        if low.endswith(IMG_EXT):
            alt = extra if extra and not re.fullmatch(r'\d+(x\d+)?', extra) else os.path.basename(name)
            target = idx.images.get(low)
            link = rel_link(md, target) if target else enc(name.replace('\\', '/'))
            return f'![{alt}]({link})'
        # embed file khác (pdf, note...)
        if low.endswith('.md'):
            low = low[:-3]
            name = name[:-3]
        target = idx.notes.get(low)
        if target:
            link = rel_link(md, target)
        elif os.path.basename(name).lower() in idx.files:
            link = rel_link(md, idx.files[os.path.basename(name).lower()])
        else:
            link = enc(name + '.md')
        if heading:
            link += '#' + anchor(heading)
        return f'[{extra or os.path.basename(name)}]({link})'
    return EMBED_RE.sub(rep, t)


def fix_image_links(t, md, idx, stats):
    def rep(m):
        alt, raw = m.group(1), m.group(2).strip()
        title = ''
        tm = re.match(r'^(.*?)(\s+"[^"]*")$', raw)
        if tm:
            raw, title = tm.group(1), tm.group(2)
        if raw.startswith('<') and raw.endswith('>'):
            raw = raw[1:-1]
        if is_external(raw):
            return m.group(0)
        decoded = unquote(raw.split('?')[0])
        cand = os.path.normpath(os.path.join(os.path.dirname(md), decoded))
        if os.path.isfile(cand):               # đường dẫn đã đúng -> chỉ encode
            new = rel_link(md, cand)
        else:
            target = idx.images.get(os.path.basename(decoded).lower())
            if not target:
                new = enc(decoded.replace('\\', '/'))   # không thấy ảnh: chỉ encode space
            else:
                new = rel_link(md, target)
        out = f'{alt}({new}{title})'
        if out != m.group(0):
            stats['image'] += 1
        return out
    return IMAGE_LINK_RE.sub(rep, t)


def anchor(h):
    a = h.strip().lower().replace(' ', '-')
    return re.sub(r'[^\w\-]', '', a)


def fix_wikilinks(t, md, idx, stats):
    def rep(m):
        page = m.group(1).strip().replace('\\', '/')
        heading, alias = m.group(2), m.group(3)
        base = os.path.basename(page)
        low = base.lower()
        if low.endswith('.md'):
            low = low[:-3]
        if low in idx.notes:
            link = rel_link(md, idx.notes[low])
        elif base.lower() in idx.files:           # pdf, ảnh, file đính kèm khác
            link = rel_link(md, idx.files[base.lower()])
        else:
            link = enc(page if page.lower().endswith('.md') else page + '.md')
        if heading and heading.strip():
            link += '#' + anchor(heading.lstrip('^'))
        display = (alias.strip() if alias and alias.strip() else
                   (page + (' > ' + heading.strip() if heading and heading.strip() else '')))
        display = display.replace('[', '\\[').replace(']', '\\]')
        stats['wikilink'] += 1
        return f'[{display}]({link})'
    return WIKILINK_RE.sub(rep, t)


def fix_callouts(t, stats):
    lines = t.split('\n')
    out = []
    for line in lines:
        m = CALLOUT_RE.match(line)
        if not m:
            out.append(line)
            continue
        prefix = m.group(1).rstrip() + ' '
        ctype = m.group(2).lower()
        title = (m.group(3) or '').strip()
        alert, emoji = CALLOUT_MAP.get(ctype, ('NOTE', '📌'))
        if ctype.upper() in GITHUB_ALERTS:
            alert = ctype.upper()
        default_title = ctype.capitalize()
        nested = prefix.count('>') > 1
        if alert and not nested:
            new = f'{prefix}[!{alert}]'
            out.append(new)
            if title and title.lower() != alert.lower():
                out.append(f'{prefix}**{title}**')
                out.append(prefix.rstrip())
            if (new != line):
                stats['callout'] += 1
        else:
            out.append(f'{prefix}**{emoji} {title or default_title}**')
            out.append(prefix.rstrip())
            stats['callout'] += 1
    return '\n'.join(out)


def fix_highlight(t, stats):
    def tex(s):
        s = re.sub(r'([\\{}$%&#_^~])', lambda m: {
            '\\': r'\backslash ', '~': r'\sim ', '^': r'\^{}'}.get(m.group(1), '\\' + m.group(1)), s)
        return s

    def rep(m):
        stats['highlight'] += 1
        inner = re.sub(r'(\*\*|__|\*|`)', '', m.group(1))
        return '$\\color{green}{\\text{' + tex(inner) + '}}$'
    return HIGHLIGHT_RE.sub(rep, t)


def fix_newlines(content):
    """Chèn dòng trống giữa các block liền nhau (GitHub cần), không đụng code/math."""
    lines = content.split('\n')
    res = []
    fence = None          # (char, len)
    in_math = False
    NUM = re.compile(r'^\d+[.)]\s')
    BUL = ('- ', '* ', '+ ')

    def is_list(s):
        return s.startswith(BUL) or bool(NUM.match(s))

    for i, line in enumerate(lines):
        s = line.strip()
        fm = re.match(r'^(`{3,}|~{3,})', s)
        if fence:
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= fence[1] and s.strip(fence[0]) == '':
                fence = None
            res.append(line)
            continue
        if in_math:
            if '$$' in s:
                in_math = False
            res.append(line)
            continue
        opened_fence = False
        if fm:
            fence = (fm.group(1)[0], len(fm.group(1)))
            opened_fence = True
        elif s.startswith('$$') and s.count('$$') == 1:
            in_math = True
            opened_fence = True

        # blank line TRƯỚC khi mở code/math block nếu dòng trước có chữ
        if opened_fence and res and res[-1].strip() and not is_list(res[-1].strip()) \
                and not res[-1].startswith((' ', '\t')):
            res.append('')
        res.append(line)
        if opened_fence or i == len(lines) - 1:
            continue

        nxt = lines[i + 1]
        ns = nxt.strip()
        if not s or not ns:
            continue
        if re.match(r'^(`{3,}|~{3,}|\$\$)', ns) and (is_list(s) or line.startswith((' ', '\t'))):
            continue
        if line.endswith(('  ', '\\')) or '<br' in s.lower():
            continue
        if is_list(s) and (is_list(ns) or nxt.startswith((' ', '\t'))):
            continue
        if line.startswith((' ', '\t')) and nxt.startswith((' ', '\t')):
            continue
        if s.startswith('|') and ns.startswith('|'):
            continue
        if s.startswith('>') and ns.startswith('>'):
            continue
        if re.fullmatch(r'=+|-{2,}', ns) and not s.startswith(('|', '>', '#')):
            continue     # setext heading
        if re.match(r'^<\/?[a-zA-Z]', s) and re.match(r'^<\/?[a-zA-Z]', ns):
            continue     # HTML liền nhau
        res.append('')
    # đóng: gộp >2 dòng trống liên tiếp (ngoài code) thành 1
    out, blank = [], 0
    fence = None
    for line in res:
        s = line.strip()
        fm = re.match(r'^(`{3,}|~{3,})', s)
        if fence:
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= fence[1] and s.strip(fence[0]) == '':
                fence = None
            out.append(line)
            continue
        if fm:
            fence = (fm.group(1)[0], len(fm.group(1)))
        if not s:
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(line)
    return '\n'.join(out)


# ============================================================
# Xử lý 1 file
# ============================================================

def process(content, md, idx, stats):
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    # NUL/control char làm GitHub không render được file -> thay bằng text
    content = content.replace('\x00', '\\0')
    content = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f]', '', content)
    front = ''
    fm = FRONTMATTER_RE.match(content)
    if fm:
        front, content = fm.group(0), content[fm.end():]

    t, blocks = protect(content)
    t = COMMENT_RE.sub('', t)
    t = fix_embeds(t, md, idx, stats)
    t = fix_image_links(t, md, idx, stats)
    t = fix_wikilinks(t, md, idx, stats)
    t = fix_callouts(t, stats)
    t = fix_highlight(t, stats)
    t = restore(t, blocks)
    t = fix_newlines(t)
    t = '\n'.join(l.rstrip(' \t') if not l.endswith('  ') or not l.strip() else l for l in t.split('\n'))
    t = t.rstrip('\n') + '\n' if t.strip() else t
    return front + t


def collect(paths):
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            if p.lower().endswith('.md'):
                yield p
            continue
        for r, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if f.lower().endswith('.md'):
                    yield os.path.join(r, f)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    targets = args or [os.getcwd()]
    for t in targets:
        if not os.path.exists(t):
            print(f'[ERR] Không tồn tại: {t}')
            return 1
    # root để tìm ảnh/note: folder được chỉ định (hoặc folder cha chứa .obsidian/.git nếu có)
    first = os.path.abspath(targets[0])
    root = first if os.path.isdir(first) else os.path.dirname(first)
    probe = root
    while True:
        if os.path.isdir(os.path.join(probe, '.obsidian')) or os.path.isdir(os.path.join(probe, '.git')):
            root = probe
            break
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent

    idx = Index(root)
    print(f'[*] Root   : {root}')
    print(f'[*] Ảnh    : {len(idx.images)} | Note: {len(idx.notes)}' + ('  (DRY RUN)' if dry else ''))
    total = {'embed': 0, 'image': 0, 'wikilink': 0, 'callout': 0, 'highlight': 0}
    n_files = n_changed = 0
    for path in collect(targets):
        rel = os.path.relpath(path, root)
        try:
            with open(path, 'r', encoding='utf-8-sig', newline='') as f:
                old = f.read()
            stats = {k: 0 for k in total}
            new = process(old, path, idx, stats)
            n_files += 1
            for k in total:
                total[k] += stats[k]
            if new != old.replace('\r\n', '\n'):
                n_changed += 1
                if not dry:
                    with open(path, 'w', encoding='utf-8', newline='\n') as f:
                        f.write(new)
                det = ', '.join(f'{v} {k}' for k, v in stats.items() if v)
                print(f'  [FIXED] {rel}' + (f'  ({det})' if det else '  (format)'))
            else:
                print(f'  [OK]    {rel}')
        except Exception as e:
            print(f'  [ERR]   {rel}: {e}')
    print('=' * 60)
    print(f'Xong: {n_files} file, {n_changed} file được sửa.')
    print('  ' + ' | '.join(f'{k}: {v}' for k, v in total.items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())