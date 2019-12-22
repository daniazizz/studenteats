from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from mapservice.models import EatingPlace


class Post(models.Model):
    # Fields: 
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=500)
    date_posted = models.DateTimeField(default = timezone.now)
    rating = models.IntegerField(null=False, default=0)
    cost = models.IntegerField(null=False, default=0)

    # Relationships:
    place = models.ForeignKey(EatingPlace, related_name='posts', on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='likers')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    # Fields:
    content = models.TextField(max_length=250)
    date_posted = models.DateTimeField(default=timezone.now)

    # Relationships:
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='comments')

    def __str__(self):
        return f'{self.author.username} comment'

class PostImage(models.Model):
    # Fields:
    image = models.ImageField(upload_to='post_images')

    # Relationships:
    post = models.ForeignKey(Post, related_name='images', on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.post} PostImage'

    def save(self):
        super().save()
        img = Image.open(self.image.path)

        # Resizing the image if its too large (300x300)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
