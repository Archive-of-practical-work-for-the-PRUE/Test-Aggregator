from django.contrib import admin
from .models import Profile, Category, Quiz, Question, Choice, Attempt, Answer, Comment

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Attempt)
admin.site.register(Answer)
admin.site.register(Comment)
