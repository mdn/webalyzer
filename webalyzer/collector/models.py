from django.db import models


class Page(models.Model):
    domain = models.CharField(max_length=100, db_index=True)
    url = models.URLField()
    html = models.TextField()
    size = models.PositiveIntegerField(default=0)
    title = models.TextField(null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.url

    def __repr__(self):
        return '<%s: %s %.2fKb>' % (
            self.__class__.__name__,
            self.url,
            len(self.html) / 1024.0
        )
