import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Comment, Follow, Group, Post, User, Rating


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, encoded_image = data.split(";base64,")
            extension = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(encoded_image), name="image." + extension
            )

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор юзеров."""

    class Meta:
        fields = "__all__"
        model = User


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комметариев."""

    author = SlugRelatedField(slug_field="username", read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    class Meta:
        fields = "__all__"
        model = Comment
        read_only_fields = ("post", "author")


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Follow
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "following"),
                message="Вы уже подписаны на этого пользователя.",
            ),
        )

    def validate_following(self, value):
        if value == self.context["request"].user:
            raise serializers.ValidationError("Нельзя подписываться на себя.")
        return value


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор групп."""

    class Meta:
        fields = "__all__"
        model = Group


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор постов."""

    author = SlugRelatedField(slug_field="username", read_only=True)
    comments = CommentSerializer(read_only=True, many=True)
    image = Base64ImageField(required=False, allow_null=True)
    # rating = serializers.SerializerMethodField(read_only=True)
    class Meta:
        fields = (
            "id",
            "title",
            "text",
            "created",
            "image",
            "author",
            "group",
            "comments",
            # "rating"
        )
        model = Post

    def get_rating(self, obj):
        rating = Rating.objects.filter(post_id=obj.id).select_related("user", "post")
        if rating:
            return rating[0].rating
        return 0


class RatingSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ("user", "post")

    def validate(self, attrs):
        return attrs