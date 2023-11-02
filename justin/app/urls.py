from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', RegistrationAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='api_token_auth'),
    path('helo/', hello.as_view(), name='api_token_auth'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('ask_journal/', journal, name='journal'),
    path('delete-history/', DeleteUserHistoryView.as_view(), name='delete_user_history'),


   
]