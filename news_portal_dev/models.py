from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    _rating_user = models.IntegerField(default=0)

    def update_rating(self):
        post_ratings = self.post_set.aggregate(total=models.Sum('_rating'))['total'] or 0
        total_post_rating = post_ratings * 3
        author_comments_rating = self.user.comment_set.aggregate(total=models.Sum('_rating'))['total'] or 0
        post_comments_rating = Comment.objects.filter(post__author=self).aggregate(total=models.Sum('_rating'))[
                                   'total'] or 0
        self._rating_user = total_post_rating + author_comments_rating + post_comments_rating
        self.save()


    @property
    def rating_user(self):
        return self._rating_user

class Category(models.Model):
    category = models.CharField(max_length= 200, unique=True)

class Post(models.Model):
    ARTICLE = 'article'
    NEWS = 'news'

    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость')
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(choices=POST_TYPES, max_length=7)
    timestamp = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    _rating = models.IntegerField(default=0)

    @property
    def rating(self):
        return self._rating

    def like(self):
        self._rating += 1
        self.save()

    def dislike(self):
        self._rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...'

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

    def __str__(self):
        return self.title + '\n' + self.content[:124] + '...'



class PostCategory(models.Model):
    post  = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    _rating = models.IntegerField(default=0)

    @property
    def rating(self):
        return self._rating

    def like(self):
        self._rating += 1
        self.save()

    def dislike(self):
        self._rating -= 1
        self.save()

class Subscriber(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )