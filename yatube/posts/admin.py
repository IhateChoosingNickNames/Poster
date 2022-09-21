from django.contrib import admin

from .models import Comment, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "created", "author", "group", "image")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"
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
    prepopulated_fields = {"slug": ("title",)}
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
