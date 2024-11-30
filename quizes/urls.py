from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('quiz/create/', views.create_quiz, name='quiz_create'),
    path('quiz/<int:quiz_id>/create_questions/', views.create_questions, name='create_questions'),

    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Маршруты для тестов
    # path('quiz/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    # path('quiz/<int:pk>/edit/', views.QuizUpdateView.as_view(), name='quiz_update'),
    # path('question/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question_update'),

    # Маршруты для прохождения тестов
    path('quiz/<int:quiz_id>/attempts/', views.attempt_list, name='attempt_list'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/list/', views.quiz_list, name='quiz_list'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/detail/<int:pk>/', views.quiz_detail, name='quiz_detail'),
]
