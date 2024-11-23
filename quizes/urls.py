from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('create_quiz/<int:quiz_id>/questions/',
         views.create_questions, name='create_questions'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]
