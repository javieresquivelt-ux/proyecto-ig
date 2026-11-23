from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from notifications.utils import create_notification
from profiles.models import UserProfile

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Post published!'))
        return super().form_valid(form)


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_comments = self.object.comments.all()
        context['comments'] = all_comments.filter(parent=None)
        context['total_comments'] = all_comments.count()
        context['comment_form'] = CommentForm()
        context['liked_post_ids'] = set(
            Like.objects.filter(user=self.request.user, post=self.object).values_list('post_id', flat=True),
        )
        context['disliked_post_ids'] = set(
            self.object.dislikes.filter(pk=self.request.user.pk).values_list('pk', flat=True),
        )
        context['liked_comment_ids'] = set(
            all_comments.filter(likes=self.request.user).values_list('pk', flat=True),
        )
        context['disliked_comment_ids'] = set(
            all_comments.filter(dislikes=self.request.user).values_list('pk', flat=True),
        )
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['following_ids'] = set(
            profile.following.values_list('user', flat=True),
        )
        return context


class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            post.dislikes.remove(request.user)
            create_notification(post.user, request.user, 'like', post=post)
        else:
            like.delete()
        return JsonResponse({
            'liked': Like.objects.filter(user=request.user, post=post).exists(),
            'disliked': post.dislikes.filter(pk=request.user.pk).exists(),
            'likes_count': post.likes.count(),
            'dislikes_count': post.dislikes.count(),
        })


class PostDislikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.dislikes.filter(pk=request.user.pk).exists():
            post.dislikes.remove(request.user)
        else:
            post.dislikes.add(request.user)
            Like.objects.filter(user=request.user, post=post).delete()
            create_notification(post.user, request.user, 'dislike', post=post)
        return JsonResponse({
            'liked': Like.objects.filter(user=request.user, post=post).exists(),
            'disliked': post.dislikes.filter(pk=request.user.pk).exists(),
            'likes_count': post.likes.count(),
            'dislikes_count': post.dislikes.count(),
        })


class PostCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            create_notification(post.user, request.user, 'comment', post=post, comment=comment)
        return redirect('post_detail', pk=post.pk)


class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        parent = get_object_or_404(Comment, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = parent.post
            reply.user = request.user
            reply.parent = parent
            reply.save()
            create_notification(parent.user, request.user, 'reply', post=parent.post, comment=parent)
        return redirect('post_detail', pk=parent.post.pk)


class CommentLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.likes.filter(pk=request.user.pk).exists():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
            comment.dislikes.remove(request.user)
            create_notification(comment.user, request.user, 'like', post=comment.post, comment=comment)
        return JsonResponse({
            'liked': comment.likes.filter(pk=request.user.pk).exists(),
            'disliked': comment.dislikes.filter(pk=request.user.pk).exists(),
            'likes_count': comment.likes.count(),
            'dislikes_count': comment.dislikes.count(),
        })


class CommentDislikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.dislikes.filter(pk=request.user.pk).exists():
            comment.dislikes.remove(request.user)
        else:
            comment.dislikes.add(request.user)
            comment.likes.remove(request.user)
            create_notification(comment.user, request.user, 'dislike', post=comment.post, comment=comment)
        return JsonResponse({
            'liked': comment.likes.filter(pk=request.user.pk).exists(),
            'disliked': comment.dislikes.filter(pk=request.user.pk).exists(),
            'likes_count': comment.likes.count(),
            'dislikes_count': comment.dislikes.count(),
        })


def _post_context(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return {
        'following_ids': set(profile.following.values_list('user', flat=True)),
        'liked_post_ids': set(
            Like.objects.filter(user=request.user).values_list('post_id', flat=True),
        ),
        'disliked_post_ids': set(
            Post.objects.filter(dislikes=request.user).values_list('pk', flat=True),
        ),
    }


def _paginated_grid_response(queryset, request, per_page=10):
    try:
        page_number = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page_number = 1
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    context = _post_context(request)
    context['posts'] = page_obj.object_list
    html = render_to_string('posts/_post_grid.html', context, request=request)
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


class HomeFeedPageView(LoginRequiredMixin, View):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        following_users = profile.following.values_list('user', flat=True)
        queryset = Post.objects.filter(user__in=following_users).order_by('-created_at')
        return _paginated_grid_response(queryset, request)


class PostListPageView(LoginRequiredMixin, View):
    def get(self, request):
        queryset = Post.objects.all().order_by('-created_at')
        return _paginated_grid_response(queryset, request)
