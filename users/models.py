from django.db import models
from django.contrib.auth.models import User
from PIL import Image



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    following = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='followers') ## symmetrical = False makes it so that the follow relationship is unidirectional
    ##Reference https://www.caktusgroup.com/blog/2009/08/14/creating-recursive-symmetrical-many-to-many-relationships-in-django/
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)## Calling parent class' save method

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:## Resizes the profile image if its too large
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


