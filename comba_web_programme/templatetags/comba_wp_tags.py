__author__ = 'michel'
from django import template
from django.utils.translation import get_language
import os
register = template.Library()

@register.filter
def formatdate(d):
    locale = get_language()
    if locale == "de":
        return d.strftime("%d.%m.%Y %H:%M")
    else:
        return d.strftime("%Y-%m-%d %H:%M")

@register.filter
def basename(location):
    return os.path.basename(str(location).replace('file://',''))
