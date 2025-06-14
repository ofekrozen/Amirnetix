from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from Simulator.models import Simulator, SimulatorAttempt, SimulatorLevel # For creating test data
from Management.models import Word, Student_Word_Knowledge, Level_Choices # For creating test data
import datetime

CustomUser = get_user_model()

class AnalysisViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='analysistestuser',
            password='password',
            first_name='Analysis',
            last_name='User'
        )
        self.client.login(username='analysistestuser', password='password')

        # Setup data that Analysis views might depend on
        self.simulator = Simulator.objects.create(name='Analysis Test Sim', level=SimulatorLevel.EASY)
        self.attempt = SimulatorAttempt.objects.create(user=self.user, simulator=self.simulator)

        self.word = Word.objects.create(eng_word='testword', heb_word='מילתבדיקה', word_level=Level_Choices.PERFECT)
        Student_Word_Knowledge.objects.create(
            student=self.user,
            word=self.word,
            familiarity=Level_Choices.PERFECT,
            selection_date=datetime.datetime.now()
        )

    def test_analysis_index_view_status_code(self):
        """Test the main Analysis index page status code."""
        url = reverse('analysis') # Assuming 'analysis' is the name of Analysis's index view
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_vocab_home_view_status_code(self):
        """Test the vocabulary home page status code."""
        url = reverse('vocab_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_english_vocab_view_status_code(self):
        """Test the English vocabulary learning page status code."""
        url = reverse('english_vocab')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_analyze_simulator_view_status_code(self):
        """Test the analyze_simulator page status code for an existing attempt."""
        # Ensure the URL name is 'analyze_simulator' and it takes 'attempt_id'
        url = reverse('analyze_simulator', kwargs={'attempt_id': self.attempt.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_familiarity_view_requires_post(self):
        """Test that update_familiarity view expects POST and fails for GET."""
        url = reverse('update_familiarity')
        response = self.client.get(url)
        # Expecting 400 or 405 for GET if it only handles POST and JSON
        self.assertIn(response.status_code, [400, 405])

    def test_update_familiarity_view_success(self):
        """Test successful update of word familiarity via POST JSON."""
        url = reverse('update_familiarity')
        # Data to send in POST request
        payload = {
            'word_id': self.word.id,
            'fam_level': Level_Choices.PARTIALLY.value # Send the actual value
        }
        response = self.client.post(
            url,
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response['success'])

        # Verify the change in the database
        updated_knowledge = Student_Word_Knowledge.objects.get(student=self.user, word=self.word)
        self.assertEqual(updated_knowledge.familiarity, Level_Choices.PARTIALLY)
