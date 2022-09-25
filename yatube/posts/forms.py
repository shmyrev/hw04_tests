from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import Post


User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Текст', 'group': 'Группа'}
        help_texts = {'text': 'Новый текст', 'group': 'Выбрать группу'}
