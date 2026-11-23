from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    COMMENT = 'comment'
    REPLY = 'reply'

    TYPE_CHOICES = [
        (LIKE, _('Like')),
        (DISLIKE, _('Dislike')),
        (COMMENT, _('Comment')),
        (REPLY, _('Reply')),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications',
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications',
    )
    comment = models.ForeignKey(
        'posts.Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications',
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def get_message(self):
        actor = self.actor.display_name
        if self.notification_type == self.LIKE:
            target = _('comment') if self.comment else _('post')
            return _('%(actor)s liked your %(target)s') % {'actor': actor, 'target': target}
        if self.notification_type == self.DISLIKE:
            target = _('comment') if self.comment else _('post')
            return _('%(actor)s disliked your %(target)s') % {'actor': actor, 'target': target}
        if self.notification_type == self.COMMENT:
            return _('%(actor)s commented on your post') % {'actor': actor}
        if self.notification_type == self.REPLY:
            return _('%(actor)s replied to your comment') % {'actor': actor}
        return ''

    def __str__(self):
        return f'{self.actor} -> {self.recipient} ({self.notification_type})'
