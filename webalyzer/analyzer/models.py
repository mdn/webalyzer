from django.db import models


class Result(models.Model):
    domain = models.CharField(max_length=100, db_index=True)
    url = models.URLField()
    line = models.PositiveIntegerField(null=True)  # link's don't have this
    before = models.TextField()
    after = models.TextField()
    ignored = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)

    @property
    def suspects(self):
        return Suspect.objects.filter(result=self)


class Suspect(models.Model):
    result = models.ForeignKey(Result)
    selector = models.TextField()
    # useful when the selector appears in a bundle with other selectors
    selector_full = models.TextField()
    style = models.TextField()
    line = models.PositiveIntegerField(null=True)  # null if it goes wrong
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('modified',)

    @property
    def size(self):
        return len(self.style)
