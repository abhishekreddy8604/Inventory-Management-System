from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class QuizCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Quiz(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(QuizCategory, on_delete=models.CASCADE)
    description = models.TextField()
    deadline = models.DateTimeField(null=True)
    total_time = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(10)]
    )
    examiner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz")

    def __str__(self):
        return self.name

    @property
    def is_valid(self):
            return self.total_questions == self.questions.all().count() 


    @property
    def remaining(self):
        return self.total_questions - self.questions.all().count() - 1


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quiz_attempt"
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="quiz_attempt"
    )
    questions = models.ManyToManyField(Question, related_name="quiz_attempts")
    is_attempted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "quiz")



class UserResponse(models.Model):
    quiz_attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name="user_responses"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="user_responses"
    )
    selected_option = models.ForeignKey(
        Option, on_delete=models.SET_NULL, null=True, related_name="user_responses"
    )

    def is_correct(self):
        return self.selected_option.is_correct


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    examinee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="results")
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.examinee}'s result for {self.quiz}"

    def calculate_score(self):
        quiz_attempt = QuizAttempt.objects.get(user=self.examinee, quiz=self.quiz)
        quiz_attempt.is_attempted = True
        quiz_attempt.save()

        total_questions = self.quiz.questions.count()
        correct_responses = quiz_attempt.user_responses.filter(
            selected_option__is_correct=True
        ).count()

        self.score = (correct_responses / 5) * 100
        self.save()

        return self.score
    
