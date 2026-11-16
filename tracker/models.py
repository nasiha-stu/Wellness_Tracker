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

    fitness_goal = models.PositiveIntegerField(
        default=30
)

    fitness_goal_type = models.CharField(
        max_length=10,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
    ],
    default="daily"
    )
    fitness_goal_unit = models.CharField(
    max_length=10,
    choices=[
        ("minutes", "Minutes"),
        ("hours", "Hours"),
    ],
    default="minutes"
)
    study_goal = models.FloatField(
    default=60
)

    study_goal_unit = models.CharField(
        max_length=10,
        choices=[
            ("minutes", "Minutes"),
            ("hours", "Hours"),
    ],
    default="minutes"
)

    study_goal_type = models.CharField(
        max_length=10,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
    ],
    default="daily"
)
    def __str__(self):
        return self.user.username

class Fitness(models.Model):


    ACTIVITY_CHOICES = [
        ("Walking", "🚶‍♀️ Walking"),
        ("Running", "🏃‍♀️ Running"),
        ("Cycling", "🚴‍♀️ Cycling"),
        ("Workout", "🏋️‍♀️ Workout"),
        ("Other", "✨ Other"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    activity = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES
    )

    duration = models.DecimalField(
    max_digits=5,
    decimal_places=1
)

    unit = models.CharField(
        max_length=10,
        choices=[
            ("minutes", "Minutes"),
            ("hours", "Hours"),
        ],
        default="minutes"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.activity} - {self.duration} {self.unit}"

class Study(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    subject = models.CharField(
        max_length=100
    )

    duration = models.FloatField()

    unit = models.CharField(
        max_length=10,
        choices=[
            ("minutes", "Minutes"),
            ("hours", "Hours"),
        ],
        default="minutes"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    def duration_display(self):

        total_minutes = 0

        if self.unit == "minutes":
            total_minutes = float(self.duration)

        elif self.unit == "hours":
            total_minutes = float(self.duration) * 60

        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)

        if hours and minutes:
            return f"{hours}h {minutes}m"

        elif hours:
            return f"{hours}h"

        else:
            return f"{minutes}m"

    def __str__(self):
        return f"{self.user.username} - {self.subject} - {self.duration} {self.unit}"

class Reflection(models.Model):

    FEELING_CHOICES = [
        ("great", "😊 Great"),
        ("good", "🙂 Good"),
        ("okay", "😐 Okay"),
        ("low", "😔 Low"),
        ("difficult", "😣 Difficult"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    feeling = models.CharField(
        max_length=20,
        choices=FEELING_CHOICES
    )

    text = models.TextField()

    date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.date}"