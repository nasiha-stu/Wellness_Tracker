from django.db import models
from django.contrib.auth.models import User

class Habit(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Hydration(models.Model):

    DRINK_CHOICES = [
        ("Water", "💧 Water"),
        ("Coffee", "☕ Coffee"),
        ("Tea", "🍵 Tea"),
    ]

    UNIT_CHOICES = [
        ("ml", "ml"),
        ("cups", "cups"),
       
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    drink_type = models.CharField(
        max_length=20,
        choices=DRINK_CHOICES,
        default="Water"
    )

    amount = models.IntegerField()

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="ml"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.user.username} - {self.drink_type} - {self.amount}{self.unit}"
    
class Sleep(models.Model):

    QUALITY_CHOICES = [
        ("Poor", "😴 Poor"),
        ("Okay", "🙂 Okay"),
        ("Good", "😊 Good"),
        ("Great", "⭐ Great"),
    ]

    TYPE_CHOICES = [
        ("Sleep", "😴 Sleep"),
        ("Nap", "💤 Nap"),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    hours_slept = models.DecimalField(
        max_digits=4,
        decimal_places=1
    )

    quality = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default="Okay"
    )

    sleep_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default="Sleep"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.user.username} - {self.hours_slept} hours"

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    water_goal = models.PositiveIntegerField(
        default=2000
    )

    def __str__(self):
        return self.user.username