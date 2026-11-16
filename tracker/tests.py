
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Hydration, Sleep, Fitness, Study, Reflection, Profile
from datetime import datetime, time, timedelta
from django.utils import timezone



class AuthenticationAndAccessTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!"
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_registration_successful(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            }
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

        self.assertIn("_auth_user_id", self.client.session)

    def test_registration_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "StrongPassword123!",
                "password2": "DifferentPassword123!",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Your passwords do not match. Please try again."
        )

        self.assertFalse(
            User.objects.filter(username="newuser").exists()
        )

    def test_login_successful(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "TestPassword123!",
            }
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.assertIn("_auth_user_id", self.client.session)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "WrongPassword123!",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Incorrect username or password. Please try again."
        )

    def test_logout_redirects_to_home(self):
        self.client.login(
            username="testuser",
            password="TestPassword123!"
        )

        response = self.client.get(reverse("logout"))

        self.assertRedirects(
            response,
            reverse("home")
        )

        self.assertNotIn("_auth_user_id", self.client.session)

    def test_private_pages_require_login(self):

        private_pages = [
            "dashboard",
            "profile",
            "hydration",
            "sleep",
            "fitness",
            "study",
            "reflection",
            "previous_reflections",
        ]

        for page in private_pages:

            with self.subTest(page=page):

                response = self.client.get(reverse(page))

                self.assertEqual(response.status_code, 302)


class HydrationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="hydrationuser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="TestPassword123!"
        )

        self.client.login(
            username="hydrationuser",
            password="TestPassword123!"
        )

    def test_create_hydration_entry(self):
        response = self.client.post(
            reverse("hydration"),
            {
                "drink_type": "Water",
                "amount": 500,
                "unit": "ml",
            }
        )

        self.assertRedirects(
            response,
            reverse("hydration")
        )

        self.assertEqual(
            Hydration.objects.filter(user=self.user).count(),
            1
        )

        entry = Hydration.objects.get(user=self.user)

        self.assertEqual(entry.drink_type, "Water")
        self.assertEqual(entry.amount, 500)
        self.assertEqual(entry.unit, "ml")

    def test_hydration_rejects_invalid_amounts(self):
        invalid_amounts = [
            (0, "ml"),
            (-100, "ml"),
            (3001, "ml"),
            (13, "cups"),
        ]

        for amount, unit in invalid_amounts:

            with self.subTest(amount=amount, unit=unit):

                response = self.client.post(
                    reverse("hydration"),
                    {
                        "drink_type": "Water",
                        "amount": amount,
                        "unit": unit,
                    }
                )

                self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Hydration.objects.filter(user=self.user).count(),
            0
        )

    def test_edit_hydration_entry(self):
        entry = Hydration.objects.create(
            user=self.user,
            drink_type="Water",
            amount=500,
            unit="ml",
        )

        response = self.client.post(
            reverse("edit_hydration", args=[entry.id]),
            {
                "drink_type": "Coffee",
                "amount": 250,
                "unit": "ml",
            }
        )

        self.assertRedirects(
            response,
            reverse("hydration")
        )

        entry.refresh_from_db()

        self.assertEqual(entry.drink_type, "Coffee")
        self.assertEqual(entry.amount, 250)

    def test_delete_hydration_entry(self):
        entry = Hydration.objects.create(
            user=self.user,
            drink_type="Water",
            amount=500,
            unit="ml",
        )

        response = self.client.post(
            reverse("delete_hydration", args=[entry.id])
        )

        self.assertRedirects(
            response,
            reverse("hydration")
        )

        self.assertFalse(
            Hydration.objects.filter(id=entry.id).exists()
        )

    def test_user_cannot_edit_another_users_hydration(self):
        entry = Hydration.objects.create(
            user=self.other_user,
            drink_type="Water",
            amount=500,
            unit="ml",
        )

        response = self.client.post(
            reverse("edit_hydration", args=[entry.id]),
            {
                "drink_type": "Coffee",
                "amount": 250,
                "unit": "ml",
            }
        )

        self.assertEqual(response.status_code, 404)

        entry.refresh_from_db()

        self.assertEqual(entry.drink_type, "Water")
        self.assertEqual(entry.amount, 500)

    def test_user_cannot_delete_another_users_hydration(self):
        entry = Hydration.objects.create(
            user=self.other_user,
            drink_type="Water",
            amount=500,
            unit="ml",
        )

        response = self.client.post(
            reverse("delete_hydration", args=[entry.id])
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Hydration.objects.filter(id=entry.id).exists()
        )


class SleepTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="sleepuser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="othersleepuser",
            password="TestPassword123!"
        )

        self.client.login(
            username="sleepuser",
            password="TestPassword123!"
        )

    def test_create_sleep_entry(self):
        response = self.client.post(
            reverse("sleep"),
            {
                "hours_slept": "8.0",
                "quality": "Good",
                "sleep_type": "Sleep",
            }
        )

        self.assertRedirects(
            response,
            reverse("sleep")
        )

        entry = Sleep.objects.get(user=self.user)

        self.assertEqual(entry.hours_slept, 8.0)
        self.assertEqual(entry.quality, "Good")
        self.assertEqual(entry.sleep_type, "Sleep")

    def test_sleep_rejects_invalid_hours(self):
        invalid_hours = [
            "0",
            "-2",
            "16.1",
        ]

        for hours in invalid_hours:

            with self.subTest(hours=hours):

                response = self.client.post(
                    reverse("sleep"),
                    {
                        "hours_slept": hours,
                        "quality": "Good",
                        "sleep_type": "Sleep",
                    }
                )

                self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Sleep.objects.filter(user=self.user).count(),
            0
        )

    def test_only_one_main_sleep_per_day(self):
        Sleep.objects.create(
            user=self.user,
            hours_slept=8,
            quality="Good",
            sleep_type="Sleep",
        )

        response = self.client.post(
            reverse("sleep"),
            {
                "hours_slept": "7.0",
                "quality": "Great",
                "sleep_type": "Sleep",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "You already logged your sleep for today."
        )

        self.assertEqual(
            Sleep.objects.filter(
                user=self.user,
                sleep_type="Sleep"
            ).count(),
            1
        )

    def test_multiple_naps_are_allowed(self):
        for hours in ["1.0", "1.5"]:

            response = self.client.post(
                reverse("sleep"),
                {
                    "hours_slept": hours,
                    "quality": "Good",
                    "sleep_type": "Nap",
                }
            )

            self.assertRedirects(
                response,
                reverse("sleep")
            )

        self.assertEqual(
            Sleep.objects.filter(
                user=self.user,
                sleep_type="Nap"
            ).count(),
            2
        )

    def test_edit_sleep_entry(self):
        entry = Sleep.objects.create(
            user=self.user,
            hours_slept=7,
            quality="Okay",
            sleep_type="Sleep",
        )

        response = self.client.post(
            reverse("edit_sleep", args=[entry.id]),
            {
                "hours_slept": "8.5",
                "quality": "Great",
                "sleep_type": "Sleep",
            }
        )

        self.assertRedirects(
            response,
            reverse("sleep")
        )

        entry.refresh_from_db()

        self.assertEqual(entry.hours_slept, 8.5)
        self.assertEqual(entry.quality, "Great")

    def test_delete_sleep_entry(self):
        entry = Sleep.objects.create(
            user=self.user,
            hours_slept=8,
            quality="Good",
            sleep_type="Sleep",
        )

        response = self.client.post(
            reverse("delete_sleep", args=[entry.id])
        )

        self.assertRedirects(
            response,
            reverse("sleep")
        )

        self.assertFalse(
            Sleep.objects.filter(id=entry.id).exists()
        )

    def test_user_cannot_edit_another_users_sleep(self):
        entry = Sleep.objects.create(
            user=self.other_user,
            hours_slept=8,
            quality="Good",
            sleep_type="Sleep",
        )

        response = self.client.post(
            reverse("edit_sleep", args=[entry.id]),
            {
                "hours_slept": "9.0",
                "quality": "Great",
                "sleep_type": "Sleep",
            }
        )

        self.assertEqual(response.status_code, 404)

        entry.refresh_from_db()

        self.assertEqual(entry.hours_slept, 8)

    def test_user_cannot_delete_another_users_sleep(self):
        entry = Sleep.objects.create(
            user=self.other_user,
            hours_slept=8,
            quality="Good",
            sleep_type="Sleep",
        )

        response = self.client.post(
            reverse("delete_sleep", args=[entry.id])
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Sleep.objects.filter(id=entry.id).exists()
        )


class FitnessTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="fitnessuser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="otherfitnessuser",
            password="TestPassword123!"
        )

        self.client.login(
            username="fitnessuser",
            password="TestPassword123!"
        )

    def test_create_fitness_entry(self):
        response = self.client.post(
            reverse("fitness"),
            {
                "activity": "Walking",
                "duration": "30",
                "unit": "minutes",
            }
        )

        self.assertRedirects(
            response,
            reverse("fitness")
        )

        entry = Fitness.objects.get(user=self.user)

        self.assertEqual(entry.activity, "Walking")
        self.assertEqual(entry.duration, 30)
        self.assertEqual(entry.unit, "minutes")

    def test_fitness_rejects_invalid_durations(self):
        invalid_entries = [
            ("0", "minutes"),
            ("-10", "minutes"),
            ("721", "minutes"),
            ("12.1", "hours"),
        ]

        for duration, unit in invalid_entries:

            with self.subTest(duration=duration, unit=unit):

                response = self.client.post(
                    reverse("fitness"),
                    {
                        "activity": "Running",
                        "duration": duration,
                        "unit": unit,
                    }
                )

                self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Fitness.objects.filter(user=self.user).count(),
            0
        )

    def test_fitness_rejects_blank_activity(self):
        response = self.client.post(
            reverse("fitness"),
            {
                "activity": "   ",
                "duration": "30",
                "unit": "minutes",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Fitness.objects.filter(user=self.user).count(),
            0
        )

    def test_fitness_accepts_valid_hours(self):
        response = self.client.post(
            reverse("fitness"),
            {
                "activity": "Cycling",
                "duration": "2",
                "unit": "hours",
            }
        )

        self.assertRedirects(
            response,
            reverse("fitness")
        )

        entry = Fitness.objects.get(user=self.user)

        self.assertEqual(entry.duration, 2)
        self.assertEqual(entry.unit, "hours")

    def test_edit_fitness_entry(self):
        entry = Fitness.objects.create(
            user=self.user,
            activity="Walking",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("edit_fitness", args=[entry.id]),
            {
                "activity": "Running",
                "duration": "45",
                "unit": "minutes",
            }
        )

        self.assertRedirects(
            response,
            reverse("fitness")
        )

        entry.refresh_from_db()

        self.assertEqual(entry.activity, "Running")
        self.assertEqual(entry.duration, 45)

    def test_delete_fitness_entry(self):
        entry = Fitness.objects.create(
            user=self.user,
            activity="Walking",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("delete_fitness", args=[entry.id])
        )

        self.assertRedirects(
            response,
            reverse("fitness")
        )

        self.assertFalse(
            Fitness.objects.filter(id=entry.id).exists()
        )

    def test_user_cannot_edit_another_users_fitness(self):
        entry = Fitness.objects.create(
            user=self.other_user,
            activity="Walking",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("edit_fitness", args=[entry.id]),
            {
                "activity": "Running",
                "duration": "45",
                "unit": "minutes",
            }
        )

        self.assertEqual(response.status_code, 404)

        entry.refresh_from_db()

        self.assertEqual(entry.activity, "Walking")
        self.assertEqual(entry.duration, 30)

    def test_user_cannot_delete_another_users_fitness(self):
        entry = Fitness.objects.create(
            user=self.other_user,
            activity="Walking",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("delete_fitness", args=[entry.id])
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Fitness.objects.filter(id=entry.id).exists()
        )


class StudyTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="studyuser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="otherstudyuser",
            password="TestPassword123!"
        )

        self.client.login(
            username="studyuser",
            password="TestPassword123!"
        )

    def test_create_study_entry(self):
        response = self.client.post(
            reverse("study"),
            {
                "subject": "Computer Science",
                "duration": "60",
                "unit": "minutes",
            }
        )

        self.assertRedirects(
            response,
            reverse("study")
        )

        entry = Study.objects.get(user=self.user)

        self.assertEqual(entry.subject, "Computer Science")
        self.assertEqual(entry.duration, 60)
        self.assertEqual(entry.unit, "minutes")

    def test_study_rejects_invalid_durations(self):
        invalid_entries = [
            ("0", "minutes"),
            ("-10", "minutes"),
            ("721", "minutes"),
            ("12.1", "hours"),
        ]

        for duration, unit in invalid_entries:

            with self.subTest(duration=duration, unit=unit):

                response = self.client.post(
                    reverse("study"),
                    {
                        "subject": "Mathematics",
                        "duration": duration,
                        "unit": unit,
                    }
                )

                self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Study.objects.filter(user=self.user).count(),
            0
        )

    def test_study_rejects_blank_subject(self):
        response = self.client.post(
            reverse("study"),
            {
                "subject": "   ",
                "duration": "60",
                "unit": "minutes",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Study.objects.filter(user=self.user).count(),
            0
        )

    def test_study_accepts_valid_hours(self):
        response = self.client.post(
            reverse("study"),
            {
                "subject": "Programming",
                "duration": "2",
                "unit": "hours",
            }
        )

        self.assertRedirects(
            response,
            reverse("study")
        )

        entry = Study.objects.get(user=self.user)

        self.assertEqual(entry.duration, 2)
        self.assertEqual(entry.unit, "hours")

    def test_study_duration_display(self):
        entry = Study.objects.create(
            user=self.user,
            subject="Programming",
            duration=90,
            unit="minutes",
        )

        self.assertEqual(
            entry.duration_display(),
            "1h 30m"
        )

    def test_edit_study_entry(self):
        entry = Study.objects.create(
            user=self.user,
            subject="Mathematics",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("edit_study", args=[entry.id]),
            {
                "subject": "Computer Science",
                "duration": "2",
                "unit": "hours",
            }
        )

        self.assertRedirects(
            response,
            reverse("study")
        )

        entry.refresh_from_db()

        self.assertEqual(entry.subject, "Computer Science")
        self.assertEqual(entry.duration, 2)
        self.assertEqual(entry.unit, "hours")

    def test_delete_study_entry(self):
        entry = Study.objects.create(
            user=self.user,
            subject="Mathematics",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("delete_study", args=[entry.id])
        )

        self.assertRedirects(
            response,
            reverse("study")
        )

        self.assertFalse(
            Study.objects.filter(id=entry.id).exists()
        )

    def test_user_cannot_edit_another_users_study(self):
        entry = Study.objects.create(
            user=self.other_user,
            subject="Mathematics",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("edit_study", args=[entry.id]),
            {
                "subject": "Programming",
                "duration": "60",
                "unit": "minutes",
            }
        )

        self.assertEqual(response.status_code, 404)

        entry.refresh_from_db()

        self.assertEqual(entry.subject, "Mathematics")
        self.assertEqual(entry.duration, 30)

    def test_user_cannot_delete_another_users_study(self):
        entry = Study.objects.create(
            user=self.other_user,
            subject="Mathematics",
            duration=30,
            unit="minutes",
        )

        response = self.client.post(
            reverse("delete_study", args=[entry.id])
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Study.objects.filter(id=entry.id).exists()
        )


class ReflectionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reflectionuser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="otherreflectionuser",
            password="TestPassword123!"
        )

        self.client.login(
            username="reflectionuser",
            password="TestPassword123!"
        )

    def test_create_reflection(self):
        response = self.client.post(
            reverse("reflection"),
            {
                "feeling": "great",
                "text": "Today was a productive and positive day.",
            }
        )

        self.assertRedirects(
            response,
            reverse("reflection")
        )

        entry = Reflection.objects.get(user=self.user)

        self.assertEqual(entry.feeling, "great")
        self.assertEqual(
            entry.text,
            "Today was a productive and positive day."
        )

    def test_reflection_rejects_blank_text(self):
        response = self.client.post(
            reverse("reflection"),
            {
                "feeling": "good",
                "text": "",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Reflection.objects.filter(user=self.user).count(),
            0
        )

    def test_reflection_rejects_invalid_feeling(self):
        response = self.client.post(
            reverse("reflection"),
            {
                "feeling": "unknown",
                "text": "Today was an interesting day.",
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Reflection.objects.filter(user=self.user).count(),
            0
        )

    def test_previous_reflections_only_show_current_users_entries(self):
        own_entry = Reflection.objects.create(
            user=self.user,
            feeling="good",
            text="My personal reflection.",
        )

        other_entry = Reflection.objects.create(
            user=self.other_user,
            feeling="low",
            text="Another user's private reflection.",
        )

        response = self.client.get(
            reverse("previous_reflections")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "My personal reflection."
        )

        self.assertNotContains(
            response,
            "Another user's private reflection."
        )

    def test_edit_reflection(self):
        entry = Reflection.objects.create(
            user=self.user,
            feeling="okay",
            text="An ordinary day.",
        )

        response = self.client.post(
            reverse("edit_reflection", args=[entry.id]),
            {
                "feeling": "great",
                "text": "Today turned out wonderfully!",
            }
        )

        self.assertRedirects(
            response,
            reverse("previous_reflections")
        )

        entry.refresh_from_db()

        self.assertEqual(entry.feeling, "great")
        self.assertEqual(
            entry.text,
            "Today turned out wonderfully!"
        )

    def test_delete_reflection(self):
        entry = Reflection.objects.create(
            user=self.user,
            feeling="good",
            text="A good day.",
        )

        response = self.client.post(
            reverse("delete_reflection", args=[entry.id])
        )

        self.assertRedirects(
            response,
            reverse("previous_reflections")
        )

        self.assertFalse(
            Reflection.objects.filter(id=entry.id).exists()
        )

    def test_user_cannot_edit_another_users_reflection(self):
        entry = Reflection.objects.create(
            user=self.other_user,
            feeling="low",
            text="This is private.",
        )

        response = self.client.post(
            reverse("edit_reflection", args=[entry.id]),
            {
                "feeling": "great",
                "text": "Trying to change someone else's entry.",
            }
        )

        self.assertEqual(response.status_code, 404)

        entry.refresh_from_db()

        self.assertEqual(entry.feeling, "low")
        self.assertEqual(entry.text, "This is private.")

    def test_user_cannot_delete_another_users_reflection(self):
        entry = Reflection.objects.create(
            user=self.other_user,
            feeling="low",
            text="This is private.",
        )

        response = self.client.post(
            reverse("delete_reflection", args=[entry.id])
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Reflection.objects.filter(id=entry.id).exists()
        )


class ProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="otherprofileuser",
            password="TestPassword123!"
        )

        self.profile = Profile.objects.get_or_create(
            user=self.user
        )[0]

        self.other_profile = Profile.objects.get_or_create(
            user=self.other_user
        )[0]

        self.client.login(
            username="profileuser",
            password="TestPassword123!"
        )

    def valid_profile_data(self):
        return {
            "water_goal": 2000,
            "fitness_goal": 30,
            "fitness_goal_unit": "minutes",
            "fitness_goal_type": "daily",
            "study_goal": 60,
            "study_goal_unit": "minutes",
            "study_goal_type": "daily",
        }

    def test_update_profile_goals(self):
        data = self.valid_profile_data()
        data.update({
            "water_goal": 2500,
            "fitness_goal": 45,
            "study_goal": 90,
        })

        response = self.client.post(
            reverse("profile"),
            data
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.water_goal, 2500)
        self.assertEqual(self.profile.fitness_goal, 45)
        self.assertEqual(self.profile.study_goal, 90)

    def test_profile_rejects_invalid_water_goals(self):
        for water_goal in [499, 3001]:

            with self.subTest(water_goal=water_goal):

                data = self.valid_profile_data()
                data["water_goal"] = water_goal

                response = self.client.post(
                    reverse("profile"),
                    data
                )

                self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.water_goal, 2000)

    def test_profile_rejects_zero_fitness_goal(self):
        data = self.valid_profile_data()
        data["fitness_goal"] = 0

        response = self.client.post(
            reverse("profile"),
            data
        )

        self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.fitness_goal, 30)

    def test_profile_rejects_zero_study_goal(self):
        data = self.valid_profile_data()
        data["study_goal"] = 0

        response = self.client.post(
            reverse("profile"),
            data
        )

        self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.study_goal, 60)

    def test_profile_rejects_excessive_fitness_goals(self):
        invalid_goals = [
            (13, "hours", "daily"),
            (41, "hours", "weekly"),
            (721, "minutes", "daily"),
            (2401, "minutes", "weekly"),
        ]

        for goal, unit, goal_type in invalid_goals:

            with self.subTest(
                goal=goal,
                unit=unit,
                goal_type=goal_type
            ):

                data = self.valid_profile_data()
                data.update({
                    "fitness_goal": goal,
                    "fitness_goal_unit": unit,
                    "fitness_goal_type": goal_type,
                })

                response = self.client.post(
                    reverse("profile"),
                    data
                )

                self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.fitness_goal, 30)

    def test_profile_accepts_maximum_valid_fitness_goals(self):
        valid_goals = [
            (12, "hours", "daily"),
            (40, "hours", "weekly"),
            (720, "minutes", "daily"),
            (2400, "minutes", "weekly"),
        ]

        for goal, unit, goal_type in valid_goals:

            with self.subTest(
                goal=goal,
                unit=unit,
                goal_type=goal_type
            ):

                data = self.valid_profile_data()
                data.update({
                    "fitness_goal": goal,
                    "fitness_goal_unit": unit,
                    "fitness_goal_type": goal_type,
                })

                response = self.client.post(
                    reverse("profile"),
                    data
                )

                self.assertRedirects(
                    response,
                    reverse("dashboard")
                )

    def test_users_have_separate_profiles(self):
        data = self.valid_profile_data()
        data["water_goal"] = 2500

        response = self.client.post(
            reverse("profile"),
            data
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.profile.refresh_from_db()
        self.other_profile.refresh_from_db()

        self.assertEqual(self.profile.water_goal, 2500)
        self.assertEqual(self.other_profile.water_goal, 2000)



class DashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboarduser",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="otherdashboarduser",
            password="TestPassword123!"
        )

        self.profile = Profile.objects.get_or_create(
            user=self.user
        )[0]

        Profile.objects.get_or_create(
            user=self.other_user
        )

        self.client.login(
            username="dashboarduser",
            password="TestPassword123!"
        )

        self.today = timezone.localdate()

    def make_date(self, days_ago=0, hour=12):
        day = self.today - timedelta(days=days_ago)

        return timezone.make_aware(
            datetime.combine(day, time(hour, 0))
        )

    def test_dashboard_water_calculation(self):
        water_ml = Hydration.objects.create(
            user=self.user,
            drink_type="Water",
            amount=500,
            unit="ml"
        )

        water_cups = Hydration.objects.create(
            user=self.user,
            drink_type="Water",
            amount=2,
            unit="cups"
        )

        Hydration.objects.create(
            user=self.user,
            drink_type="Coffee",
            amount=500,
            unit="ml"
        )

        yesterday_water = Hydration.objects.create(
            user=self.user,
            drink_type="Water",
            amount=1000,
            unit="ml"
        )

        Hydration.objects.filter(pk=water_ml.pk).update(
            date=self.make_date()
        )

        Hydration.objects.filter(pk=water_cups.pk).update(
            date=self.make_date()
        )

        Hydration.objects.filter(pk=yesterday_water.pk).update(
            date=self.make_date(days_ago=1)
        )

        # Another user's water must not count.
        Hydration.objects.create(
            user=self.other_user,
            drink_type="Water",
            amount=2000,
            unit="ml"
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_water"], 980)
        self.assertEqual(response.context["progress_percentage"], 49)

    def test_dashboard_water_progress_is_capped_at_100(self):
        entry = Hydration.objects.create(
            user=self.user,
            drink_type="Water",
            amount=3000,
            unit="ml"
        )

        Hydration.objects.filter(pk=entry.pk).update(
            date=self.make_date()
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["progress_percentage"], 100)
        self.assertEqual(
            response.context["progress_message"],
            "🎉 Goal complete!"
        )

    def test_dashboard_sleep_average(self):
        entries = [
            (8, "Sleep", 0),
            (1, "Nap", 0),
            (6, "Sleep", 1),
            (8, "Sleep", 5),
        ]

        for hours, sleep_type, days_ago in entries:
            entry = Sleep.objects.create(
                user=self.user,
                hours_slept=hours,
                sleep_type=sleep_type
            )

            Sleep.objects.filter(pk=entry.pk).update(
                date=self.make_date(days_ago)
            )

        # Another user's sleep must not affect the average.
        other_entry = Sleep.objects.create(
            user=self.other_user,
            hours_slept=10,
            sleep_type="Sleep"
        )

        Sleep.objects.filter(pk=other_entry.pk).update(
            date=self.make_date()
        )

        response = self.client.get(reverse("dashboard"))

        # Today: 8 + 1 = 9 hours
        # Yesterday: 6 hours
        # Five days ago: 8 hours
        # Average: 23 / 3 = 7.7
        self.assertEqual(response.context["average_sleep"], 7.7)

    def test_dashboard_shows_latest_main_sleep_today(self):
        first_sleep = Sleep.objects.create(
            user=self.user,
            hours_slept=7,
            sleep_type="Sleep"
        )

        latest_sleep = Sleep.objects.create(
            user=self.user,
            hours_slept=8,
            sleep_type="Sleep"
        )

        Sleep.objects.filter(pk=first_sleep.pk).update(
            date=self.make_date(hour=10)
        )

        Sleep.objects.filter(pk=latest_sleep.pk).update(
            date=self.make_date(hour=11)
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(
            response.context["last_night_sleep"].hours_slept,
            8
        )

    def test_dashboard_daily_fitness_calculation(self):
        self.profile.fitness_goal = 60
        self.profile.fitness_goal_unit = "minutes"
        self.profile.fitness_goal_type = "daily"
        self.profile.save()

        entries = [
            (30, "minutes", 0),
            (0.5, "hours", 0),
            (60, "minutes", 1),
        ]

        for duration, unit, days_ago in entries:
            entry = Fitness.objects.create(
                user=self.user,
                activity="Walking",
                duration=duration,
                unit=unit
            )

            Fitness.objects.filter(pk=entry.pk).update(
                date=self.make_date(days_ago)
            )

        # Another user's activity must not count.
        Fitness.objects.create(
            user=self.other_user,
            activity="Running",
            duration=120,
            unit="minutes"
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["total_fitness_minutes"], 60)
        self.assertEqual(response.context["fitness_goal_percentage"], 100)
        self.assertEqual(
            response.context["fitness_goal_message"],
            "🎉 Goal complete!"
        )

    def test_dashboard_weekly_fitness_calculation(self):
        self.profile.fitness_goal = 2
        self.profile.fitness_goal_unit = "hours"
        self.profile.fitness_goal_type = "weekly"
        self.profile.save()

        entries = [
            (30, "minutes", 0),
            (0.5, "hours", self.today.weekday()),
            (120, "minutes", self.today.weekday() + 1),]
        for duration, unit, days_ago in entries:
            entry = Fitness.objects.create(
                user=self.user,
                activity="Walking",
                duration=duration,
                unit=unit
            )

            Fitness.objects.filter(pk=entry.pk).update(
                date=self.make_date(days_ago)
            )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["total_fitness_minutes"], 60)
        self.assertEqual(response.context["fitness_goal_percentage"], 50)
        self.assertEqual(response.context["fitness_hours"], 1)
        self.assertEqual(response.context["fitness_minutes"], 0)

    def test_dashboard_daily_study_calculation(self):
        self.profile.study_goal = 60
        self.profile.study_goal_unit = "minutes"
        self.profile.study_goal_type = "daily"
        self.profile.save()

        entries = [
            (30, "minutes", 0),
            (0.5, "hours", 0),
            (60, "minutes", 1),
        ]

        for duration, unit, days_ago in entries:
            entry = Study.objects.create(
                user=self.user,
                subject="Programming",
                duration=duration,
                unit=unit
            )

            Study.objects.filter(pk=entry.pk).update(
                date=self.make_date(days_ago)
            )

        # Another user's study time must not count.
        Study.objects.create(
            user=self.other_user,
            subject="Math",
            duration=120,
            unit="minutes"
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["total_study_minutes"], 60)
        self.assertEqual(response.context["study_goal_percentage"], 100)
        self.assertEqual(
            response.context["study_goal_message"],
            "🎉 Goal complete!"
        )

    def test_dashboard_weekly_study_calculation(self):
        self.profile.study_goal = 2
        self.profile.study_goal_unit = "hours"
        self.profile.study_goal_type = "weekly"
        self.profile.save()

        entries = [
            (30, "minutes", 0),
            (0.5, "hours", self.today.weekday()),
            (120, "minutes", self.today.weekday() + 1),
        ]

        for duration, unit, days_ago in entries:
            entry = Study.objects.create(
                user=self.user,
                subject="Programming",
                duration=duration,
                unit=unit
            )

            Study.objects.filter(pk=entry.pk).update(
                date=self.make_date(days_ago)
            )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["total_study_minutes"], 60)
        self.assertEqual(response.context["study_goal_percentage"], 50)
        self.assertEqual(response.context["study_hours"], 1)
        self.assertEqual(response.context["study_minutes"], 0)
