from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.db.models.deletion import CASCADE
from taggit.managers import TaggableManager

# Create your models here.

class Ad(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(2, 'There Must be atleast 2 characters.')])
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    text = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    picture = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file.')
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Comment', related_name='comments_owned')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Fav', related_name='favorite_ads')
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    text = models.TextField(validators=[MinLengthValidator(3, "Comment must be longer than 3 characters")])
    ad = models.ForeignKey(Ad, on_delete=CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + '...'

class Fav(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ad', 'user')

    def __str__(self):
        return '%s likes %s' %(self.user.username, self.ad.title[:10])