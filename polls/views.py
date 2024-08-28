from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be published in the future).
        """
        published_question_list = [q.pk for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(pk__in=published_question_list).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_question_list = [q.pk for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(pk__in=published_question_list)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        published_question_list = [q.pk for q in Question.objects.all() if q.is_published()]
        return Question.objects.filter(pk__in=published_question_list)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Voting is not allowed for this question.",
        })
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
