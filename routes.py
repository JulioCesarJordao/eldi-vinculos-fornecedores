from django.urls import path
from django.contrib.auth import views as auth
from eldi import views

urlpatterns = [path('entrar/', auth.LoginView.as_view(template_name='login.html'), name='login'), path('sair/', auth.LogoutView.as_view(), name='logout'), path('', views.home, name='home'), path('pendencias/', views.pending, name='pending'), path('pendencias/<int:pk>/', views.update, name='update'), path('importar/', views.upload, name='upload')]
