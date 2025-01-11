from django.db import models
import uuid

# Create your models here.

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank = True,null = True)
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
