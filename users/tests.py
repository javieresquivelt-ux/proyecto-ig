from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user('test@example.com', 'password123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'password123')

    def test_create_superuser(self):
        user = User.objects.create_superuser('admin@example.com', 'password123')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_display_name_with_name(self):
        user = User.objects.create_user(
            'ana@example.com', 'password123', first_name='Ana', last_name='Lopez',
        )
        self.assertEqual(user.display_name, 'Ana Lopez')

    def test_display_name_falls_back_to_email(self):
        user = User.objects.create_user('anon@example.com', 'password123')
        self.assertEqual(user.display_name, 'anon@example.com')

    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')
