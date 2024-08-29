"""
This file configures the Django admin interface
for the Choice and Question models.
"""
from django.contrib import admin
from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    """
    Provides an inline interface
    for editing Choice objects in the Question admin page.
    """
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """
    Configures the admin interface for the Question model.
    """
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date', 'end_date'],
                              'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
