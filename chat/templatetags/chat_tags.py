from django import template

from ..models import Room

register = template.Library()


@register.simple_tag(takes_context=True)
def show_interlocutor_name(context, room_id, user_id):
    return Room.get_interlocutor(room_id=room_id, user_id=user_id).username
