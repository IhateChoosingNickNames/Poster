class TemplateMixin:
    """Контейнер хранения шаблонов."""

    INDEX_TEMPLATE = "posts/index.html"
    GROUPS_TEMPLATE = "posts/group_list.html"
    GROUP_LIST_TEMPLATE = "posts/list_of_groups.html"
    SHOW_POST_TEMPLATE = "posts/show_post.html"
    ADD_POST_TEMPLATE = "posts/creation.html"
    POST_PROFILE_TEMPLATE = "posts/profile.html"
    FEEDBACK_TEMPLATE = "posts/feedback.html"


class PaginationMixin:
    """Миксин пагинации."""

    paginate_by = 10
