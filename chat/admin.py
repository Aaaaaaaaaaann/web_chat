from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'is_active']
    list_display_links = ['username']
    list_editable = ['is_active']
