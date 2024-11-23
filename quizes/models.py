from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    is_author = models.BooleanField(default=False)

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Один вариант'),
        ('multiple', 'Несколько вариантов'),
        ('text', 'Текстовый ответ'),
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField()
    correct_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Вопрос {self.order}: {self.text[:50]}'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)

    def __str__(self):
        return f'Попытка {self.user.username} - {self.quiz.title}'


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    text_answer = models.TextField(blank=True)

    def __str__(self):
        return f'Ответ на вопрос "{self.question.text[:50]}" от {self.attempt.user.username}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.user.username} к "{self.quiz.title}"'
