from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # гость не может создавать пост
    def test_guest_create_post(self):
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:index'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Текст из формы').exists())

    # Создание нового поста
    def test_authorized_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'noname'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, запись на совподение полей
        self.assertTrue(
            Post.objects.filter(
                text='Текст из формы',
                author=self.user,
                group=self.group.id,
            ).exists()
        )
        # Проверяем, последняя ли зпись
        self.assertTrue(
            Post.objects.filter(
                text='Текст из формы',
                author=self.user,
                group=self.group.id,
            ).last()
        )

    # редактирование поста
    def test_authorized_edit_post(self):
        # до редактирования
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        # после редоктирования
        post_edit = Post.objects.get(id=self.group.id)
        form_data = {
            'text': 'Измененный текст формы',
            'group': post_edit.id,
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_edit.id}),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.group.id)
        self.assertEqual(response_edit.status_code, 200)
        # проверяем, внеслись ли изменения
        self.assertEqual(post_edit.text, 'Измененный текст формы')
