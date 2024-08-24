"""
This module defines model-related classes for polls application
"""
import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    Represents a poll question in the application.
    Each question has its own text and a publication date.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        """
        Returns a string representation of the question text.
        """
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        """
        Returns True if the question was published within the last day.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """
    Represents a choice in a poll question.
    Each choice is a part of  a specific question and has its own text and vote count.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """
        Returns a string representation of the choice text.
        """
        return self.choice_text
