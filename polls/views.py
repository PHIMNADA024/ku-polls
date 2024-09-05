"""
This file contains views for handling polling functionality in KU Polls.
"""
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    """
    View that displays a list of the latest published questions.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions
        (not including those set to be published in the future).
        """
        published_question_list = [q.pk for q in Question.objects.all()
                                   if q.is_published()]
        published_questions = Question.objects.filter(pk__in=published_question_list)
        sorted_questions = published_questions.order_by('-pub_date')[:5]
        return sorted_questions

    def get_context_data(self, **kwargs):
        """
        Add the status of each question to the context.
        """
        context = super().get_context_data(**kwargs)
        for question in context['latest_question_list']:
            question.status = 'Open' if question.can_vote() else 'Closed'
        return context


class DetailView(generic.DetailView):
    """
    View that displays details of a specific question.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_question_list = [q.pk for q in Question.objects.all()
                                   if q.is_published()]
        return Question.objects.filter(pk__in=published_question_list)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the detail view of a question.
        Redirect to the index page with an error message
        if voting is not allowed.
        """
        try:
            question = self.get_object()
        except Http404:
            messages.error(request, "This question is not available.")
            return HttpResponseRedirect(reverse('polls:index'))
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this question.")
            return HttpResponseRedirect(reverse('polls:index'))
        this_user = request.user
        try:
            last_vote = Vote.objects.get(user=this_user, choice__question=question).choice.id
        except Vote.DoesNotExist:
            last_vote = 0
        return render(request, self.template_name, {'question': question, 'last_vote': last_vote})


class ResultsView(generic.DetailView):
    """
    View that displays the results for a specific question.
    """
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_question_list = [q.pk for q in Question.objects.all()
                                   if q.is_published()]
        return Question.objects.filter(pk__in=published_question_list)


@login_required
def vote(request, question_id):
    """
    Handle voting for a specific question.
    """
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    # References to the current user
    this_user = request.user

    # Get the user's vote
    try:
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # user has a vote for this question! Update his choice.
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was updated to '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        # does not have a vote yet
        Vote.objects.create(user=this_user, choice=selected_choice)
        # automatically saved
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")

    return HttpResponseRedirect(reverse('polls:results',
                                        args=(question_id,)))
