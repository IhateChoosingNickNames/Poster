from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet,
                    RatingViewSet, UserViewSet)

api_v1_router = DefaultRouter()
api_v1_router.register(r"posts", PostViewSet)
api_v1_router.register(r"groups", GroupViewSet)
api_v1_router.register(r"users", UserViewSet)
api_v1_router.register(r"follow", FollowViewSet, basename="user_follows")
api_v1_router.register(
    r"posts/(?P<post_id>[1-9]\d*)/comments",
    CommentViewSet,
    basename="post_comments",
)
api_v1_router.register(
    r"posts/(?P<post_id>[1-9]\d*)/rating",
    RatingViewSet,
    basename="post_rating",
)


urlpatterns = [
    path("v1/", include(api_v1_router.urls)),
    path("v1/", include("djoser.urls")),
    path("v1/", include("djoser.urls.jwt")),
]
