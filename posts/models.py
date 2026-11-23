from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(verbose_name=_("Image"), upload_to='post_images/', blank=True, null=True)
    caption = models.TextField(verbose_name=_("Caption"), max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation date"))
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', through='Like')
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_posts', blank=True)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")

    def __str__(self):
        return f"{self.user.email} -> {self.post}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name=_("Content"), max_length=300)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation date"))
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_comments', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} -> {self.post}"
