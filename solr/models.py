from django.db import models


class Update(models.Model):
    uid = models.CharField(max_length=20, blank=False, db_index=True,
                           unique=True)
    solr_dict = models.TextField()
    delete = models.BooleanField(default=False)