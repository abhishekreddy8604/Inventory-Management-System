import random
from typing import Any
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import Avg
from .forms import QuizCreateForm

from my_app.models import (
    Quiz,
    Question,
    Option,
    Result,
    QuizAttempt,
    UserResponse,
    QuizCategory,
)


class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    form_class = QuizCreateForm
    template_name = "my_app/quiz_create.html"

    def test_func(self):
        return self.request.user.is_examiner

    def form_valid(self, form):
        form.instance.examiner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse_lazy('question_create', kwargs={'quiz_id': self.object.id})}?remaining={self.object.total_questions - 1}"


class QuizCategoryCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = QuizCategory
    fields = "__all__"
    template_name = "my_app/quiz_category_create.html"

    def test_func(self):
        return self.request.user.is_examiner

    def get_success_url(self):
        return reverse_lazy("quiz_create")


class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    fields = ("name", "description", "total_time", "total_questions")
    template_name = "my_app/quiz_update.html"
    success_url = reverse_lazy("my_quiz")

    def form_valid(self, form):
        form.instance.examiner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        obj = self.get_object()
        return obj.examiner == self.request.user


class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = "my_app/quiz_delete.html"
    context_object_name = "quiz"
    success_url = reverse_lazy("my_quiz")

    def test_func(self):
        obj = self.get_object()
        return obj.examiner == self.request.user


# class QuizListView(LoginRequiredMixin, ListView):
#     model = Quiz
#     template_name = "my_app/quiz_list.html"
#     context_object_name = "quiz_list"

#     def get_queryset(self):
#         return [quiz for quiz in Quiz.objects.all() if quiz.is_valid]


class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "my_app/quiz_list.html"
    context_object_name = "quiz_list"
    

    def get_queryset(self):
        return [quiz for quiz in Quiz.objects.filter(examiner__category = self.request.user.category ) if quiz.is_valid]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        return context



class MyQuizListView(ListView):
    model = Quiz
    template_name = "my_app/my_quiz_list.html"
    context_object_name = "quiz_list"

    def get_queryset(self):
        # Filter quizzes based on the examiner (the current user)
        return Quiz.objects.filter(examiner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize a dictionary to store question counts for each quiz
        question_counts = {}

        # Iterate over the quizzes and count questions for each
        for quiz in self.get_queryset():
            question_counts[quiz.id] = quiz.questions.count()

        # Add the question counts dictionary to the context
        context['question_counts'] = question_counts

        return context

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    fields = ("text",)
    template_name = "questions/question_create.html"
    OptionFormSet = inlineformset_factory(
        Question, Option, fields="__all__", extra=4, can_delete=False
    )

    def get_context_data(self, **kwargs):
        quiz = Quiz.objects.get(id=self.kwargs["quiz_id"])
        remaining_questions = int(self.request.GET.get("remaining"))

        context = super().get_context_data(**kwargs)
        context["question_no"] = quiz.total_questions - remaining_questions
        context["formset"] = self.OptionFormSet()
        context["quiz"] = quiz.name
        return context

    def form_valid(self, form):
        quiz_id = self.kwargs["quiz_id"]
        form.instance.quiz_id = quiz_id
        print(form.instance)  # question instance
        print(self.request.POST)

        formset = self.OptionFormSet(self.request.POST, instance=form.instance)
        print("formset", formset)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            print("self.objects ", self.object)
            formset.save()
            print("formset", formset)

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )

    def get_success_url(self):
        remaining_questions = int(self.request.GET.get("remaining"))
        return (
            reverse_lazy("home")
            if remaining_questions == 0
            else f"{reverse_lazy('question_create', kwargs={'quiz_id': self.kwargs['quiz_id']})}?remaining={remaining_questions - 1}"
        )

class QuizResultView(LoginRequiredMixin, CreateView, ListView):
    model = Result
    fields = ("quiz", "examinee", "score")
    template_name = "my_app/quiz_result.html"
    context_object_name = "quiz_result"

    def get_initial(self):
        initial = super().get_initial()
        quiz_id = self.kwargs["quiz_id"]
        quiz = get_object_or_404(Quiz, id=quiz_id)

        result, created = Result.objects.get_or_create(
            quiz=quiz, examinee=self.request.user
        )
        result.calculate_score()
        return initial

    def get_queryset(self):
        quiz_id = self.kwargs["quiz_id"]
        quiz = Quiz.objects.get(id=quiz_id)
        return Result.objects.filter(quiz=quiz, examinee=self.request.user)


