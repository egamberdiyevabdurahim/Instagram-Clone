from django.urls import path

from app_post import views


urlpatterns = [
    path('', views.PostListView.as_view()),
    path('<int:pk>/', views.PostDetailView.as_view()),
    path('user/<int:user_id>/', views.PostByUserListView.as_view()),
    path('<int:post_id>/like/', views.LikePostView.as_view()),

    path('comment/', views.CommentListView.as_view()),
    path('<int:post_id>/comment/', views.CommentByPostListView.as_view()),
    path('comment/<int:pk>/', views.CommentDetailView.as_view()),
    path('comment/<int:comment_id>/like/', views.LikeCommentView.as_view()),

    path('story/', views.StoryListView.as_view()),
    path('story/<int:pk>/', views.StoryDetailView.as_view()),
    path('story/<int:story_id>/like/', views.LikeStoryView.as_view()),
]