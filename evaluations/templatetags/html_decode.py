import datetime
import json
from decimal import Decimal
from django import template
from django.http import QueryDict
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    if s:
        htmlCodes = {
                ("¿", '&iquest;'),
                ("'", '&#39;'),
                ('"', '&quot;'),
                ('>', '&gt;'),
                ('<', '&lt;'),
                ('ó', '&oacute;'),
                ('Ó', '&Oacute;'),
                ('Á', '&Aacute;'),
                ('É', '&Eacute;'),
                ('Í', '&Iacute;'),
                ('Ú', '&Uacute;'),
                ('á', '&aacute;'),
                ('é', '&eacute;'),
                ('í', '&iacute;'),
                ('ó', '&oacute;'),
                ('ú', '&uacute;'),
                ('Ñ', '&Ntilde;'),
                ('ñ', '&ntilde;'),
                ('ñ', '&ntilde;'),
                ('❤️','&#9829;'),
                ('❤','&#9825;'),
                ('“','&#8220;'),
                ('”','&#8221;'),
                ('!','&#33;'),
                ('¡','&#161;'),
                }
        for code in htmlCodes:
            s = s.replace(code[0], code[1])
    return str(s)
