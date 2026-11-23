from .models import Notification


def create_notification(recipient, actor, notification_type, post=None, comment=None):
    if recipient is None or recipient == actor:
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        post=post,
        comment=comment,
    )
