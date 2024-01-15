from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_examiner = models.BooleanField(default=False)

    CATEGORY_CHOICES = (
        ("Biomedical Engineering", "Biomedical Engineering"),
        ("Computer Science", "Computer Science"),
        ("Electrical and Computer Engineering", "Electrical and Computer Engineering"),
        ("Engineering Design Division", "Engineering Design Division"),
        ("Materials Science and Engineering", "Materials Science and Engineering"),
        ("Mechanical Engineering", "Mechanical Engineering"),
        ("Systems Science and Industrial Engineering","Systems Science and Industrial Engineering"),
    )

    category = models.CharField(
        choices=CATEGORY_CHOICES,
        default=CATEGORY_CHOICES[1],
    )

    def __str__(self):
        return self.username
    
    
