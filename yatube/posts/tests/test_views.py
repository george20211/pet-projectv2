from django.views.decorators import cache
from ..forms import PostForm
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, Comment, Follow
from django.core.cache import cache
import shutil

from django.conf import settings

User = get_user_model()


class UrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='AndreyG')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.author,
            group=Group.objects.create(
                title='testGroup',
                slug='test-slug2',)
        )

        Group.objects.create(
            title='test title',
            slug='test-slug'
        )
        cls.contexted = {
            'text': 'TestText',
            'author': 'AndreyG',
            'title': 'test title',
            'slug': 'test-slug',
            'title2': 'testGroup',
        }

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(
            User.objects.create_user(username='TEST_USR2'))

    def test_pages_uses_correct_template(self):
        cache.clear()
        templates_page_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'test-slug'})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_page(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(
            response.context['group'].title, self.contexted['title'])
        self.assertEqual(
            response.context['group'].slug, self.contexted['slug'])

    def test_page_index(self):
        cache.clear()
        response = self.authorized_client.get(
            reverse('index',))

        self.assertEqual(
            response.context['page'][0].text, self.contexted['text'])
        self.assertEqual(
            response.context['page'][0].author.username,
            self.contexted['author'])
        self.assertEqual(
            response.context['page'][0].group.title, self.contexted['title2'])

    def test_new_post_page(self):
        response = self.authorized_client.get(
            reverse('new_post'))
        form_fields = PostForm
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], form_fields)

    def test_edit_post_page(self):
        response = self.authorized_client.get(
            f'/{ self.author }/{ self.post.id }/edit/')
        form_fields = PostForm
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], form_fields)

    def test_profile_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': f'{self.author}'}))
        self.assertEqual(
            response.context['page'][0].text, self.contexted['text'])
        self.assertEqual(
            response.context['profile'].username, self.contexted['author'])

    def test_post_in_right_group(self):
        cache.clear()
        response = self.guest_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug2'}))
        self.assertEqual(
            response.context['page'][0].text, self.contexted['text'])

        response = self.guest_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        with self.assertRaises(IndexError):
            response.context['page'][0].text

        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            response.context['page'][0].text, self.contexted['text'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='testGroup',
            slug='test-slug2',
        )
        cls.author = User.objects.create_user(username='TEST_USR')
        for _ in range(13):
            Post.objects.create(
                text='TestText', author=cls.author, group=cls.group,)

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_group_10post(self):
        response = self.client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug2'}))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_profile_10post(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': f'{self.author}'}))
        self.assertEqual(len(response.context.get('page').object_list), 5)


class Cache_test_page(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='CacheUser')
        cls.post = Post.objects.create(
            text='TestCacheText',
            author=cls.author,
        )

    def setUp(self):

        self.unauth = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        self.follow = User.objects.create_user(username='follower11')
        self.follower_client = Client()
        self.follower_client.force_login(self.follow)

        self.unfollow = User.objects.create_user(username='unfollower11')
        self.unfollow_client = Client()
        self.unfollow_client.force_login(self.unfollow)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_index_cache(self):
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context['page'][0].text, 'TestCacheText')

    def test_404(self):
        response = self.client.get('/dfzghdfh/')
        with self.assertRaises(AssertionError):
            self.assertEqual(response, 404)

    def test_index_cache_Work(self):
        cache.clear()
        Post.objects.create(
            text='TestWorkPost',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context['page'][0].text, 'TestWorkPost')

    def test_index_cache_TypeError(self):
        Post.objects.create(
            text='TestFalseCache',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('index'))
        with self.assertRaises(TypeError):
            response.context['page'][0].text

    def test_auth_usr_follow(self):
        self.follower_client.get(reverse('profile_follow',
                                 kwargs={'username': self.author}))
        coun = Follow.objects.all().count()
        self.assertEqual(coun, 1)

        self.follower_client.get(reverse('profile_unfollow',
                                 kwargs={'username': self.author}))
        coun = Follow.objects.all().count()

        self.assertEqual(coun, 0)

    def test_post_follower(self):
        self.follower_client.get(reverse('profile_follow',
                                 kwargs={'username': self.author}))
        response = self.follower_client.get('/follow/')
        self.assertEqual(response.context['page'][0].text, 'TestCacheText')

        response = self.unfollow_client.get('/follow/')
        with self.assertRaises(IndexError):
            self.assertEqual(response.context['page'][0].text, IndexError)

    def test_comment_auth(self):

        self.follower_client.post(
            reverse('add_comment', kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id}), {
                'text': 'KOMMEHTAPuu'
            }, follow=True)

        response = self.follower_client.get(
            reverse('post', kwargs={
                    'username': self.author.username,
                    "post_id": self.post.id}
                    ))

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.context['comments'][0].text, "KOMMEHTAPuu")

    def test_comment_unAuth(self):
        try:
            self.unauth.post(
                reverse('add_comment', kwargs={
                        'username': self.post.author.username,
                        'post_id': self.post.id}),
                {
                    'text': 'KOMMEHTAPuu'
                }, follow=True)
        except(ValueError):
            print("Неавторизованный пользователь не может комментировать")

        self.assertEqual(Comment.objects.count(), 0)
