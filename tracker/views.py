from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import HydrationForm, ProfileForm, SleepForm
from .models import Hydration, Sleep

def home(request):
    return render(request, "tracker/home.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")

    else:
        form = UserCreationForm()

    return render(request, "tracker/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

    return render(request, "tracker/login.html")


@login_required
def dashboard(request):

    today = timezone.localdate()

    
    water_entries = Hydration.objects.filter(
        user=request.user,
        drink_type="Water",
        date__date=today
    )

    total_water = 0

    for entry in water_entries:

        if entry.unit == "ml":
            total_water += entry.amount

        elif entry.unit == "cups":
            total_water += entry.amount * 240


    water_goal = request.user.profile.water_goal

    progress_percentage = int(
        (total_water / water_goal) * 100
    )


    if progress_percentage >= 100:
        progress_message = "🎉 Goal complete!"

    elif progress_percentage >= 90:
        progress_message = "🔥 Almost there!"

    elif progress_percentage >= 50:
        progress_message = "💪 You're doing great!"

    else:
        progress_message = "🌱 Keep going! Every sip counts."

        start_date = today - timedelta(days=6)
    end_date = today + timedelta(days=1)

    start_datetime = timezone.make_aware(
        datetime.combine(start_date, datetime.min.time())
    )

    end_datetime = timezone.make_aware(
        datetime.combine(end_date, datetime.min.time())
    )


    sleep_entries = Sleep.objects.filter(
        user=request.user,
        date__gte=start_datetime,
        date__lt=end_datetime
    ).order_by("-date")


    daily_sleep = {}

    for entry in sleep_entries:

        entry_day = timezone.localtime(entry.date).date()

        if entry_day not in daily_sleep:
            daily_sleep[entry_day] = 0

        daily_sleep[entry_day] += float(entry.hours_slept)


    if daily_sleep:

        average_sleep = round(
            sum(daily_sleep.values()) / len(daily_sleep),
            1
        )

    else:

        average_sleep = 0


    last_night_sleep = Sleep.objects.filter(
        user=request.user,
        date__date=today,
        sleep_type="Sleep"
    ).first()

    return render(request, "tracker/dashboard.html", {
        "total_water": total_water,
        "water_goal": water_goal,
        "progress_percentage": progress_percentage,
        "progress_message": progress_message,
        "sleep_entries": sleep_entries,
        "average_sleep": average_sleep,
        "last_night_sleep": last_night_sleep
    })


@login_required
def profile(request):

    profile = request.user.profile

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "tracker/profile.html",
        {"form": form}
    )

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def hydration(request):

    if request.method == "POST":
        form = HydrationForm(request.POST)

        if form.is_valid():
            hydration = form.save(commit=False)
            hydration.user = request.user
            hydration.save()

            return redirect("hydration")

    else:
        form = HydrationForm()


    entries = Hydration.objects.filter(
        user=request.user
    ).order_by("-date")


    return render(request, "tracker/hydration.html", {
        "form": form,
        "entries": entries
    })

@login_required
def delete_hydration(request, id):

    hydration = get_object_or_404(
        Hydration,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        hydration.delete()
        return redirect("hydration")

    return render(
        request,
        "tracker/delete_hydration.html",
        {"hydration": hydration}
    )

@login_required
def edit_hydration(request, id):

    hydration = get_object_or_404(
        Hydration,
        id=id,
        user=request.user
    )


    if request.method == "POST":

        form = HydrationForm(
            request.POST,
            instance=hydration
        )

        if form.is_valid():

            form.save()

            return redirect("hydration")


    else:

        form = HydrationForm(
            instance=hydration
        )


    return render(
        request,
        "tracker/edit_hydration.html",
        {
            "form": form
        }
    )

@login_required
def sleep(request):

    if request.method == "POST":

        form = SleepForm(request.POST)

        if form.is_valid():

            today = timezone.localdate()

            if form.cleaned_data["sleep_type"] == "Sleep":

                existing_sleep = Sleep.objects.filter(
                    user=request.user,
                    date__date=today,
                    sleep_type="Sleep"
                ).exists()

                if existing_sleep:

                    form.add_error(
                        None,
                        "You already logged your sleep for today."
                    )

                else:

                    sleep_entry = form.save(commit=False)
                    sleep_entry.user = request.user
                    sleep_entry.save()

                    return redirect("sleep")

            else:

                sleep_entry = form.save(commit=False)
                sleep_entry.user = request.user
                sleep_entry.save()

                return redirect("sleep")

    else:

        form = SleepForm()

    entries = Sleep.objects.filter(
        user=request.user
    ).order_by("-date")

    return render(request, "tracker/sleep.html", {
        "form": form,
        "entries": entries
    })


@login_required
def delete_sleep(request, id):

    sleep_entry = get_object_or_404(
        Sleep,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        sleep_entry.delete()
        return redirect("sleep")

    return render(
        request,
        "tracker/delete_sleep.html",
        {"sleep_entry": sleep_entry}
    )

@login_required
def edit_sleep(request, id):

    sleep_entry = get_object_or_404(
        Sleep,
        id=id,
        user=request.user
    )


    if request.method == "POST":

        form = SleepForm(
            request.POST,
            instance=sleep_entry
        )

        if form.is_valid():

            form.save()

            return redirect("sleep")


    else:

        form = SleepForm(
            instance=sleep_entry
        )


    return render(
        request,
        "tracker/edit_sleep.html",
        {
            "form": form
        }
    )