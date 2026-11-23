from django import forms
from django.utils.translation import gettext_lazy as _

from .models import UserProfile


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(
        label=_("Bio"),
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
    )
    birth_date = forms.DateField(
        label=_("Birth date"),
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio', 'location', 'birth_date')
