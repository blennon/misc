#!/usr/bin/env python3
"""Convert markdown files to EPUB-compatible XHTML."""

import re
import os

def md_to_xhtml(md_content, part_num):
    """Convert markdown to XHTML."""

    # Basic HTML escaping
    content = md_content

    # Convert headers
    # H1 - Part titles
    content = re.sub(r'^# (PART [IVX]+:.*)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)

    # H2 - Chapter titles with IDs
    chapter_num = [0]
    def replace_h2(match):
        chapter_num[0] += 1
        title = match.group(1)
        return f'<h2 id="ch{chapter_num[0]}">{title}</h2>'
    content = re.sub(r'^## (Chapter \d+:.*)$', replace_h2, content, flags=re.MULTILINE)

    # Other H2s
    content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)

    # H3
    content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)

    # Bold
    content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)

    # Italic
    content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)

    # Block quotes
    lines = content.split('\n')
    new_lines = []
    in_blockquote = False
    for line in lines:
        if line.startswith('> '):
            if not in_blockquote:
                new_lines.append('<blockquote>')
                in_blockquote = True
            new_lines.append(f'<p>{line[2:]}</p>')
        else:
            if in_blockquote:
                new_lines.append('</blockquote>')
                in_blockquote = False
            new_lines.append(line)
    if in_blockquote:
        new_lines.append('</blockquote>')
    content = '\n'.join(new_lines)

    # Lists
    lines = content.split('\n')
    new_lines = []
    in_list = False
    list_type = None
    for line in lines:
        # Unordered list
        if re.match(r'^- (.+)$', line):
            if not in_list or list_type != 'ul':
                if in_list:
                    new_lines.append(f'</{list_type}>')
                new_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            match = re.match(r'^- (.+)$', line)
            new_lines.append(f'<li>{match.group(1)}</li>')
        # Numbered list
        elif re.match(r'^\d+\. (.+)$', line):
            if not in_list or list_type != 'ol':
                if in_list:
                    new_lines.append(f'</{list_type}>')
                new_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            match = re.match(r'^\d+\. (.+)$', line)
            new_lines.append(f'<li>{match.group(1)}</li>')
        else:
            if in_list and line.strip() and not line.startswith(' '):
                new_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            new_lines.append(line)
    if in_list:
        new_lines.append(f'</{list_type}>')
    content = '\n'.join(new_lines)

    # Horizontal rules
    content = re.sub(r'^---+$', '<hr/>', content, flags=re.MULTILINE)

    # Paragraphs - wrap text blocks in <p> tags
    lines = content.split('\n')
    new_lines = []
    para_buffer = []

    for line in lines:
        stripped = line.strip()
        # Skip if it's already HTML or empty
        if (stripped.startswith('<') or
            stripped == '' or
            stripped.startswith('#')):
            if para_buffer:
                new_lines.append('<p>' + ' '.join(para_buffer) + '</p>')
                para_buffer = []
            if stripped:
                new_lines.append(line)
        else:
            para_buffer.append(stripped)

    if para_buffer:
        new_lines.append('<p>' + ' '.join(para_buffer) + '</p>')

    content = '\n'.join(new_lines)

    # Clean up empty paragraphs
    content = re.sub(r'<p>\s*</p>', '', content)

    # Wrap in XHTML
    xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>Part {part_num}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{content}
</body>
</html>'''

    return xhtml


def main():
    content_dir = '/home/user/misc/ctmu-book/content'
    epub_dir = '/home/user/misc/ctmu-book/epub/OEBPS'

    parts = [
        ('part1-foundations.md', 'part1.xhtml', 'I'),
        ('part2-western-philosophy.md', 'part2.xhtml', 'II'),
        ('part3-eastern-philosophy.md', 'part3.xhtml', 'III'),
        ('part4-physics.md', 'part4.xhtml', 'IV'),
        ('part5-ctmu.md', 'part5.xhtml', 'V'),
        ('part6-synthesis.md', 'part6.xhtml', 'VI'),
        ('part7-appendices.md', 'part7.xhtml', 'Appendices'),
        ('part8-extended-discussions.md', 'part8.xhtml', 'Extended'),
    ]

    for md_file, xhtml_file, part_num in parts:
        md_path = os.path.join(content_dir, md_file)
        xhtml_path = os.path.join(epub_dir, xhtml_file)

        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        xhtml_content = md_to_xhtml(md_content, part_num)

        with open(xhtml_path, 'w', encoding='utf-8') as f:
            f.write(xhtml_content)

        print(f'Converted {md_file} -> {xhtml_file}')


if __name__ == '__main__':
    main()
