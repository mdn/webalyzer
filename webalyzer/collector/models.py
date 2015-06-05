from django.db import models
from django.dispatch import receiver


class Page(models.Model):
    domain = models.CharField(max_length=100, db_index=True)
    url = models.URLField()
    html = models.TextField()
    size = models.PositiveIntegerField(default=0)
    title = models.TextField(null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    source_hash = models.IntegerField(default=0, db_index=True)

    def __unicode__(self):
        return self.url

    def __repr__(self):
        return '<%s: %s %.2fKb>' % (
            self.__class__.__name__,
            self.url,
            len(self.html) / 1024.0
        )

    def __len__(self):
        return len(self.html)


class Stylesheet(models.Model):
    domain = models.CharField(max_length=100, db_index=True)
    url = models.URLField()
    css = models.TextField()
    size = models.PositiveIntegerField(default=0)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    source_hash = models.IntegerField(default=0, db_index=True)

    def __unicode__(self):
        return self.url

    def __repr__(self):
        return '<%s: %s %.2fKb>' % (
            self.__class__.__name__,
            self.url,
            len(self.css) / 1024.0
        )

    def __len__(self):
        return len(self.css)


@receiver(models.signals.pre_save, sender=Page)
@receiver(models.signals.pre_save, sender=Stylesheet)
def set_size(sender, instance, **kwargs):
    if not instance.size:
        instance.size = len(instance)
