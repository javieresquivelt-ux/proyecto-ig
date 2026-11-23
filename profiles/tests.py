from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Follow, UserProfile

User = get_user_model()


class ProfileSignalTests(TestCase):
    def test_profile_auto_created_on_user_creation(self):
        user = User.objects.create_user('a@example.com', 'password123')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class FollowModelTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('u1@example.com', 'password123')
        self.u2 = User.objects.create_user('u2@example.com', 'password123')
        self.p1 = UserProfile.objects.get(user=self.u1)
        self.p2 = UserProfile.objects.get(user=self.u2)

    def test_follow_counts(self):
        Follow.objects.create(follower=self.p1, following=self.p2)
        self.assertEqual(self.p1.following.count(), 1)
        self.assertEqual(self.p2.followers.count(), 1)
        self.assertEqual(self.p1.followers.count(), 0)

    def test_follow_unique_together(self):
        Follow.objects.create(follower=self.p1, following=self.p2)
        with self.assertRaises(Exception):
            Follow.objects.create(follower=self.p1, following=self.p2)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'a@example.com', 'password123', first_name='Ana', last_name='Lopez',
        )
        self.other = User.objects.create_user(
            'b@example.com', 'password123', first_name='Bruno', last_name='Perez',
        )

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_user_list_excludes_superuser_and_self(self):
        User.objects.create_superuser('admin@example.com', 'password123')
        self.client.force_login(self.user)
        html = self.client.get(reverse('user_list')).content.decode()
        self.assertEqual(html.count('Ana Lopez'), 1)      # solo en el header
        self.assertEqual(html.count('Bruno Perez'), 1)    # visible en la lista
        self.assertNotIn('admin@example.com', html)

    def test_follow_toggle(self):
        self.client.force_login(self.user)
        target = UserProfile.objects.get(user=self.other)
        self.client.post(reverse('follow_toggle', args=[target.pk]))
        self.assertTrue(Follow.objects.filter(follower__user=self.user, following=target).exists())
        self.client.post(reverse('follow_toggle', args=[target.pk]))
        self.assertFalse(Follow.objects.filter(follower__user=self.user, following=target).exists())

    def test_profile_edit_updates_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('profile_edit'),
            {'bio': 'nueva bio', 'location': 'Madrid', 'birth_date': ''},
        )
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.bio, 'nueva bio')
        self.assertEqual(profile.location, 'Madrid')
