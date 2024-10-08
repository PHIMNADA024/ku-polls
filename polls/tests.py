"""This file contains tests for the polling application, including model methods and view functionality."""
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice, Vote
from django.contrib.auth.models import User
from mysite import settings


class QuestionModelTests(TestCase):
    """Tests for the methods of the Question model."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_question(self):
        """is_published() returns False for questions whose pub_date is in the future."""
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """is_published() returns True for questions with the default pub_date (now)."""
        question = Question(pub_date=timezone.now())
        self.assertIs(question.is_published(), True)

    def test_is_published_with_past_question(self):
        """is_published() returns True for questions whose pub_date is in the past."""
        past_time = timezone.now() - datetime.timedelta(days=30)
        past_question = Question(pub_date=past_time)
        self.assertIs(past_question.is_published(), True)

    def test_can_vote_before_start_date(self):
        """can_vote() returns False if the current time is before the pub_date."""
        future_time = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=future_time)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_within_voting_period(self):
        """can_vote() returns True if the current time is between pub_date and end_date."""
        pub_time = timezone.now() - datetime.timedelta(days=1)
        end_time = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertIs(question.can_vote(), True)

    def test_cannot_vote_after_end_date(self):
        """can_vote() returns False if the current time is after the end_date."""
        pub_time = timezone.now() - datetime.timedelta(days=2)
        end_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=end_time)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_no_end_date(self):
        """can_vote() returns True if there is no end_date and current time is after pub_date."""
        pub_time = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_time, end_date=None)
        self.assertIs(question.can_vote(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the given number
    of `days` offset to now (negative for questions published in the past, positive
    for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """Tests for the index view of KU Polls."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        question = create_question(question_text="Past Question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    """Tests for the detail view of KU Polls."""

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future redirects to the index page."""
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """The detail view of a question with a pub_date in the past displays the question's text."""
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class UserAuthTest(TestCase):
    """Tests for user authentication and access control."""

    def setUp(self):
        """Set up data for authentication tests."""
        super().setUp()
        self.username = "test_user"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()

        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_user_can_logout(self):
        """A user can log out using the logout URL and is redirected to the login page."""
        logout_url = reverse("logout")
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        response = self.client.post(logout_url)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can log in using the login view."""
        login_url = reverse("login")
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        form_data = {"username": "test_user", "password": "FatChance!"}
        response = self.client.post(login_url, form_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote; unauthenticated users are redirected."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        self.assertEqual(response.status_code, 302)
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)


class VoteLimitTests(TestCase):
    """Tests to ensure vote limitations are enforced."""

    def setUp(self):
        """Set up data for testing voting behavior."""
        # Create a user for the test
        self.user = User.objects.create_user(username='test_user', password='password')
        # Create a question and two choices for the test
        self.question = Question.objects.create(
            question_text='Test Question', pub_date=timezone.now()
        )
        self.choice1 = Choice.objects.create(choice_text='Choice 1', question=self.question)
        self.choice2 = Choice.objects.create(choice_text='Choice 2', question=self.question)

    def test_user_can_vote_once(self):
        """Ensure that a user can only vote once for a question."""
        self.client.login(username='test_user', password='password')
        vote_url = reverse('polls:vote', args=[self.question.id])

        # First vote
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertEqual(response.status_code, 302)  # Should redirect to results page

        # Attempt to change vote
        response = self.client.post(vote_url, {'choice': self.choice2.id})
        self.assertEqual(response.status_code, 302)  # Should still redirect to results

        # Verify that only one vote exists for the user, and it's updated to choice2
        self.assertEqual(Vote.objects.filter(user=self.user, choice__question=self.question).count(), 1)
        updated_vote = Vote.objects.get(user=self.user, choice__question=self.question)
        self.assertEqual(updated_vote.choice, self.choice2)

    def test_anonymous_user_cannot_vote(self):
        """Ensure that an anonymous (unauthenticated) user is redirected to login page when trying to vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertEqual(response.status_code, 302)  # Should redirect to log in

        login_url_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_url_with_next)
