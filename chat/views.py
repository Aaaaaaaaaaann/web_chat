from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm, UsernameSearchForm
from .models import CustomUser, Message, Room


def is_banned(func):
    def inner(*args, **kwargs):
        if args[0].user.is_authenticated:
            user = CustomUser.objects.get(pk=args[0].user.pk)
            if not user.is_active:
                return render(*args, 'chat/banned.html')
        return func(*args, **kwargs)
    return inner


@login_required
@is_banned
def start_page(request):
    # return render(request, 'chat/start_page.html')
    return index(request)


@login_required
@is_banned
def index(request):
    form = UsernameSearchForm()
    # Collect the chats a user participates in.
    user_rooms_ids = [room.pk for room in Room.objects.filter(
        users__contains=[request.user.pk])]
    # Collect the last message from every chat.
    last_messages = []
    for room_id in user_rooms_ids:
        try:
            last_messages.append(Message.objects.filter(
                room_id=room_id).latest('date'))
        # If a chat room was created, but no message was sent in it,
        # this chat room won't appear in the list.
        except ObjectDoesNotExist:
            continue
    return render(request, 'chat/index.html', {
        'form': form,
        'last_messages': last_messages
    })


@login_required
@is_banned
def user_search(request):
    if 'username' in request.GET:
        form = UsernameSearchForm(request.GET)
        if form.is_valid():
            username = request.GET['username']
            user = CustomUser.objects.get(username=username)
            # If a user searches for himself, show an error.
            if user == request.user:
                error_message = 'You can\'t talk to yourself, sorry.'
                return render(request, 'chat/index.html', {
                    'form': form,
                    'error_message': error_message
                })
            # Search for the chat room where both users participate in.
            room, created = Room.objects.get_or_create(
                users__contains=[user.id, request.user.id],
                defaults={'users': [user.id, request.user.id]})
            return HttpResponseRedirect(reverse(
                'chat:chat',
                kwargs={'room_id': room.id}
            ))
        else:
            return render(request, 'chat/index.html', {'form': form})
    else:
        form = UsernameSearchForm()
        return render(request, 'chat/index.html', {'form': form})


@login_required
@is_banned
def chat(request, room_id):
    user = request.user
    # Prevent a user from trying to get to not his chat room
    # if he tries to put its number directly to the link.
    try:
        chat_room = Room.objects.get(pk=room_id)
    # Sow an error even if the chat room doesn't exist.
    except ObjectDoesNotExist:
        return render(request, 'chat/access_prohibited.html')
    else:
        # If a user doesn't participate in the chat room,
        # show an error.
        if user.pk not in chat_room.users:
            return render(request, 'chat/access_prohibited.html')
        # If he participates in the chat,
        # return history and interlocutor's name.
        interlocutor_id = set(chat_room.users) - {user.pk}
        interlocutor = CustomUser.objects.get(pk=interlocutor_id.pop())
        # Prevent a user from connecting with a banned user.
        if not interlocutor.is_active:
            error_message = 'This user is banned, you can\'t talk to him.'
            form = UsernameSearchForm()
            return render(request, 'chat/index.html', {
                'form': form, 'error_message': error_message
            })
        history = Message.get_last_messages(room_id=room_id)
        return render(request, 'chat/room.html', {
            'room_id': room_id,
            'username': user.username,
            'interlocutor': interlocutor.username,
            'history': history,
        })


class ChatUserRegisterView(CreateView):
    """Overridden class for login a user after registration."""
    model = CustomUser
    template_name = 'chat/register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        form.save()
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        login(self.request, user)
        return HttpResponseRedirect(reverse_lazy('chat:index'))
