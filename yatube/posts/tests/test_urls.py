from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group
from django.core.cache import cache
from http import HTTPStatus


User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Автор поста
        cls.user = User.objects.create_user('Author_StasBasov')
        # Авторизированный пользователь
        cls.auth_user = User.objects.create_user('AuthUser')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Пост от имени автора
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.templates = [
            "/",
            f"/group/{cls.group.slug}/",
            f"/profile/{cls.user}/",
            f"/posts/{cls.post.id}/",
        ]

    def setUp(self):
        # Пользователь без авторизации
        self.guest_client = Client()
        # Автор поста
        self.author_post = Client()
        self.author_post.force_login(PostsURLTest.user)
        # Авторизированный пользователь
        self.authorized_user = Client()
        self.authorized_user.force_login(PostsURLTest.auth_user)
        cache.clear()

# Проверяем общедоступные страницы
    def test_urls_exists_at_desired_location(self):
        for adress in self.templates:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

# Страницы для авторизированных пользователей
    def test_post_edit(self):
        """Страница редактирования поста 'posts/<int:post_id>/edit/'
        доступ авторизованному автору"""
        response = self.author_post.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_not_authorized_user(self):
        """Страница редактирования поста 'posts/<int:post_id>/edit/'
        пользователь без авторизации"""
        response = self.guest_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        )

    def test_post_create(self):
        """Страница добавления поста 'create/' авторизованному"""
        response = self.authorized_user.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_not_authorized_user(self):
        """Страница добавления поста 'create/' анонимному пользователю"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_unexisting_page(self):
        """Проверка несуществующей страницы"""
        response = self.guest_client.get('/xxxx/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_templates(self):
        """Проверка шаблонов"""
        templates_url = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': f'/profile/{self.post.author}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            'posts/post_create.html': '/create/',
            'posts/post_create.html': '/create/',
        }
        for template, url in templates_url.items():
            with self.subTest(url=url):
                response = self.author_post.get(url)
                self.assertTemplateUsed(response, template)
