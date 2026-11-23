
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from notifications.views import NotificationListView
from posts.views import CommentDislikeView, CommentLikeView, CommentReplyView, HomeFeedPageView, PostCommentView, PostCreateView, PostDetailView, PostDislikeView, PostLikeView, PostListPageView, PostListView
from profiles.views import FollowToggleView, ProfileEditView, ProfileView, UserListView, UserProfileView

from .views import HomeView, LoginView, RegisterView, LegalView, ContactView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path('profile/<int:pk>/follow/', FollowToggleView.as_view(), name='follow_toggle'),
    path('home/feed-page/', HomeFeedPageView.as_view(), name='home_feed_page'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/page/', PostListPageView.as_view(), name='post_list_page'),
    path('posts/new/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
    path('posts/<int:pk>/dislike/', PostDislikeView.as_view(), name='post_dislike'),
    path('posts/<int:pk>/comment/', PostCommentView.as_view(), name='post_comment'),
    path('comments/<int:pk>/like/', CommentLikeView.as_view(), name='comment_like'),
    path('comments/<int:pk>/dislike/', CommentDislikeView.as_view(), name='comment_dislike'),
    path('comments/<int:pk>/reply/', CommentReplyView.as_view(), name='comment_reply'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('legal/', LegalView.as_view(), name='legal'),
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

