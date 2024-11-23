from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/list/', views.quiz_list, name='quiz_list'),
    path('quiz/detail/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/attempts/', views.attempt_list, name='attempt_list'),
]
