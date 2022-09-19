from django.contrib import admin

from .models import Comment, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "created", "author", "group", "image")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"
    # Если вдруг кто-то увидит этот коммент: откуда растут ноги у
    # list_editable? У меня в админке на каждый новый пост происходит
    # однотипный запрос к моделям групп. И ни через какой select_related()
    # это не убирается. -_-
    list_editable = ("group",)
    readonly_fields = ("group",)
    list_select_related = ("author", "group")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "slug",
        "description",
    )
    search_fields = ("title",)
    list_filter = ("slug",)
    empty_value_display = "-пусто-"
    list_editable = ("description",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "text",
        "created",
        "image",
        "child",
        "is_child",
    )
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"
    list_select_related = ("author", "child")
