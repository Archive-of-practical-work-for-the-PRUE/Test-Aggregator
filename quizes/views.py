from .models import Quiz, Choice, Attempt, Answer, Profile, Question
from .forms import QuizForm, UserRegisterForm, ProfileUpdateForm, QuestionForm, ChoiceForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages


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


@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.author = request.user
            quiz.save()
            # Redirect to question creation
            return redirect('create_questions', quiz_id=quiz.pk)
    else:
        form = QuizForm()
    return render(request, 'quiz/create_quiz.html', {'form': form})


def create_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        # получаем количество вопросов из скрытого поля формы
        num_questions = int(request.POST.get('num_questions', 0))

        for i in range(num_questions):
            question_data = {
                'text': request.POST.get(f'question_{i}-text'),
                'question_type': request.POST.get(f'question_{i}-question_type'),
                'quiz': quiz,
                'order': i+1  # Устанавливаем порядок вопроса
            }
            if not all(question_data.values()):  # проверка на неполные вопросы
                return HttpResponseBadRequest("Не все поля заполнены!")

            question_form = QuestionForm(question_data)
            if question_form.is_valid():
                question = question_form.save()

                num_choices = int(request.POST.get(f'num_choices_{i}', 0))
                for j in range(num_choices):
                    choice_data = {
                        'question': question,
                        'text': request.POST.get(f'choice_{i}_{j}-text'),
                        'is_correct': request.POST.get(f'choice_{i}_{j}-is_correct') == 'on',
                    }
                    # проверяем наличие текста варианта ответа
                    if not choice_data['text']:
                        continue

                    choice_form = ChoiceForm(choice_data)
                    if choice_form.is_valid():
                        choice_form.save()
                    else:
                        # Обработка ошибки при невалидности данных о варианте ответа
                        return HttpResponseBadRequest(choice_form.errors)
            else:
                # Обработка ошибок при невалидности данных о вопросе
                return HttpResponseBadRequest(question_form.errors)

        # Перенаправление на страницу с квизом
        return redirect('home')

    else:
        return render(request, 'quiz/create_questions.html', {'quiz': quiz, 'question_form': QuestionForm()})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически логиним пользователя после регистрации
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            # Перенаправляем на главную страницу или куда нужно
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'quiz/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
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
