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

        html = markdown.markdown(
            escaped_value,
            extensions=['fenced_code', 'nl2br', 'sane_lists'],
            output_format='html5',
        )
    except ImportError:
        html = _basic_markdown(escaped_value)

    return mark_safe(html)


def _basic_markdown(value):
    lines = value.splitlines()
    html_lines = []
    in_list = False

    for line in lines:
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

    if in_list:
        html_lines.append('</ul>')

    html = '\n'.join(html_lines)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    return html
