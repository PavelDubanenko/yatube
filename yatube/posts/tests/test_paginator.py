from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
# from django import forms
from ..models import Post, Group

User = get_user_model()


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Автор поста
        cls.user = User.objects.create_user(username='Author_StasBasov')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Пост от имени автора
        cls.post = Post.objects.bulk_create(
            Post(
                text=f'Это пост под номером: {i}',
                author=cls.user,
                group=cls.group,
            )
            for i in range(1, 14)
        )

    def setUp(self):
        # Автор поста
        self.author_post = Client()
        self.author_post.force_login(PostsPagesTest.user)

    def test_first_page_contains_ten_records(self):
        response = self.author_post.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.author_post.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_group_paginator(self):
        """Проверка пажинатора на странице отсортированной по группе"""
        response = self.author_post.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        zapisulku = list(Post.objects.filter(group_id=self.group.id)[:10])
        self.assertEqual(list(response.context["page_obj"]), zapisulku)
