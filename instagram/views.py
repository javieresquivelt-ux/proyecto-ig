from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, FormView

from posts.models import Like, Post
from profiles.models import UserProfile
from users.forms import RegistrationForm

from .forms import ContactForm


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'general/home.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        following_users = profile.following.values_list('user', flat=True)
        return Post.objects.filter(user__in=following_users).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['following_ids'] = set(
            profile.following.values_list('user', flat=True),
        )
        context['liked_post_ids'] = set(
            Like.objects.filter(user=self.request.user).values_list('post_id', flat=True),
        )
        context['disliked_post_ids'] = set(
            Post.objects.filter(dislikes=self.request.user).values_list('pk', flat=True),
        )
        return context


class LoginView(DjangoLoginView):
    template_name = 'general/login.html'


class RegisterView(CreateView):
    template_name = 'general/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home')


class LegalView(TemplateView):
    template_name = 'general/legal.html'


class ContactView(FormView):
    template_name = 'general/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        messages.success(self.request, _('Thanks! Your message has been sent.'))
        return super().form_valid(form)
