from django.test import TestCase, Client
from django.urls import reverse
from Auth.models import CustomUser # Assuming CustomUser is in Auth.models
# If CustomUser is settings.AUTH_USER_MODEL, import get_user_model
# from django.contrib.auth import get_user_model
# CustomUser = get_user_model()

class AuthModelTests(TestCase):

    def test_create_custom_user(self):
        """Test creating a CustomUser instance."""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(str(user), 'testuser')

class AuthViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_home_view_status_code(self):
        """Test the home page (Auth index) status code."""
        url = reverse('home') # Assuming 'home' is the name of Auth's index view
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_status_code(self):
        """Test the login page status code."""
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_view_status_code(self):
        """Test the register page status code."""
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logout_view_redirects(self):
        """Test the logout view redirects to login."""
        self.client.login(username='testuser', password='password123')
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login'))
