from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post


User = get_user_model()


class PostModelTest(TestCase):

    def test_post_str(self):
        post = Post(text="Короткий пост")
        self.assertEqual(str(post), "Короткий пост")
        long_post = Post(text="str сокращает title до первых 15 строк")
        self.assertEqual(str(long_post), 'str сокращает t')

    def test_verbose_name(self):
        """Проверяем, что у моделей корректно работает verbose_name."""
        def hint(field):
            return Post._meta.get_field(field).verbose_name

        self.assertEqual(hint('text'), 'Текст поста')
        self.assertEqual(hint('group'), 'Группа')
        self.assertEqual(hint('pub_date'), 'Дата публикации')
        self.assertEqual(hint('author'), 'Автор')

    def test_help_text(self):
        """Проверяем, что у моделей корректно работает help_text."""
        def hint(field):
            return Post._meta.get_field(field).help_text
        self.assertEqual(hint('text'), 'Введите текст поста')
        self.assertEqual(
            hint('group'), 'Группа, к которой будет относиться пост'
        )
