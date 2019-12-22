from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# This model represents a user-profile
class Profile(models.Model):
    # Fields:
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=150, default='') 

    # Relationships:
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Recursieve relationship inspired by ref: https://www.caktusgroup.com/blog/2009/08/14/creating-recursive-symmetrical-many-to-many-relationships-in-django/
    following = models.ManyToManyField('self', symmetrical = False, blank=True, related_name='followers') 


    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        # Resizing the profile image if its too large (300x300)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


