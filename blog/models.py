from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from mapservice.models import EatingPlace


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default = timezone.now)
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, blank=True, related_name='likers')
    # Eating Place
    place = models.ForeignKey(EatingPlace, related_name='posts', null = True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk}) ## Returns the url to the details page of the current post AS A STRING
                                                            ## Difference between redirect and reverse: rederict, redirects the user to an url, while reverse returns the url as a string

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete = models.CASCADE)
    image = models.ImageField(upload_to='post_images')

    def __str__(self):
        return f'{self.post} PostImage'

    def save(self):
        super().save()## Calling parent class' save method

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:## Resizes the post image if its too large
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
