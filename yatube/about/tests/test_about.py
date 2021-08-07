from django.test import Client, TestCase


class TaskCreateFormTests(TestCase):
    def setUp(self):

        self.guest_client = Client()

    def test_about(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/tech.html', 'err06')

        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/author.html', 'err06')
