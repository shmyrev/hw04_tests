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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
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
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        author = User.objects.get(username='noname')
        group = Group.objects.get(title='Тестовая группа')
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'noname'})
        )
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertEqual(author.username, 'noname')
        self.assertEqual(group.title, 'Тестовая группа')

    # редактирование поста
    def test_authorized_edit_post(self):
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:index'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=self.group.id)
        self.client.get(f'posts/{self.post.id}/edit/')
        form_data = {
            'text': 'Текст из формы',
            'group': self.post.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id,
                    }),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post.text, 'Тестовый пост')
