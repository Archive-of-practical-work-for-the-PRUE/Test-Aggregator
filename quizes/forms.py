from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Quiz, Question, Choice, Profile


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'category', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text', 'question_type', 'order', 'correct_answer']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'correct_answer': forms.Textarea(attrs={'rows': 2}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['question', 'text', 'is_correct']


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Добавляем поле email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