class TakeQuizView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = UserResponse
    fields = ("selected_option",)
    template_name = "my_app/take_quiz_create.html"
    success_url = reverse_lazy("home")

    def get_initial(self):
        initial = super().get_initial()
        quiz = Quiz.objects.get(id=self.kwargs["quiz_id"])
        self.time = quiz.total_time
        self.quiz_attempt, created = QuizAttempt.objects.get_or_create(
            user=self.request.user, quiz=quiz
        )
        if created:
            random_indices = random.sample(range(0, quiz.total_questions), 5)
            question_list = [quiz.questions.all()[index] for index in random_indices]
            for question in question_list:
                self.quiz_attempt.questions.add(question)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_idx = int(self.request.GET.get("question"))
        question = list(self.quiz_attempt.questions.all())[question_idx]
        context["question_no"] = question_idx + 1
        context["question"] = question
        context["time"] = self.time * 60
        context["quiz_id"] = self.kwargs["quiz_id"]

        context["options"] = [option for option in question.options.all()]
        return context

    def form_valid(self, form):
        question_idx = int(self.request.GET.get("question"))
        form.instance.quiz_attempt = self.quiz_attempt
        form.instance.question = self.quiz_attempt.questions.all()[question_idx]

        if form.is_valid():
            form.instance.selected_option = Option.objects.get(
                id=self.request.POST.get("selected_option")
            )
            form.save()
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        question_idx = int(self.request.GET.get("question"))
        return (
            f"{reverse_lazy('quiz_result', kwargs={'quiz_id': self.kwargs['quiz_id']})}"
            if question_idx == 4
            else f"{reverse_lazy('take_quiz', kwargs={'quiz_id': self.kwargs['quiz_id']})}?question={question_idx + 1}"
        )

    def test_func(self):
        quiz = Quiz.objects.get(id=self.kwargs["quiz_id"])
        quiz_attempt = QuizAttempt.objects.filter(user=self.request.user, quiz=quiz)
        return not (len(quiz_attempt) and quiz_attempt.first().is_attempted)

    def handle_no_permission(self):
        return HttpResponseRedirect(
            reverse_lazy(
                "already_attempted", kwargs={"quiz_id": self.kwargs["quiz_id"]}
            )
        )




class AlreadyAttemptedView(LoginRequiredMixin, TemplateView):
    template_name = "my_app/already_attempt.html"

    def get_context_data(self, **kwargs):
        quiz = Quiz.objects.get(id=self.kwargs["quiz_id"])
        context = super().get_context_data(**kwargs)
        context["quiz"] = quiz
        return context


class QuizVisualization(LoginRequiredMixin, TemplateView):
    template_name = "my_app/quiz_visualization.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        top_five = Result.objects.all().order_by("-score")[:5]
        last_five = Result.objects.all().order_by("score")[:5]
        context["last_five"] = last_five
        print(top_five.count())
        context["top_five"] = top_five
        # max_score = Result.objects.aggregate(max_score=Max("score"))["max_score"]
        average_score = Result.objects.aggregate(avg=Avg("score"))["avg"]
        context["average_score"] = average_score
        return context



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Result, Quiz  # Import your models

class QuizSubmissionsView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'my_app/quiz_submissions.html'  # Update with your actual template name
    context_object_name = 'submissions'

    def get_queryset(self):
        # Get quizzes created by the current user
        user_quizzes = Quiz.objects.filter(examiner=self.request.user)

        # Filter results to include only those related to the user's quizzes
        return Result.objects.filter(quiz__in=user_quizzes).select_related('quiz', 'examinee')


class QuestionEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    fields = ['text']
    template_name = 'questions/question_edit.html'
    OptionFormSet = inlineformset_factory(Question, Option, fields='__all__', extra=0, can_delete=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = self.OptionFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = self.OptionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def test_func(self):
        question = self.get_object()
        return self.request.user == question.quiz.examiner

    def get_success_url(self):
        # Redirect back to quiz view or another appropriate page
        return reverse_lazy('view_quizz', kwargs={'pk': self.object.quiz.id})



class QuestionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Question
    template_name = 'questions/question_confirm_delete.html'

    def test_func(self):
        question = self.get_object()
        return self.request.user == question.quiz.examiner

    def get_success_url(self):
        # Redirect to the quiz view or another appropriate view
        return reverse_lazy('view_quizz', kwargs={'pk': self.object.quiz.id})

    def delete(self, *args, **kwargs):
        # Perform the delete action
        return super(QuestionDeleteView, self).delete(*args, **kwargs)

from django.views.generic import DetailView


class QuizQuestionsView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'my_app/quiz_questions.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context

