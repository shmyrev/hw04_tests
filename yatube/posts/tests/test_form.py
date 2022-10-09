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
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_create_post(self):
        """Создание нового поста"""
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
            response, reverse('posts:profile', kwargs={'username': 'auth'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, запись на совподение полей
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.group.id,
            ).exists()
        )
        # Проверяем, последняя ли зпись
        self.assertTrue(
            Post.objects.filter(pub_date__isnull=False,
                                text=form_data['text']).latest('pub_date')
        )

    def test_authorized_edit_post(self):
        """редактирование поста"""
        post = PostCreateFormTests.post
        form_data = {
            'text': 'Измененный текст формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.text, 'Измененный текст формы')
