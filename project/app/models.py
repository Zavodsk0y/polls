from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Оповещать при новых комментариях?')
    avatar = models.ImageField(upload_to='media', blank=False, null=False)

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.username


class Poll(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    full_description = models.TextField()
    publish_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    photo = models.ImageField(upload_to='media')

    def __str__(self):
        return self.title


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=180)
    votes = models.IntegerField()

    def __str__(self):
        return self.choice_text


class Voter(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
