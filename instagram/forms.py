from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    SUBJECT_CHOICES = [
        ('general', _('General question')),
        ('account', _('Account and privacy')),
        ('report', _('Report a problem')),
        ('press', _('Press and media')),
        ('partnership', _('Partnership')),
    ]

    name = forms.CharField(label=_('Name'), max_length=100)
    email = forms.EmailField(label=_('Email'))
    subject = forms.ChoiceField(label=_('Subject'), choices=SUBJECT_CHOICES)
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea(attrs={'rows': 4}),
    )
