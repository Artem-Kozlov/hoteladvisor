from django import template

register = template.Library()

@register.filter
def range_list(value):
    return range(int(value))