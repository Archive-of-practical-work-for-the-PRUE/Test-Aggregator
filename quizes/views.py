from .models import Quiz, Choice, Attempt, Answer, Profile
from .forms import QuizForm, UserRegisterForm, ProfileUpdateForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone


def home(request):
    quizzes = Quiz.objects.filter(is_published=True)
    return render(request, 'quiz/home.html', {'quizzes': quizzes})


@login_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)

    if request.method == 'POST':
        # Создание новой попытки прохождения теста
        attempt = Attempt.objects.create(user=request.user, quiz=quiz)

        # Получение списка вопросов теста
        questions = quiz.questions.all()

        # Обработка ответов пользователя
        for question in questions:
            # Получаем данные из формы
            answer_data = request.POST.getlist(f'question_{question.id}')

            if question.question_type == 'single':
                # Для одиночного выбора ожидаем одно значение
                selected_choice_id = answer_data[0] if answer_data else None
                selected_choice = Choice.objects.get(
                    id=selected_choice_id) if selected_choice_id else None

                # Создаем ответ
                answer = Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer='',
                )
                if selected_choice:
                    answer.selected_choices.add(selected_choice)

            elif question.question_type == 'multiple':
                # Для множественного выбора ожидаем список значений
                selected_choice_ids = answer_data
                selected_choices = Choice.objects.filter(
                    id__in=selected_choice_ids)

                # Создаем ответ
                answer = Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer='',
                )
                answer.selected_choices.set(selected_choices)

            elif question.question_type == 'text':
                # Для текстового ответа получаем введенный текст
                text_answer = answer_data[0] if answer_data else ''
                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer=text_answer,
                )

        # Вычисление результатов (баллов)
        total_score = 0
        max_score = 0

        for question in questions:
            max_score += 1  # Предположим, что каждый вопрос оценивается в 1 балл
            answer = attempt.answers.get(question=question)

            if question.question_type in ['single', 'multiple']:
                correct_choices = set(question.choices.filter(is_correct=True))
                user_choices = set(answer.selected_choices.all())

                if correct_choices == user_choices:
                    total_score += 1
            elif question.question_type == 'text':
                # Здесь можно добавить логику проверки текстовых ответов
                pass

        # Обновляем попытку с результатами
        attempt.score = total_score
        attempt.max_score = max_score
        attempt.finished_at = timezone.now()
        attempt.save()

        # Перенаправление на страницу результатов
        return HttpResponseRedirect(reverse('quiz_result', args=[attempt.id]))
    else:
        # Отображение формы с вопросами
        return render(request, 'quiz/take_quiz.html', {'quiz': quiz})


def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.author = request.user
            quiz.save()
            return HttpResponseRedirect(reverse('create_quiz'))
    else:
        form = QuizForm()

    return render(request, 'quiz/create_quiz.html', {"form": form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически логиним пользователя после регистрации
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('home')  # Перенаправляем на главную страницу или куда нужно
    else:
        form = UserRegisterForm()
    return render(request, 'quiz/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Ваш профиль был обновлен!')
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'quiz/profile.html', {'p_form': p_form})


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(Attempt, pk=attempt_id, user=request.user)
    return render(request, 'quiz/quiz_result.html', {'attempt': attempt})


def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz})
