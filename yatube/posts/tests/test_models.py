from django.test import TestCase
from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='TEST_USR')
        cls.Post = Post.objects.create(
            text="тестовыйпостна15символов",
            author=author,)
        cls.Group = Group.objects.create(
            title="test")

    def test_title_and_15_symbols(self):
        group = PostModelTest.Group
        post = PostModelTest.Post
        context = {
            "title": "test",
            "post": "тестовыйпостна1"
        }
        self.assertEqual(context['title'], group.title)
        self.assertEqual(context['post'], post.text[:15])
