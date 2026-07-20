import re

with open('layer_board_widget.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

pattern = re.compile(r'self\.tr\("([^"]+)"\)|self\.tr\(\'([^\']+)\'\)')

for idx, line in enumerate(lines):
    for m in pattern.finditer(line):
        text = m.group(1) or m.group(2)
        print(f'L{idx+1:4d}: {text}')
