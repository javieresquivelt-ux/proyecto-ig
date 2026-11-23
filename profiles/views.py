from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from .forms import ProfileForm
from .models import Follow, UserProfile


class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'profiles/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.user.posts.all()
        context['comments'] = self.object.user.comments.all()
        context['followers'] = self.object.followers.all()
        context['following'] = self.object.following.all()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = 'profiles/profile_edit.html'
    context_object_name = 'profile'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully.'))
        return super().form_valid(form)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'profiles/user_profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['is_following'] = Follow.objects.filter(
            follower=current, following=self.object,
        ).exists()
        context['is_self'] = self.object.user == self.request.user
        context['posts'] = self.object.user.posts.all()
        return context


class UserListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'profiles/user_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return UserProfile.objects.exclude(user__is_superuser=True).exclude(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['following_ids'] = set(
            current.following.values_list('pk', flat=True),
        )
        return context


class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(UserProfile, pk=pk)
        current, _ = UserProfile.objects.get_or_create(user=request.user)
        if target != current:
            follow = Follow.objects.filter(follower=current, following=target)
            if follow.exists():
                follow.delete()
            else:
                Follow.objects.create(follower=current, following=target)
        next_url = request.POST.get('next') or reverse(
            'user_profile', kwargs={'pk': target.pk},
        )
        return redirect(next_url)
