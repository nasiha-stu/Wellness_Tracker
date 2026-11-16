from django import forms
from .models import Hydration, Profile, Sleep, Fitness, Study, Reflection



class HydrationForm(forms.ModelForm):

    class Meta:
        model = Hydration
        fields = [
            "drink_type",
            "amount",
            "unit",
        ]

    def clean(self):
        cleaned_data = super().clean()

        amount = cleaned_data.get("amount")
        unit = cleaned_data.get("unit")

        if amount is not None and unit:

            if amount <= 0:
                raise forms.ValidationError(
                    "Amount must be greater than zero."
                )

            if unit == "ml" and amount > 3000:
                raise forms.ValidationError(
                    "Please enter a realistic amount in milliliters."
                )

            if unit == "cups" and amount > 12:
                raise forms.ValidationError(
                    "Please enter a realistic amount in cups."
                )

        return cleaned_data
    
class SleepForm(forms.ModelForm):

    class Meta:
        model = Sleep
        fields = [
            "hours_slept",
            "quality",
            "sleep_type"
        ]


    def clean_hours_slept(self):

        hours = self.cleaned_data["hours_slept"]

        if hours <= 0:
            raise forms.ValidationError(
                "Sleep hours must be greater than zero."
            )

        if hours > 16:
            raise forms.ValidationError(
                "Please enter a realistic amount of sleep."
            )

        return hours


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "water_goal",
            "fitness_goal",
            "fitness_goal_unit",
            "fitness_goal_type",
            "study_goal",
            "study_goal_unit",
            "study_goal_type",
        ]

    def clean(self):

        cleaned_data = super().clean()

        goal = cleaned_data.get("fitness_goal")
        unit = cleaned_data.get("fitness_goal_unit")
        goal_type = cleaned_data.get("fitness_goal_type")
        study_goal = cleaned_data.get("study_goal")

        # Fitness goal must be greater than zero
        if goal is not None and goal <= 0:
            self.add_error(
                "fitness_goal",
                "Your fitness goal must be greater than zero."
            )

        # Study goal must be greater than zero
        if study_goal is not None and study_goal <= 0:
            self.add_error(
                "study_goal",
                "Your study goal must be greater than zero."
            )

        if goal is None or unit is None or goal_type is None:
            return cleaned_data

        # Fitness maximum limits
        if unit == "hours":

            if goal_type == "daily" and goal > 12:
                self.add_error(
                    "fitness_goal",
                    "Your daily fitness goal cannot be more than 12 hours."
                )

            elif goal_type == "weekly" and goal > 40:
                self.add_error(
                    "fitness_goal",
                    "Your weekly fitness goal cannot be more than 40 hours."
                )

        elif unit == "minutes":

            if goal_type == "daily" and goal > 720:
                self.add_error(
                    "fitness_goal",
                    "Your daily fitness goal cannot be more than 720 minutes."
                )

            elif goal_type == "weekly" and goal > 2400:
                self.add_error(
                    "fitness_goal",
                    "Your weekly fitness goal cannot be more than 2400 minutes."
                )

        return cleaned_data

    def clean_water_goal(self):

        goal = self.cleaned_data.get("water_goal")

        if goal is None:
            return goal

        if goal < 500:
            raise forms.ValidationError(
                "Your goal must be at least 500 ml."
            )

        if goal > 3000:
            raise forms.ValidationError(
                "Your goal cannot be more than 3000 ml."
            )

        return goal

class FitnessForm(forms.ModelForm):

    class Meta:
        model = Fitness
        fields = [
            "activity",
            "duration",
            "unit",
        ]

    def clean_activity(self):
        activity = self.cleaned_data["activity"].strip()

        if not activity:
            raise forms.ValidationError(
                "Please enter an activity."
            )

        return activity

    def clean(self):

        cleaned_data = super().clean()

        duration = cleaned_data.get("duration")
        unit = cleaned_data.get("unit")

        if duration is None or unit is None:
            return cleaned_data

        if duration <= 0:

            self.add_error(
                "duration",
                "Workout time must be at least 1 minute."
            )

        elif unit == "minutes" and duration > 720:

            self.add_error(
                "duration",
                "A workout session cannot be longer than 720 minutes (12 hours)."
            )

        elif unit == "hours" and duration > 12:

            self.add_error(
                "duration",
                "A workout session cannot be longer than 12 hours."
            )

        return cleaned_data
class StudyForm(forms.ModelForm):

    class Meta:
        model = Study
        fields = [
            "subject",
            "duration",
            "unit",
        ]

    def clean_subject(self):
        subject = self.cleaned_data["subject"].strip()

        if not subject:
            raise forms.ValidationError(
                "Please enter a subject."
            )

        return subject

    def clean(self):

        cleaned_data = super().clean()

        duration = cleaned_data.get("duration")
        unit = cleaned_data.get("unit")

        if duration is None or unit is None:
            return cleaned_data

        if duration <= 0:

            self.add_error(
                "duration",
                "Study time must be at least 1 minute."
            )

        elif unit == "minutes" and duration > 720:

            self.add_error(
                "duration",
                "A study session cannot be longer than 720 minutes (12 hours)."
            )

        elif unit == "hours" and duration > 12:

            self.add_error(
                "duration",
                "A study session cannot be longer than 12 hours."
            )

        return cleaned_data


class ReflectionForm(forms.ModelForm):

    class Meta:
        model = Reflection
        fields = [
            "feeling",
            "text",
        ]

        labels = {
            "feeling": "How are you feeling today?",
            "text": "What's on your mind?",
        }

        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Write whatever is on your mind..."
                }
            ),
        }