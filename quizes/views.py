from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Choice, Attempt, Answer, Profile, Question
from .forms import QuizForm, UserRegisterForm, ProfileUpdateForm, QuestionForm, ChoiceForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Exists, OuterRef


def home(request):
    quizzes = Quiz.objects.filter(is_published=True)
    return render(request, 'quiz/home.html', {'quizzes': quizzes})


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_published=True)
    questions = quiz.questions.all()

    if request.method == 'POST':
        # Создаем новую попытку
        attempt = Attempt.objects.create(user=request.user, quiz=quiz)

        # Обработка ответов пользователя
        for question in questions:
            answer_data = request.POST.getlist(f'question_{question.id}')

            if question.question_type == 'text':
                text_answer = answer_data[0] if answer_data else ''
                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer=text_answer,
                )

            if question.question_type == 'single':
                selected_choice_id = answer_data[0] if answer_data else None
                selected_choice = Choice.objects.get(id=selected_choice_id) if selected_choice_id else None

                answer = Answer.objects.create(
                    attempt=attempt,
                    question=question,
                )
                if selected_choice:
                    answer.selected_choices.add(selected_choice)

            elif question.question_type == 'multiple':
                selected_choice_ids = answer_data
                selected_choices = Choice.objects.filter(id__in=selected_choice_ids)

                answer = Answer.objects.create(
                    attempt=attempt,
                    question=question,
                )
                answer.selected_choices.set(selected_choices)

        # Вычисление результатов
        total_score = 0
        max_score = questions.count()

        for answer in attempt.answers.all():
            question = answer.question
            if question.question_type in ['single', 'multiple']:
                correct_choices = set(question.choices.filter(is_correct=True))
                user_choices = set(answer.selected_choices.all())
                if correct_choices == user_choices:
                    total_score += 1
            elif question.question_type == 'text':
                correct_answer = question.correct_answer.strip().lower() if question.correct_answer else ''
                user_answer = answer.text_answer.strip().lower()
                if user_answer == correct_answer:
                    total_score += 1

        # Обновляем попытку с результатами
        attempt.score = total_score
        attempt.max_score = max_score
        attempt.finished_at = timezone.now()
        attempt.save()

        # Перенаправление на страницу с результатами
        return redirect('quiz_result', attempt_id=attempt.id)

    else:
        # Отображение формы с вопросами
        return render(request, 'quiz/take_quiz.html', {'quiz': quiz, 'questions': questions})


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


@login_required
def create_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        num_questions = int(request.POST.get('num_questions', 0))

        for i in range(num_questions):
            question_text = request.POST.get(f'question_{i}-text')
            question_type = request.POST.get(f'question_{i}-question_type')
            correct_answer = request.POST.get(f'question_{i}-correct_answer', '')

            if not question_text or not question_type:
                return HttpResponseBadRequest("Не все поля вопроса заполнены!")

            question_data = {
                'quiz': quiz.id,
                'text': question_text,
                'question_type': question_type,
                'order': i + 1,
                'correct_answer': correct_answer
            }

            question_form = QuestionForm(question_data)
            if question_form.is_valid():
                question = question_form.save()

                if question_type in ['single', 'multiple']:
                    num_choices = int(request.POST.get(f'num_choices_{i}', 0))
                    for j in range(num_choices):
                        choice_text = request.POST.get(f'choice_{i}_{j}-text')
                        is_correct = request.POST.get(f'choice_{i}_{j}-is_correct') == 'on'

                        if not choice_text:
                            continue

                        choice_data = {
                            'question': question.id,
                            'text': choice_text,
                            'is_correct': is_correct
                        }

                        choice_form = ChoiceForm(choice_data)
                        if choice_form.is_valid():
                            choice_form.save()
                        else:
                            return HttpResponseBadRequest(f"Ошибка в варианте ответа: {choice_form.errors}")
            else:
                return HttpResponseBadRequest(f"Ошибка в вопросе: {question_form.errors}")

        # Перенаправление на страницу с тестом
        return redirect('quiz_detail', pk=quiz_id)

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

    # Подготовка данных для шаблона
    answers = []
    for answer in attempt.answers.all():
        question = answer.question
        is_correct = False
        correct_choices = []
        user_choices = []

        if question.question_type in ['single', 'multiple']:
            # Получаем правильные варианты ответа
            correct_choices = list(question.choices.filter(is_correct=True))
            # Получаем варианты, выбранные пользователем
            user_choices = list(answer.selected_choices.all())
            # Проверяем, совпадают ли выбранные и правильные варианты
            is_correct = set(correct_choices) == set(user_choices)
        elif question.question_type == 'text':
            # Логика проверки текстовых ответов (опционально)
            correct_answer = question.correct_answer.strip().lower() if question.correct_answer else ''
            user_answer = answer.text_answer.strip().lower()
            is_correct = user_answer == correct_answer

        answers.append({
            'answer': answer,
            'is_correct': is_correct,
            'correct_choices': correct_choices,
            'user_choices': user_choices,
        })

    context = {
        'attempt': attempt,
        'answers': answers,
    }
    return render(request, 'quiz/quiz_result.html', context)


def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz})


@login_required
def quiz_list(request):
    # Получаем список всех опубликованных тестов
    quizzes = Quiz.objects.filter(is_published=True)

    # Аннотируем тесты информацией о том, был ли у пользователя попытки прохождения этого теста
    quizzes = quizzes.annotate(
        is_solved=Exists(
            Attempt.objects.filter(
                quiz=OuterRef('pk'),
                user=request.user
            )
        )
    )

    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


@login_required
def attempt_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    attempts = Attempt.objects.filter(user=request.user, quiz=quiz).order_by('-finished_at')
    return render(request, 'quiz/attempt_list.html', {'quiz': quiz, 'attempts': attempts})
