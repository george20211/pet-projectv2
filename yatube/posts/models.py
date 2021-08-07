from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(max_length=100)
    pub_date = models.DateTimeField("date published",
                                    auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date', ]


class Group(models.Model):
    title = models.CharField(max_length=200, blank=True, null=False)
    slug = models.SlugField(verbose_name='slug',
                            blank=False, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(max_length=100)
    created = models.DateTimeField("date published",
                                   auto_now_add=True)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
