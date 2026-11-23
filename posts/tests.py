import io
import os

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from profiles.models import Follow, UserProfile
from .models import Comment, Like, Post

User = get_user_model()


def make_image(name='test.jpg'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buf, 'JPEG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/jpeg')


class PostCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('a@example.com', 'password123')

    def test_create_requires_login(self):
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('post_create'), {'caption': 'nuevo post', 'image': make_image()},
        )
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(user=self.user)
        self.assertEqual(post.caption, 'nuevo post')
        self.assertTrue(post.image)


class PostEditDeleteTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author@example.com', 'password123')
        self.other = User.objects.create_user('other@example.com', 'password123')
        self.post = Post.objects.create(user=self.author, caption='original')

    def test_edit_own_post(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse('post_edit', args=[self.post.pk]), {'caption': 'editado'})
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.caption, 'editado')

    def test_edit_other_post_forbidden(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('post_edit', args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)

    def test_delete_own_post(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse('post_delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_other_post_forbidden(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('post_delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_removes_image_file(self):
        self.post.image.save('x.jpg', make_image(), save=True)
        path = self.post.image.path
        self.assertTrue(os.path.exists(path))
        self.client.force_login(self.author)
        self.client.post(reverse('post_delete', args=[self.post.pk]))
        self.assertFalse(os.path.exists(path))


class LikeDislikeTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author@example.com', 'password123')
        self.user = User.objects.create_user('user@example.com', 'password123')
        self.post = Post.objects.create(user=self.author, caption='hola')

    def test_like_unlike(self):
        self.client.force_login(self.user)
        data = self.client.post(reverse('post_like', args=[self.post.pk])).json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        data = self.client.post(reverse('post_like', args=[self.post.pk])).json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)

    def test_like_dislike_mutually_exclusive(self):
        self.client.force_login(self.user)
        self.client.post(reverse('post_like', args=[self.post.pk]))
        data = self.client.post(reverse('post_dislike', args=[self.post.pk])).json()
        self.assertFalse(data['liked'])
        self.assertTrue(data['disliked'])


class CommentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author@example.com', 'password123')
        self.user = User.objects.create_user('user@example.com', 'password123')
        self.post = Post.objects.create(user=self.author, caption='hola')

    def test_add_comment(self):
        self.client.force_login(self.user)
        self.client.post(reverse('post_comment', args=[self.post.pk]), {'content': 'comentario'})
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)

    def test_add_reply(self):
        comment = Comment.objects.create(post=self.post, user=self.author, content='raiz')
        self.client.force_login(self.user)
        self.client.post(reverse('comment_reply', args=[comment.pk]), {'content': 'respuesta'})
        self.assertEqual(Comment.objects.filter(parent=comment).count(), 1)


class HomeFeedTests(TestCase):
    def setUp(self):
        self.me = User.objects.create_user('me@example.com', 'password123')
        self.followed = User.objects.create_user('followed@example.com', 'password123')
        self.not_followed = User.objects.create_user('no@example.com', 'password123')
        self.me_profile = UserProfile.objects.get(user=self.me)
        self.followed_profile = UserProfile.objects.get(user=self.followed)
        Follow.objects.create(follower=self.me_profile, following=self.followed_profile)

    def test_home_shows_only_followed_posts(self):
        Post.objects.create(user=self.followed, caption='de seguido')
        Post.objects.create(user=self.not_followed, caption='de no seguido')
        self.client.force_login(self.me)
        html = self.client.get(reverse('home')).content.decode()
        self.assertIn('de seguido', html)
        self.assertNotIn('de no seguido', html)


class PostDetailTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author@example.com', 'password123')
        self.post = Post.objects.create(user=self.author, caption='hola')

    def test_detail_shows_edit_buttons_only_for_author(self):
        other = User.objects.create_user('other@example.com', 'password123')
        self.client.force_login(self.author)
        self.assertContains(self.client.get(reverse('post_detail', args=[self.post.pk])), 'Edit')
        self.client.force_login(other)
        self.assertNotContains(self.client.get(reverse('post_detail', args=[self.post.pk])), 'Edit')
