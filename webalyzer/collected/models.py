from django.db import models

from sorl.thumbnail import ImageField

from webalyzer.collector.models import Page


class Screenshot(models.Model):
    page = models.ForeignKey(Page)
    file = ImageField(upload_to='screenshots')
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    engine = models.CharField(max_length=100, default='slimerjs')
    added = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, page):
        for each in cls.objects.filter(page=page).order_by('-added'):
            return each
