from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from Simulator.models import Simulator, Chapter, Question, AnswerOption, SimulatorAttempt, UserAnswer, SimulatorLevel, ChapterType
import datetime

CustomUser = get_user_model()

class SimulatorModelTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='simtestuser', password='password')
        self.simulator = Simulator.objects.create(name='Test Simulator', level=SimulatorLevel.EASY)
        self.chapter = Chapter.objects.create(
            simulator=self.simulator,
            order=1,
            chapter_type=ChapterType.SENTENCE_COMPLETION,
            title='Test Chapter SC',
            time_limit=10
        )
        self.question = Question.objects.create(
            chapter=self.chapter,
            order=1,
            description='Test Question Desc'
        )
        self.answer_option = AnswerOption.objects.create(
            question=self.question,
            order=1,
            description='Test Answer Option',
            is_correct=True
        )

    def test_simulator_creation(self):
        self.assertEqual(self.simulator.name, 'Test Simulator')
        self.assertEqual(str(self.simulator), 'Test Simulator')

    def test_chapter_creation(self):
        self.assertEqual(self.chapter.title, 'Test Chapter SC')
        self.assertEqual(str(self.chapter), f"{self.simulator} - chapter number 1 - SC")

    def test_question_creation(self):
        self.assertEqual(self.question.description, 'Test Question Desc')
        # str(self.question) includes chapter which includes simulator, so checking part of it
        self.assertTrue(f"question number 1" in str(self.question))


    def test_answer_option_creation(self):
        self.assertEqual(self.answer_option.description, 'Test Answer Option')
        self.assertTrue(self.answer_option.is_correct)
        self.assertTrue(f"Option number 1" in str(self.answer_option))

    def test_simulator_attempt_creation(self):
        attempt = SimulatorAttempt.objects.create(user=self.user, simulator=self.simulator)
        self.assertEqual(attempt.user, self.user)
        self.assertEqual(attempt.simulator, self.simulator)
        self.assertTrue(f"{self.user.username} - {self.simulator.name}" in str(attempt))

    def test_user_answer_creation(self):
        attempt = SimulatorAttempt.objects.create(user=self.user, simulator=self.simulator)
        user_answer = UserAnswer.objects.create(
            user=self.user,
            simulator_attempt=attempt,
            question=self.question,
            selected_option=self.answer_option,
            timestamp=datetime.datetime.now()
        )
        self.assertEqual(user_answer.selected_option, self.answer_option)
        self.assertEqual(str(user_answer), f"{self.user.username} - {self.answer_option}")


class SimulatorViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='simviewuser', password='password')
        self.simulator = Simulator.objects.create(name='View Test Sim', level=SimulatorLevel.EASY)
        # Login the user for views that might require authentication
        self.client.login(username='simviewuser', password='password')


    def test_simulator_list_view_status_code(self):
        """Test the simulator list page status code."""
        url = reverse('simulator_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_start_simulator_view_status_code(self):
        """Test the start simulator page status code (for an existing simulator)."""
        url = reverse('start_simulator', args=[self.simulator.id])
        response = self.client.get(url)
        # This view creates an attempt and then renders a page.
        # It might redirect if user not authenticated properly, but setUp logs user in.
        self.assertEqual(response.status_code, 200)
        # Check if an attempt was created
        self.assertTrue(SimulatorAttempt.objects.filter(user=self.user, simulator=self.simulator).exists())
