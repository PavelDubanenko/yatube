from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Post, Group, Comment, Follow

User = get_user_model()


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Автор поста
        cls.user = User.objects.create_user('Author_StasBasov')
        # Авторизированный пользователь
        cls.auth_user = User.objects.create_user('AuthUser')

        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание группы',
        )
        # Пост от имени автора
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        # Пользователь без авторизации
        self.guest_client = Client()
        # Автор поста
        self.author_post = Client()
        self.author_post.force_login(PostsPagesTest.user)
        # Авторизированный пользователь
        self.authorized_user = Client()
        self.authorized_user.force_login(PostsPagesTest.auth_user)

    def test_templates(self):
        """URL адрес использует соответсвенный шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', args=(self.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=(self.user.username,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=(self.post.pk,)
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', args=(self.post.pk,)
            ): 'posts/post_create.html',
        }
        for reverse_name, templates in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_post.get(reverse_name)
                self.assertTemplateUsed(response, templates)
        # def url(url, **kwargs):
        #     return reverse(url, kwargs=kwargs)
        # urls = [
        #     url('posts:index'),
        #     url('posts:group_list', slug=self.group.slug),
        #     url('posts:profile', username=self.user.username),
        #     url('posts:post_detail', post_id=self.post.id),
        #     url('posts:post_edit', post_id=self.post.id),
        #     url('posts:post_create'),
        # ]

        # templates = [
        #     'posts/index.html',
        #     'posts/group_list.html',
        #     'posts/profile.html',
        #     'posts/post_detail.html',
        #     'posts/post_create.html',
        #     'posts/post_create.html',
        # ]

        # for url, template in zip(urls, templates):
        #     with self.subTest(url=url):
        #         response = self.authorized_user.get(url)
        #         self.assertTemplateUsed(response, template)

    def test_index_page(self):
        """Проверка словаря контекст на список отображения постов"""
        response = self.authorized_user.get(reverse('posts:index'))
        zapisulku = list(Post.objects.all()[:10])
        first_post = response.context["page_obj"]
        self.assertEqual(list(response.context["page_obj"]), zapisulku)
        # Проверяем первый созданый пост
        self.assertEqual(first_post[0], self.post)

    def test_group_list(self):
        """Проверка словаря контекст на список отображения постов,"""
        """отсортированных по группе"""
        response = self.authorized_user.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        zapisulku = list(Post.objects.filter(group_id=self.group.id)[:10])
        first_post = response.context["page_obj"]
        self.assertEqual(list(response.context["page_obj"]), zapisulku)
        # Проверяем первый созданый пост
        self.assertEqual(first_post[0], self.post)

    def test_profile(self):
        """Проверка словаря контекст на список отображения постов,"""
        """отсортированных по пользователю"""
        response = self.authorized_user.get(reverse(
            'posts:profile', args=(self.user.username,))
        )
        zapisulku = list(Post.objects.filter(author=self.user)[:10])
        first_post = response.context["page_obj"]
        self.assertEqual(list(response.context["page_obj"]), zapisulku)
        # Проверяем первый созданый пост
        self.assertEqual(first_post[0], self.post)

    def test_post_detail(self):
        """Проверка контекста, отображение одного поста,"""
        """осортированного по id"""
        response = self.authorized_user.get(
            reverse('posts:post_detail', kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context["post"].text, self.post.text)
        self.assertEqual(response.context["post"].author, self.post.author)
        self.assertEqual(response.context["post"].group, self.post.group)

    def test_post_edit(self):
        """Проверяем форму редактирования/создания поста"""
        response = self.author_post.get(
            reverse('posts:post_edit', kwargs={"post_id": self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context["form"].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_comments(self):
        '''комментировать посты может только авторизованный пользователь'''
        '''после отправки комментарий появляется на странице поста.'''
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий'
        }
        response = self.authorized_user.post(
            reverse('posts:add_comment', kwargs={"post_id": self.post.id}),
            data=form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={"post_id": self.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(text='Комментарий').exists())

    def test_cache(self):
        response = self.guest_client.get(reverse('posts:index'))
        Post.objects.get(pk=self.post.id).delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response2.content)

    def test_page_not_found(self):
        response = self.guest_client.get('/xxxx/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_follow_page(self):
        # Проверка подписки на автора поста
        Follow.objects.get_or_create(user=self.auth_user,
                                     author=self.post.author)
        response = self.authorized_user.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertIn(self.post, response.context["page_obj"])

        # Проверка отписки от автора поста
        Follow.objects.all().delete()
        response = self.authorized_user.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 0)
