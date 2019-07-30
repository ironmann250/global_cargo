from __future__ import unicode_literals
from django.db import models

# Create your models here.
class SEARCH(models.Model):
	code=models.TextField()
	data=models.TextField()

	def __str__(self):
		return self.code