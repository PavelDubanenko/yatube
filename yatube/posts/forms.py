from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from posts.models import Post, Comment

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': ('Имя'),
            'last_name': ('Фамилия'),
            'username': ('Никнэйм'),
            'email': ('Электронная почта')
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': ('Текст записи'),
            'group': ('Сообщество'),
            'image': ('Изображение'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
        labels = {'text': ('Текст комментария')}
