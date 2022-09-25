from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticUrlTests(TestCase):
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
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        url_exists = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/auth/': 200,
            f'/posts/{ self.post.id }/': 200,
        }
        for url, status_code in url_exists.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_url_exists_at_desired_authorized(self):
        """Страница доступна авторизованному пользователю."""
        url_exists = {
            '/create/': 200,
            f'/posts/{ self.post.id }/edit/': 302,
        }
        for url, status_code in url_exists.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    # Шаблоны по адресам
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_url_name = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': f'/posts/{ self.post.id }/',
            'posts/create_post.html': '/create/',
        }
        for template, address in template_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем редиректы для неавторизованного пользователя
    # def test_url_redirect_anonymous_on_admin_login(self):
    #     """Страница перенаправит анонимного
    #           пользователя на страницу логина."""
    #     response = self.guest_client.get(
    #         f'/posts/{ self.post.id }/edit/', follow=True)
    #     self.assertRedirects(response, '/admin/login/?next=/post_detail/')
