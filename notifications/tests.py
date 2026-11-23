from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Comment, Post
from .models import Notification

User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author@example.com', 'password123')
        self.actor = User.objects.create_user('actor@example.com', 'password123')
        self.post = Post.objects.create(user=self.author, caption='hola')

    def test_like_generates_notification(self):
        self.client.force_login(self.actor)
        self.client.post(reverse('post_like', args=[self.post.pk]))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author, actor=self.actor, notification_type='like',
            ).exists()
        )

    def test_no_notification_for_own_action(self):
        self.client.force_login(self.author)
        self.client.post(reverse('post_like', args=[self.post.pk]))
        self.assertFalse(Notification.objects.filter(recipient=self.author, actor=self.author).exists())

    def test_comment_generates_notification(self):
        self.client.force_login(self.actor)
        self.client.post(reverse('post_comment', args=[self.post.pk]), {'content': 'comentario'})
        self.assertTrue(
            Notification.objects.filter(recipient=self.author, notification_type='comment').exists()
        )

    def test_reply_generates_notification(self):
        comment = Comment.objects.create(post=self.post, user=self.author, content='raiz')
        self.client.force_login(self.actor)
        self.client.post(reverse('comment_reply', args=[comment.pk]), {'content': 'respuesta'})
        self.assertTrue(
            Notification.objects.filter(recipient=self.author, notification_type='reply').exists()
        )

    def test_notification_list_marks_read(self):
        Notification.objects.create(
            recipient=self.author, actor=self.actor, notification_type='like', post=self.post,
        )
        self.client.force_login(self.author)
        self.client.get(reverse('notification_list'))
        self.assertFalse(Notification.objects.filter(recipient=self.author, is_read=False).exists())
