from django import forms
from .models import Hydration, Profile, Sleep 



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
        ]

    def clean_water_goal(self):
        goal = self.cleaned_data["water_goal"]

        if goal < 500:
            raise forms.ValidationError(
                "Your goal must be at least 500 ml."
            )

        if goal > 3000:
            raise forms.ValidationError(
                "Your goal cannot be more than 3000 ml."
            )

        return goal