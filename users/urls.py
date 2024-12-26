from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('email-confirmation-sent/', views.email_confirmation, name='email_confirmation'),
    path('activate/<uidb64>/<token>/', views.activate, name='email_confirm'),
]