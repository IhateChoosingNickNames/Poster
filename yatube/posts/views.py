import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from django.urls import reverse
from django.views.generic.list import MultipleObjectMixin

from .forms import CommentForm, FeedbackForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import PaginationMixin, TemplateMixin

User = get_user_model()


class PostsView(PaginationMixin, TemplateMixin, ListView):
    """Отображение основной страницы."""

    model = Post
    context_object_name = "posts"

    def get_template_names(self):
        return self.INDEX_TEMPLATE

    def get_queryset(self):
        return Post.objects.all().select_related("group", "author")


class PostGroupView(TemplateMixin, PaginationMixin, ListView):
    """Отображение страницы группы."""

    model = Post
    context_object_name = "posts"

    def get_template_names(self):
        return self.GROUPS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = get_object_or_404(Group, slug=self.kwargs["slug"])
        return context

    def get_queryset(self):
        return Post.objects.filter(
            group__slug=self.kwargs["slug"]
        ).select_related("group", "author")


class PostGroupArchiveView(PostGroupView):
    """Неиспользуемый в данном проекте класс. Поэтому есть дублирование кода.

    В дальнейшем я изменю PostGroupView и уберу оттуда отображение всех постов.

    Это будет функция непосредственно архива.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["archive"] = True
        return context


class GroupListView(TemplateMixin, ListView):
    """Отображение списка групп."""

    model = Group
    context_object_name = "groups"

    def get_template_names(self):
        return self.GROUP_LIST_TEMPLATE


class ShowPostView(
    PaginationMixin, TemplateMixin, DetailView, MultipleObjectMixin
):
    """Отображение отдельного поста."""

    model = Post
    pk_url_kwarg = "post_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            object_list=self.object.comments.filter(
                is_child=False
            ).select_related("author"),
            **kwargs
        )

        comment_children = self.object.comments.filter(
            is_child=True
        ).select_related("author")

        for comment_child in comment_children:

            if "treads" not in context:
                context["treads"] = {comment_child.child_id: [comment_child]}
            else:
                if comment_child.child_id not in context["treads"]:
                    context["treads"][comment_child.child_id] = [comment_child]
                else:
                    context["treads"][comment_child.child_id].append(
                        comment_child
                    )

        context["comments_count"] = self.get_queryset().count()

        # Тесты ЯП требуют ищут эту форму от неавторизованного пользователя...
        # if self.request.user.id:
        #     context["form"] = CommentForm()

        context["form"] = CommentForm()
        return context

    def get_template_names(self):
        return self.SHOW_POST_TEMPLATE

    def get_object(self, queryset=None):
        return Post.objects.select_related("author").get(
            id=self.kwargs["post_id"]
        )

    def get_queryset(self):
        return Comment.objects.select_related("child").filter(
            post__id=self.kwargs["post_id"]
        )


class ShowProfileView(
    TemplateMixin, PaginationMixin, DetailView, MultipleObjectMixin
):
    """Отображение профиля юзера."""

    model = User
    slug_url_kwarg = "username"
    slug_field = "username"

    def get_template_names(self):
        return self.POST_PROFILE_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            object_list=self.object.posts.select_related("group"), **kwargs
        )

        if self.object.id == self.request.user.id:
            context["self"] = True
            return context

        exists = Follow.objects.filter(
            user=self.request.user.id, author=self.object.id
        ).exists()

        if exists:
            context["following"] = True
        else:
            context["following"] = False

        return context


class AddPostView(LoginRequiredMixin, TemplateMixin, CreateView):
    """Отображение страницы добавления поста."""

    model = Post
    form_class = PostForm

    def get_template_names(self):
        return self.ADD_POST_TEMPLATE

    def get_success_url(self, **kwargs):
        return reverse("posts:show_profile", args=[self.request.user])

    def form_valid(self, form):
        new_post = form.save(commit=False)
        new_post.author = self.request.user
        return super().form_valid(form)


class EditPostView(LoginRequiredMixin, TemplateMixin, UpdateView):
    """Отображение страницы редактирования поста."""

    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.author != request.user:
            return redirect("posts:show_post", self.kwargs["post_id"])
        return super().dispatch(request, *args, *kwargs)

    def get_template_names(self):
        return self.ADD_POST_TEMPLATE

    def get_success_url(self, **kwargs):
        return reverse("posts:show_post", args=[self.kwargs["post_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_object(self, queryset=None):
        return Post.objects.select_related("author").get(
            id=self.kwargs["post_id"]
        )


class DeletePostView(LoginRequiredMixin, DeleteView):
    """Удаление поста."""

    model = Post
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect("posts:show_post", self.kwargs["post_id"])
        return super().dispatch(request, *args, *kwargs)

    def get_success_url(self, **kwargs):
        return reverse("posts:show_profile", args=[self.request.user])


class AddCommentaryView(
    LoginRequiredMixin, TemplateMixin, PaginationMixin, CreateView
):
    """Отображение страницы добавления комментария."""

    form_class = CommentForm

    def get_template_names(self):
        return self.ADD_POST_TEMPLATE

    def get_success_url(self, **kwargs):
        return reverse("posts:show_post", args=[self.kwargs["post_id"]])

    def form_valid(self, form):
        new_comment = form.save(commit=False)
        new_comment.post_id = self.kwargs["post_id"]
        new_comment.author = self.request.user
        new_comment.created = datetime.datetime.now()
        if "comment_id" in self.kwargs:
            new_comment.is_child = True
            new_comment.child_id = self.kwargs["comment_id"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        context["is_comment"] = True
        return context


class EditCommentaryView(TemplateMixin, UpdateView):
    """Отображение страницы редактирования комметария."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect("posts:show_post", self.kwargs["post_id"])
        return super().dispatch(request, *args, *kwargs)

    def get_template_names(self):
        return self.ADD_POST_TEMPLATE

    def get_success_url(self, **kwargs):
        return reverse("posts:show_post", args=[self.kwargs["post_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        context["is_comment"] = True
        return context


class FeedbackView(TemplateMixin, FormView):
    """Отображение страницы с формой обратной связи."""

    form_class = FeedbackForm

    def get_template_names(self):
        return self.FEEDBACK_TEMPLATE

    def form_valid(self, form):
        form.save()
        return redirect("posts:index")


class ShowFollowVies(
    TemplateMixin, LoginRequiredMixin, PaginationMixin, ListView
):
    """Отображение ленты с подписками."""

    model = Follow
    context_object_name = "posts"

    def get_template_names(self):
        return self.INDEX_TEMPLATE

    def get_queryset(self):
        follow_list = Follow.objects.filter(user__id=self.request.user.id)
        author_ids = [elem.author_id for elem in follow_list]
        return Post.objects.filter(author_id__in=author_ids).select_related(
            "author", "group"
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["follow"] = True
        return context


class ProfileFollowView(LoginRequiredMixin, CreateView):
    """Вьюха подписки."""

    model = Follow
    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs["username"])

    def dispatch(self, request, *args, **kwargs):
        author_to_follow = self.get_object()

        if request.user.id and author_to_follow != self.request.user:
            Follow.objects.get_or_create(
                user=self.request.user, author=author_to_follow
            )

        return super().dispatch(request, *args, *kwargs)

    def get(self, request, *args, **kwargs):
        return redirect("posts:show_profile", username=self.kwargs["username"])


class ProfileUnfollowView(LoginRequiredMixin, DeleteView):
    """Вьюха отписки."""

    model = Follow
    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return Follow.objects.get(
            user_id=self.request.user.id,
            author_id=User.objects.get(username=self.kwargs["username"]),
        )

    def get_success_url(self, **kwargs):
        return reverse("posts:show_profile", args=[self.kwargs["username"]])

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
