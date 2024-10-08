"""This module defines model-related classes for the polls application."""
import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


def get_current_time():
    """Return the current date and time."""
    return timezone.now()


class Question(models.Model):
    """
    Represents a poll question in the application.

    Each question has its own text and a publication date.
    """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=get_current_time)
    end_date = models.DateTimeField('date ended', null=True, blank=True)

    def __str__(self):
        """Return a string representation of the question text."""
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        """Return True if the question was published within the last day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return True if the current local date/time is on or after the question’s pub_date."""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """
        Return True if voting is allowed based on the pub_date and end_date.

        Voting is allowed if the question is published and either has no end date
        or the current time is before the end date.
        """
        now = timezone.now()
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """
    Represents a choice in a poll question.

    Each choice is associated with a specific question and has its own text.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """Return the votes for this choice."""
        return self.vote_set.count()

    def __str__(self):
        """Return a string representation of the choice text."""
        return self.choice_text


class Vote(models.Model):
    """
    Records a choice made by a user in response to a poll question.

    Each vote is associated with a user and a choice.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
