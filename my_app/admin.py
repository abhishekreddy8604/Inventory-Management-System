from django.contrib import admin

from .models import (
    Result,
    Quiz,
    Question,
    UserResponse,
    Option,
    QuizAttempt,
    QuizCategory,
)

admin.site.register(Result)
admin.site.register(UserResponse)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizAttempt)
admin.site.register(QuizCategory)
