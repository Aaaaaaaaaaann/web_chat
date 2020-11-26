from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
import pgcrypto


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Room(models.Model):
    users = ArrayField(models.IntegerField(null=True, blank=True), size=2, null=True, blank=True)

    @staticmethod
    def get_interlocutor(room_id, user_id):
        users = Room.objects.get(pk=room_id).users
        interlocutor = set(users) - {user_id}
        return CustomUser.objects.get(pk=interlocutor.pop())


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sender')
    content = pgcrypto.EncryptedTextField()
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    @staticmethod
    def get_last_messages(room_id, number=20):
        return Message.objects.filter(room_id=room_id).order_by('-date').reverse()[:number]
