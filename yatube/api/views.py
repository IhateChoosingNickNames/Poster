from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from posts.models import Group, Post, User, Rating
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer, RatingSerializer, UserSerializer)


class FollowViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                    mixins.ListModelMixin, viewsets.GenericViewSet):
    """Вьюсет подписок."""

    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)

    def get_queryset(self):
        return self.request.user.follower.all().select_related("following")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    """Вьюсет постов."""

    queryset = Post.objects.all().select_related("group", "author").prefetch_related("comments")
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет юзеров."""

    queryset = User.objects.all().prefetch_related("user_permissions", "groups", )
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return post.comments.all().select_related("author", "post")

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        serializer.save(author=self.request.user, post=post)


class RatingViewSet(viewsets.ModelViewSet):
    """Вьюсет групп."""

    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return post.likes.all().select_related("user", "post")

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        rating = Rating.objects.filter(user=self.request.user, post=post)

        if not rating:
            serializer.save(user=self.request.user, post=post)

        else:
            validated_data = {
                "user": self.request.user,
                "rating": serializer.initial_data["rating"]
            }
            serializer.update(instance=rating[0], validated_data=validated_data)
