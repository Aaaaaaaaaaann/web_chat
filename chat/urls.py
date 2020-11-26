from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'chat'

urlpatterns = [
    path('', views.start_page, name='start_page'),
    path('register/', views.ChatUserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='chat/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', LogoutView.as_view(template_name='chat/login.html'), name='logout'),
    path('chat/', views.index, name='index'),
    path('chat/user-search/', views.user_search, name='user_search'),
    path('chat/<int:room_id>/', views.chat, name='chat'),
]
