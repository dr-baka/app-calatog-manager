from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.simple_tag(takes_context=True)
def lang(context, id_text, en_text):
    request = context.get('request')
    language = getattr(request, 'LANGUAGE_CODE', 'id')
    return en_text if language == 'en' else id_text

@register.filter
def verbose_name(obj):
    if hasattr(obj, '_meta'):
        return obj._meta.verbose_name.title()
    # If it's a class
    if hasattr(obj, 'model') and hasattr(obj.model, '_meta'):
        return obj.model._meta.verbose_name.title()
    return str(obj).title()

@register.filter
def verbose_name_plural(obj):
    if hasattr(obj, '_meta'):
        return obj._meta.verbose_name_plural.title()
    if hasattr(obj, 'model') and hasattr(obj.model, '_meta'):
        return obj.model._meta.verbose_name_plural.title()
    return str(obj).title()


@register.filter
def markdownify(value):
    if not value:
        return ''

    escaped_value = escape(value)
    try:
        import markdown

        extensions = ['fenced_code', 'sane_lists', 'tables']
        if not _has_markdown_table(value):
            extensions.append('nl2br')

        html = markdown.markdown(
            escaped_value,
            extensions=extensions,
            output_format='html5',
        )
    except ImportError:
        html = _basic_markdown(escaped_value)

    return mark_safe(html)


def _has_markdown_table(value):
    lines = [line.strip() for line in value.splitlines()]
    return any(
        line.startswith('|') and set(line.replace('|', '').replace(':', '').strip()) <= {'-'}
        for line in lines
    )


def _basic_markdown(value):
    lines = value.splitlines()
    html_lines = []
    in_list = False
    index = 0

    while index < len(lines):
        line = lines[index]
        if _is_table_header(lines, index):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            headers = _split_table_row(lines[index])
            index += 2
            rows = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                rows.append(_split_table_row(lines[index]))
                index += 1
            html_lines.append(_render_basic_table(headers, rows))
            continue
        if line.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith(('- ', '* ')):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        elif line.strip():
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<p>{line}</p>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
        index += 1

    if in_list:
        html_lines.append('</ul>')

    html = '\n'.join(html_lines)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    return html


def _is_table_header(lines, index):
    if index + 1 >= len(lines):
        return False

    header = lines[index].strip()
    separator = lines[index + 1].strip()
    if not header.startswith('|') or not separator.startswith('|'):
        return False

    separator_cells = _split_table_row(separator)
    return bool(separator_cells) and all(
        set(cell.replace(':', '').strip()) <= {'-'} and '-' in cell
        for cell in separator_cells
    )


def _split_table_row(line):
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def _render_basic_table(headers, rows):
    header_html = ''.join(f'<th>{header}</th>' for header in headers)
    row_html = []
    for row in rows:
        cells = ''.join(f'<td>{cell}</td>' for cell in row)
        row_html.append(f'<tr>{cells}</tr>')
    return f'<table><thead><tr>{header_html}</tr></thead><tbody>{"".join(row_html)}</tbody></table>'
