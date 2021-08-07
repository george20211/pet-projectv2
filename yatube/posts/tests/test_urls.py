from django.core.cache import cache
from django.test import TestCase, Client
from posts.models import Group, Post
from django.contrib.auth import get_user_model
User = get_user_model()


class UrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='AndreyG')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.author,
        )

        Group.objects.create(
            title='test title',
            slug='test-slug',
        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(
            User.objects.create_user(username='TEST_USR2'))

    def test_guest(self):

        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200, 'err1')

        response = self.guest_client.get("/group/test-slug/")
        self.assertEqual(response.status_code, 200, 'err2')

        response = self.guest_client.get("/new/")
        self.assertEqual(response.status_code, 302, 'err3')

        response = self.guest_client.get("/AndreyG/")
        self.assertEqual(response.status_code, 200, 'err4')

        response = self.guest_client.get(f'/{ self.author }/{ self.post.id }/')
        self.assertEqual(response.status_code, 200, 'err5')

        response = self.guest_client.get(
            f'/{ self.author }/{ self.post.id }/edit/')
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{ self.author }/{ self.post.id }/edit/'
        )

    def test_auth_usr(self):

        cache.clear()
        response = self.authorized_client.get("/")
        self.assertEqual(response.status_code, 200, 'err01')
        self.assertTemplateUsed(response, 'index.html', 'err02')

        response = self.authorized_client.get("/group/test-slug/")
        self.assertEqual(response.status_code, 200, 'err03')
        self.assertTemplateUsed(response, 'group.html', 'err04')

        response = self.authorized_client.get("/new/")
        self.assertEqual(response.status_code, 200, 'err05')
        self.assertTemplateUsed(response, 'new.html', 'err06')

        response = self.authorized_client.get(
            f'/{ self.author }/{ self.post.id }/edit/')
        self.assertEqual(response.status_code, 200, 'err07')

    def test_auth_non_author(self):

        response = self.another_authorized_client.get(
            f'/{ self.author.username }/{ self.post.id }/edit/')
        self.assertRedirects(
            response,
            f'/{ self.author.username }/{ self.post.id }/'
        )
