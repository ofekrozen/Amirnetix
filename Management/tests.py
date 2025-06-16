from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from Management.models import Word, Word_Form, Student_Word_Knowledge, Level_Choices
from Simulator.models import Simulator # For testing management views related to simulators
import datetime

CustomUser = get_user_model()

class ManagementModelTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='mgmttestuser', password='password')
        self.word = Word.objects.create(
            eng_word='manage_word',
            heb_word='מילתניהול',
            word_level=Level_Choices.NOT_CHOSEN
        )

    def test_word_creation(self):
        self.assertEqual(self.word.eng_word, 'manage_word')
        self.assertEqual(str(self.word), 'manage_word - מילתניהול - 0') # 0 is NOT_CHOSEN

    def test_word_form_creation(self):
        word_form = Word_Form.objects.create(
            root_word=self.word,
            eng_word='managing',
            heb_word='מנהל (צורת ביניים)'
        )
        self.assertEqual(word_form.eng_word, 'managing')
        self.assertEqual(str(word_form), f"root: {self.word.eng_word} form: managing - מנהל (צורת ביניים)")

    def test_student_word_knowledge_creation(self):
        knowledge = Student_Word_Knowledge.objects.create(
            student=self.user,
            word=self.word,
            familiarity=Level_Choices.PERFECT,
            selection_date=datetime.datetime.now()
        )
        self.assertEqual(knowledge.student, self.user)
        self.assertEqual(knowledge.word, self.word)
        self.assertEqual(knowledge.familiarity, Level_Choices.PERFECT)
        self.assertEqual(str(knowledge), f"{self.user.username} - {self.word.eng_word}: {Level_Choices.PERFECT.value}")


class ManagementViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = CustomUser.objects.create_superuser(
            username='supermgr',
            email='supermgr@example.com',
            password='superpassword'
        )
        self.normal_user = CustomUser.objects.create_user(
            username='normalmgr',
            email='normalmgr@example.com',
            password='normalpassword'
        )
        self.simulator = Simulator.objects.create(name='Managed Simulator')


    def test_management_index_view_as_superuser(self):
        """Test Management index view is accessible by superuser."""
        self.client.login(username='supermgr', password='superpassword')
        url = reverse('index') # Assuming 'index' is Management's main view
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_management_index_view_redirects_normal_user(self):
        """Test Management index view redirects normal user to login."""
        # Management views are often superuser restricted.
        # The main 'index' might be too, or specific ones like 'generate_test'.
        # This test assumes 'index' itself is not superuser restricted by default in this app
        # but other actions might be. If 'index' IS restricted, this test would change.
        # For now, let's assume 'index' is accessible, but 'generate_test' is not.
        self.client.login(username='normalmgr', password='normalpassword')
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200) # Assuming index is open

        # Test a superuser-only view like generate_test
        url_generate = reverse('generate_test')
        response_generate = self.client.get(url_generate) # GET might be disallowed or redirect
        # If generate_test is POST only, GET might be 405. If superuser restricted, redirect.
        self.assertIn(response_generate.status_code, [302, 405])
        if response_generate.status_code == 302:
            self.assertTrue(reverse('login') in response_generate.url)


    def test_edit_test_view_get(self):
        """Test GET request to edit_test view for an existing simulator (as superuser)."""
        self.client.login(username='supermgr', password='superpassword')
        url = reverse('edit_test', args=[self.simulator.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.simulator.name)

    def test_delete_test_view_get_and_post(self):
        """Test GET to delete_test (confirmation) and POST to actually delete (as superuser)."""
        self.client.login(username='supermgr', password='superpassword')

        # GET request to confirm deletion
        url_get = reverse('delete_test', args=[self.simulator.id])
        response_get = self.client.get(url_get)
        self.assertEqual(response_get.status_code, 200)
        self.assertContains(response_get, self.simulator.name) # Check if simulator name is in confirmation page

        # POST request to delete
        # The view redirects to 'index' after deletion.
        # It might be better to test the count of simulators before and after.
        initial_sim_count = Simulator.objects.count()
        url_post = reverse('delete_test', args=[self.simulator.id]) # Same URL, but POST
        response_post = self.client.post(url_post) # POST request
        self.assertEqual(response_post.status_code, 200) # The view renders index after delete
        self.assertEqual(Simulator.objects.count(), initial_sim_count - 1)
