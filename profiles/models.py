from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(verbose_name=_("Profile picture"), upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(verbose_name=_("Bio"), blank=True)
    location = models.CharField(verbose_name=_("Location"), max_length=30, blank=True)
    birth_date = models.DateField(verbose_name=_("Birth date"), null=True, blank=True)
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name='following',
        through='Follow',
        through_fields=('following', 'follower'),
    )

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self):
        return self.user.email


class Follow(models.Model):
    follower = models.ForeignKey(UserProfile, verbose_name=_("Follower"), on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(UserProfile, verbose_name=_("Following"), on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Follow date"))

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = _("Follow")
        verbose_name_plural = _("Follows")

    def __str__(self):
        return f"{self.follower.user.email} -> {self.following.user.email}"
