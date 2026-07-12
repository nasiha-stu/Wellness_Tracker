from django.db import models


class Habit(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name