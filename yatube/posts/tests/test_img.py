from django.views.decorators import cache
from ..forms import PostForm
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from django.core.cache import cache
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class Cache_test_page(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='smallaer5saF.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.author = User.objects.create(username='ImageUser')
        cls.post = Post.objects.create(
            text='Testimage',
            author=cls.author,
            image=cls.uploaded,
            group=Group.objects.create(
                title='TestIMGgroup',
                slug='test-slug',)
        )
        cls.form = PostForm()
        cls.counters = Post.objects.exclude(
            image__isnull=True).exclude(image__exact='').count()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_image(self):
        cache.clear()

        form_data = {
            'text': 'Testimage',
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('index'),
            data=form_data,
            follow=True
        )

        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            response.context['page'][0].image.name,
            f'posts/{self.uploaded.name}'
        )

        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context['page'][0].image.name,
                         f'posts/{self.uploaded.name}')

        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': f'{self.author}'}))
        self.assertEqual(response.context['page'][0].image.name,
                         f'posts/{self.uploaded.name}')

        response = self.authorized_client.get(
            f'/{ self.author }/{ self.post.id }/'
        )
        self.assertEqual(response.context['post'].image.name,
                         f'posts/{self.uploaded.name}')

        self.assertEqual(self.counters, 1)

    def test_form_image(self):

        form_data = {
            'username': self.post.author.username,
            'image': self.uploaded,
            'text': 'ВРОДЕТЕКСТ',
        }

        self.authorized_client.post(reverse('new_post'), data=form_data)
        self.assertTrue(Post.image, form_data['image'])
        self.assertTrue(Post.text, form_data['text'])
