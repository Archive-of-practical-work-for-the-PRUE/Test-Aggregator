# Test-Aggregator

## Диграмма прецедентов
![Диаграмма прецедентов](assets/Диаграмма%20Прецедентов.png)

## Диаграмма классов ORM
```mermaid
classDiagram
    %% Класс User
    class User {
        +Integer id
        +String username
        +String email
        +String password
        +authenticate()
        +register()
    }
    
    %% Класс Profile
    class Profile {
        +Integer id
        +String bio
        +String avatar
        +Boolean is_author
        +update_profile()
    }
    
    %% Класс Category
    class Category {
        +Integer id
        +String name
        +String description
        +get_quizzes()
    }
    
    %% Класс Quiz
    class Quiz {
        +Integer id
        +String title
        +String description
        +DateTime created_at
        +DateTime updated_at
        +Boolean is_published
        +publish()
        +unpublish()
        +get_questions()
    }
    
    %% Класс Question
    class Question {
        +Integer id
        +String text
        +String question_type
        +Integer order
        +get_answers()
    }
    
    %% Класс Choice
    class Choice {
        +Integer id
        +String text
        +Boolean is_correct
    }
    
    %% Класс Attempt
    class Attempt {
        +Integer id
        +DateTime started_at
        +DateTime finished_at
        +Float score
        +Float max_score
    }
    
    %% Класс Answer
    class Answer {
        +Integer id
        +String text_answer
    }
    
    %% Класс Comment
    class Comment {
        +Integer id
        +String text
        +DateTime created_at
    }
    
    %% Отношения между классами
    User "1" -- "1" Profile : имеет
    User "1" -- "0..*" Attempt : делает
    User "1" -- "0..*" Quiz : создаёт
    User "1" -- "0..*" Comment : пишет
    Profile "1" -- "1" User : принадлежит
    Quiz "1" -- "0..*" Question : содержит
    Quiz "0..*" -- "1" Category : относится к
    Question "1" -- "0..*" Choice : имеет
    Attempt "1" -- "0..*" Answer : включает
    Answer "*" -- "1" Question : отвечает на
    Attempt "*" -- "1" Quiz : для
    Attempt "*" -- "1" User : принадлежит
    Comment "*" -- "1" Quiz : относится к
    Answer "*" -- "0..1" Choice : выбранный вариант
```

## Диаграмма последовательностей

### Диаграмма последовательности прохождения теста

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant QuizModelView
    participant QuizModel
    participant QuesionModel
    participant AttemptModel
    participant AnswerModel
    participant ResultView
    participant Database

    User->>Browser: Открывает страницу теста
    Browser->>QuizModelView: GET /quiz/<id>/
    QuizModelView->>QuizModel: Получить тест
    QuizModelView->>QuesionModel: Получить вопросы
    QuizModelView->>Browser: Отправить страницу теста
    Browser->>User: Отображает тест
    User->>Browser: Заполняет ответы и отправляет форму
    Browser->>QuizModelView: POST /quiz/<id>/ (ответы)
    QuizModelView->>AttemptModel: Создать попытку
    loop По каждому вопросу
        QuizModelView->>AnswerModel: Сохранить ответ
    end
    QuizModelView->>AttemptModel: Вычислить результат
    QuizModelView->>Database: Сохранить попытку и ответы
    QuizModelView->>Browser: Перенаправление на страницу результатов
    Browser->>ResultView: GET /result/<attempt_id>/
    ResultView->>AttemptModel: Получить попытку
    ResultView->>AnswerModel: Получить ответы
    ResultView->>Browser: Отправить страницу результатов
    Browser->>User: Отображает результаты
```
### Диаграмма последовательности регистрации
```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant RegistrationView
    participant UserModel
    participant ProfileModel
    participant LoginView
    participant AuthenticationSystem
    participant Database

    %% Регистрация
    User->>Browser: Открывает страницу регистрации
    Browser->>RegistrationView: GET /register/
    RegistrationView->>Browser: Отправляет форму регистрации
    User->>Browser: Заполняет форму и отправляет
    Browser->>RegistrationView: POST /register/ (данные формы)
    RegistrationView->>UserModel: Проверяет существование пользователя
    UserModel-->>RegistrationView: Не существует
    RegistrationView->>UserModel: Создает нового пользователя
    RegistrationView->>ProfileModel: Создает профиль пользователя
    RegistrationView->>Database: Сохраняет пользователя и профиль
    RegistrationView->>AuthenticationSystem: Аутентифицирует пользователя
    RegistrationView->>Browser: Перенаправляет на главную страницу
    Browser->>User: Отображает главную страницу (пользователь вошел в систему)

    %% Вход в систему
    User->>Browser: Открывает страницу входа
    Browser->>LoginView: GET /login/
    LoginView->>Browser: Отправляет форму входа
    User->>Browser: Вводит данные и отправляет форму
    Browser->>LoginView: POST /login/ (учетные данные)
    LoginView->>AuthenticationSystem: Проверяет учетные данные
    AuthenticationSystem-->>LoginView: Аутентификация успешна
    LoginView->>Browser: Перенаправляет на главную страницу
    Browser->>User: Отображает главную страницу (пользователь вошел в систему)
```