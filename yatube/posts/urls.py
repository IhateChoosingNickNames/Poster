from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = "posts"
CACHE_TIMER_SECONDS = 20

urlpatterns = [
    path(
        "",
        cache_page(CACHE_TIMER_SECONDS, cache="default", key_prefix="index")(
            views.PostsView.as_view()
        ),
        name="index",
    ),
    path("follow/", views.ShowFollowVies.as_view(), name="show_follows"),
    path("feedback/", views.FeedbackView.as_view(), name="feedback"),
    path("group/list/", views.GroupListView.as_view(), name="real_group_list"),
    path(
        "group/<slug:slug>/", views.PostGroupView.as_view(), name="group_list"
    ),
    path(
        "posts/<int:post_id>/edit/",
        views.EditPostView.as_view(),
        name="post_edit",
    ),
    path(
        "posts/<int:post_id>/delete/",
        views.DeletePostView.as_view(),
        name="post_delete",
    ),
    path(
        "posts/<int:post_id>/<int:comment_id>/comment/",
        views.AddCommentaryView.as_view(),
        name="comment_comment",
    ),
    path(
        "posts/<int:post_id>/<int:comment_id>/edit/",
        views.EditCommentaryView.as_view(),
        name="post_comment_edit",
    ),
    path(
        "posts/<int:post_id>/comment/",
        views.AddCommentaryView.as_view(),
        name="post_comment",
    ),
    path(
        "posts/<int:post_id>/", views.ShowPostView.as_view(), name="show_post"
    ),
    path(
        "posts/<int:post_id>/like/",
        views.RatingView.as_view(),
        name="post_like"
    ),
    path(
        "posts/<int:post_id>/dislike/",
        views.RatingView.as_view(),
        name="post_dislike"
    ),
    path("create/", views.AddPostView.as_view(), name="post_create"),
    path(
        "profile/<slug:username>/",
        views.ShowProfileView.as_view(),
        name="show_profile",
    ),
    path(
        "profile/<slug:username>/follow/",
        views.ProfileFollowView.as_view(),
        name="profile_follow",
    ),
    path(
        "profile/<slug:username>/unfollow/",
        views.ProfileUnfollowView.as_view(),
        name="profile_unfollow",
    ),
]
