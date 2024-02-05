from django.contrib import admin
from . import models


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    list_display_links = ['id']


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey', 'text', 'parent_question']
    list_display_links = ['id']


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text']
    list_display_links = ['id']


@admin.register(models.UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'survey', 'user', 'question', 'choice']
    list_display_links = ['id']


@admin.register(models.QuestionDependency)
class QuestionDependencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'dependent_question', 'parent_choice']
    list_display_links = ['id']
