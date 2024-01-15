from django.forms import ModelForm
from django import forms
from .models import Quiz


class QuizCreateForm(ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "datetime-local"}
        )
    )

    class Meta:
        model = Quiz
        exclude = ("examiner",)
