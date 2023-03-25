from django.db import models
from django.contrib.auth import get_user_model
# https://postimg.cc/ZvhVtmgh
# https://postimg.cc/dDmzsN99
# Create your models here.
User = get_user_model()


class Group(models.Model):

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True, verbose_name="URL")
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        default_related_name = 'posts'
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name="comments",
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст'
    )
    created = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True
    )

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ["-created"]
        default_related_name = "comments"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_author_user_following'
            )
        ]
