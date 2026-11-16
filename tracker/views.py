from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import HydrationForm, ProfileForm, SleepForm, FitnessForm, StudyForm, ReflectionForm
from .models import Hydration, Sleep, Fitness, Study, Reflection

def home(request):
    return render(request, "tracker/home.html")



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")

        elif "password2" in form.errors:
            if "The two password fields didn’t match." in form.errors["password2"]:
                form.errors["password2"] = [
                    "Your passwords do not match. Please try again."
        ]

    else:
        form = UserCreationForm()

    return render(request, "tracker/register.html", {"form": form})


def user_login(request):
    error_message = None

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
        else:
            error_message = "Incorrect username or password. Please try again."

    return render(
        request,
        "tracker/login.html",
        {"error_message": error_message}
    )


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

    if water_goal > 0:
        progress_percentage = int(
            (total_water / water_goal) * 100
        )
    else:
        progress_percentage = 0

    if progress_percentage > 100:
        progress_percentage = 100


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
    ).order_by("-date").first()


    profile = request.user.profile

    fitness_goal = profile.fitness_goal
    fitness_goal_unit = profile.fitness_goal_unit
    fitness_goal_type = profile.fitness_goal_type

    if fitness_goal_unit == "hours":
        fitness_goal_minutes = fitness_goal * 60
    else:
        fitness_goal_minutes = fitness_goal

    if fitness_goal_type == "daily":

        fitness_entries = Fitness.objects.filter(
            user=request.user,
            date__date=today
        )

    else:

        week_start = today - timedelta(days=today.weekday())

        fitness_entries = Fitness.objects.filter(
            user=request.user,
            date__date__gte=week_start,
            date__date__lte=today
        )

    total_fitness_minutes = 0

    for entry in fitness_entries:

        if entry.unit == "minutes":
            total_fitness_minutes += float(entry.duration)

        elif entry.unit == "hours":
            total_fitness_minutes += float(entry.duration) * 60

    fitness_hours = int(total_fitness_minutes // 60)
    fitness_minutes = int(total_fitness_minutes % 60)

    fitness_goal_hours = int(fitness_goal_minutes // 60)
    fitness_goal_display_minutes = int(fitness_goal_minutes % 60)

    if fitness_goal_minutes > 0:
        fitness_goal_percentage = int(
        (total_fitness_minutes / fitness_goal_minutes) * 100
    )
    else:
        fitness_goal_percentage = 0

    if fitness_goal_percentage > 100:
        fitness_goal_percentage = 100

    if fitness_goal_minutes <= 0:
        fitness_goal_message = "Set a fitness goal to track your progress."

    elif total_fitness_minutes >= fitness_goal_minutes:
        fitness_goal_message = "🎉 Goal complete!"

    elif fitness_goal_percentage >= 75:
        fitness_goal_message = "🔥 Almost there!"

    elif fitness_goal_percentage >= 50:
        fitness_goal_message = "💪 You're doing great!"

    else:
        fitness_goal_message = "🌱 Keep moving!"



    study_goal = profile.study_goal
    study_goal_unit = profile.study_goal_unit
    study_goal_type = profile.study_goal_type


    if study_goal_unit == "hours":
        study_goal_total_minutes = study_goal * 60
    else:
        study_goal_total_minutes = study_goal


    if study_goal_type == "daily":

        study_entries = Study.objects.filter(
            user=request.user,
            date__date=today
        )

    else:

        week_start = today - timedelta(days=today.weekday())

        study_entries = Study.objects.filter(
            user=request.user,
            date__date__gte=week_start,
            date__date__lte=today
        )


    total_study_minutes = 0

    for entry in study_entries:

        if entry.unit == "minutes":
            total_study_minutes += float(entry.duration)

        elif entry.unit == "hours":
            total_study_minutes += float(entry.duration) * 60


    study_hours = int(total_study_minutes // 60)
    study_minutes = int(total_study_minutes % 60)


    study_goal_hours = int(study_goal_total_minutes // 60)
    study_goal_display_minutes = int(study_goal_total_minutes % 60)


    if study_goal_total_minutes > 0:
        study_goal_percentage = int(
            (total_study_minutes / study_goal_total_minutes) * 100
        )
    else:
        study_goal_percentage = 0


    if study_goal_percentage > 100:
        study_goal_percentage = 100


    if study_goal_total_minutes <= 0:

        study_goal_message = "Set a study goal to track your progress."

    elif total_study_minutes >= study_goal_total_minutes:

        study_goal_message = "🎉 Goal complete!"

    elif study_goal_percentage >= 75:

        study_goal_message = "🔥 Almost there!"

    elif study_goal_percentage >= 50:

        study_goal_message = "💪 You're doing great!"

    else:

        study_goal_message = "🌱 Keep studying!"



    return render(request, "tracker/dashboard.html", {
        "total_water": total_water,
        "water_goal": water_goal,
        "progress_percentage": progress_percentage,
        "progress_message": progress_message,
        "average_sleep": average_sleep,
        "last_night_sleep": last_night_sleep,
        "sleep_entries": sleep_entries,
        "total_fitness_minutes": total_fitness_minutes,
        "fitness_hours": fitness_hours,
        "fitness_minutes": fitness_minutes,
        "fitness_goal": fitness_goal,
        "fitness_goal_type": fitness_goal_type,
        "fitness_goal_percentage": fitness_goal_percentage,
        "fitness_goal_message": fitness_goal_message,
        "fitness_goal_hours": fitness_goal_hours,
        "fitness_goal_minutes": fitness_goal_display_minutes,
        "total_study_minutes": total_study_minutes,
        "study_hours": study_hours,
        "study_minutes": study_minutes,
        "study_goal": study_goal,
        "study_goal_type": study_goal_type,
        "study_goal_percentage": study_goal_percentage,
        "study_goal_message": study_goal_message,
        "study_goal_hours": study_goal_hours,
        "study_goal_minutes": study_goal_display_minutes,
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
def fitness(request):

    if request.method == "POST":

        form = FitnessForm(request.POST)

        if form.is_valid():

            fitness_entry = form.save(commit=False)
            fitness_entry.user = request.user
            fitness_entry.save()

            return redirect("fitness")

    else:

        form = FitnessForm()

    entries = Fitness.objects.filter(
        user=request.user
    ).order_by("-date")

    return render(request, "tracker/fitness.html", {
        "form": form,
        "entries": entries
    })

@login_required
def delete_fitness(request, id):

    fitness_entry = get_object_or_404(
        Fitness,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        fitness_entry.delete()
        return redirect("fitness")

    return render(
        request,
        "tracker/delete_fitness.html",
        {"fitness_entry": fitness_entry}
    )


@login_required
def edit_fitness(request, id):

    fitness_entry = get_object_or_404(
        Fitness,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        form = FitnessForm(
            request.POST,
            instance=fitness_entry
        )

        if form.is_valid():
            form.save()
            return redirect("fitness")

    else:

        form = FitnessForm(
            instance=fitness_entry
        )

    return render(
        request,
        "tracker/edit_fitness.html",
        {
            "form": form
        }
    )

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

@login_required
def study(request):

    study_entries = Study.objects.filter(
        user=request.user
    ).order_by("-date")

    if request.method == "POST":

        form = StudyForm(request.POST)

        if form.is_valid():

            study_entry = form.save(commit=False)
            study_entry.user = request.user
            study_entry.save()

            return redirect("study")

    else:

        form = StudyForm()

    return render(request, "tracker/study.html", {
        "form": form,
        "study_entries": study_entries
    })

@login_required
def edit_study(request, id):

    study_entry = get_object_or_404(
        Study,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        form = StudyForm(
            request.POST,
            instance=study_entry
        )

        if form.is_valid():

            form.save()

            return redirect("study")

    else:

        form = StudyForm(
            instance=study_entry
        )

    return render(request, "tracker/edit_study.html", {
        "form": form,
        "study_entry": study_entry
    })

@login_required
def delete_study(request, id):

    study_entry = get_object_or_404(
        Study,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        study_entry.delete()

        return redirect("study")

    return render(request, "tracker/delete_study.html", {
        "study_entry": study_entry
    })

@login_required
def reflection(request):

    today = timezone.localdate()

    if request.method == "POST":

        form = ReflectionForm(request.POST)

        if form.is_valid():

            reflection_entry = form.save(commit=False)
            reflection_entry.user = request.user
            reflection_entry.save()

            return redirect("reflection")

    else:

        form = ReflectionForm()

    quotes = [
        "Small steps every day add up to big changes.",
        "Progress, not perfection.",
        "Take a breath. You are allowed to slow down.",
        "You are doing better than you think.",
        "Give yourself credit for how far you've come.",
        "Make time for the things that make you happy.",
        "Rest is part of the journey too.",
    ]

    today_quote = quotes[today.weekday()]

    return render(request, "tracker/reflection.html", {
        "form": form,
        "today_quote": today_quote,
    })

@login_required
def previous_reflections(request):

    reflections = Reflection.objects.filter(
        user=request.user
    ).order_by("-date")

    return render(request, "tracker/previous_reflections.html", {
        "reflections": reflections
    })
@login_required
def edit_reflection(request, reflection_id):

    reflection_entry = get_object_or_404(
        Reflection,
        id=reflection_id,
        user=request.user
    )

    if request.method == "POST":

        form = ReflectionForm(
            request.POST,
            instance=reflection_entry
        )

        if form.is_valid():

            form.save()

            return redirect("previous_reflections")

    else:

        form = ReflectionForm(
            instance=reflection_entry
        )

    return render(request, "tracker/edit_reflection.html", {
        "form": form,
        "reflection": reflection_entry
    })


@login_required
def delete_reflection(request, reflection_id):

    reflection_entry = get_object_or_404(
        Reflection,
        id=reflection_id,
        user=request.user
    )

    if request.method == "POST":

        reflection_entry.delete()

        return redirect("previous_reflections")

    return render(request, "tracker/delete_reflection.html", {
        "reflection": reflection_entry
    })