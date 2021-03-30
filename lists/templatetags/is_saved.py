from django import template
from lists import models as list_models

register = template.Library()


@register.simple_tag(takes_context=True)
def is_saved(context, room):
    user = context.request.user
    if user.id is not None:
        the_list = list_models.List.objects.get_or_none(user=user)
        if the_list is None:
            return False
    else:
        return False
    return room in the_list.rooms.all()
