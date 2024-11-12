from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
    # path('results/<int:attempt_id>/', views.results, name='results'),
]
