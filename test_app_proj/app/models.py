from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser


class Survey(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    parent_question = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='child_questions')
    text = models.TextField()

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class UserResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Предполагается, что есть модель пользователя
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True)
    text_response = models.TextField(blank=True)

    def get_response(self):
        if self.choice:
            return self.choice.text
        else:
            return self.text_response


class QuestionDependency(models.Model):
    dependent_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='dependencies')
    parent_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='dependent_questions')

    def __str__(self):
        return f"{self.dependent_question} - {self.parent_choice}"
