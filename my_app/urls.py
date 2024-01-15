from . import views
from django.urls import path

from my_app.views import (
    QuestionDeleteView,
    QuestionEditView,
    QuizCreateView,
    QuizListView,
    QuizUpdateView,
    QuizDeleteView,
    QuestionCreateView,
    QuizResultView,
    TakeQuizView,
    MyQuizListView,
    AlreadyAttemptedView,
    QuizCategoryCreate,
    QuizVisualization,
    QuizSubmissionsView
)

urlpatterns = [
    path("", QuizListView.as_view(), name="home"),
    path("my_quiz/", MyQuizListView.as_view(), name="my_quiz"),
    path("quiz_create/", QuizCreateView.as_view(), name="quiz_create"),
    path("quiz_update/<int:pk>/", QuizUpdateView.as_view(), name="quiz_update"),
    path("quiz_delete/<int:pk>/", QuizDeleteView.as_view(), name="quiz_delete"),
    path(
        "question_create/<int:quiz_id>/",
        QuestionCreateView.as_view(),
        name="question_create",
    ),
    path("quiz_result/<int:quiz_id>/", QuizResultView.as_view(), name="quiz_result"),
    path("take_quiz/<int:quiz_id>/", TakeQuizView.as_view(), name="take_quiz"),
    path(
        "already_attempted/<int:quiz_id>/",
        AlreadyAttemptedView.as_view(),
        name="already_attempted",
    ),
    path("quiz_category_create", QuizCategoryCreate.as_view(), name="create_category"),
    path("quiz_visualization", QuizVisualization.as_view(), name="quiz_visualization"),
    path('quiz-submissions/', QuizSubmissionsView.as_view(), name='quiz_submissions'),
    path('view_quizz/<int:pk>/', views.QuizQuestionsView.as_view(), name='view_quizz'),
    path('question_edit/<int:pk>/', QuestionEditView.as_view(), name='question_edit'),
    path('question_delete/<int:pk>/', QuestionDeleteView.as_view(), name='question_delete'),
]
