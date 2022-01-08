# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.simple_tag
def get_proper_elided_page_range(p, on_each_side=3, on_ends=2):
    return p.paginator.get_elided_page_range(number=p.number,
                                             on_each_side=on_each_side,
                                             on_ends=on_ends)
