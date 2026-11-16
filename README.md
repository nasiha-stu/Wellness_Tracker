# Wellness Tracker

Wellness Tracker is a personal wellness and productivity web application built with Django. It allows users to track daily habits and activities, set personal goals, and monitor their progress through a personalized dashboard.

## Features

- **User Authentication:** Register, log in, and log out securely.
- **Personal Dashboard:** View daily and weekly wellness progress.
- **Hydration Tracking:** Record water, coffee, and tea consumption in milliliters or cups.
- **Sleep Tracking:** Record sleep and naps, including sleep quality, and view a rolling seven-day sleep average.
- **Fitness Tracking:** Record activities and durations, and track daily or weekly fitness goals.
- **Study Tracking:** Record study sessions and monitor daily or weekly study goals.
- **Daily Reflections:** Record how you feel and write personal reflections.
- **History Management:** View, edit, and delete previous entries.
- **Personalized Goals:** Set and update individual hydration, fitness, and study goals.
- **User Privacy:** Each user can access and manage only their own records.

## Technologies Used

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/nasiha-stu/Wellness_Tracker.git
cd Wellness_Tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

## Running Tests

To run the automated test suite:

```bash
python manage.py test
```

The project includes tests covering authentication, user permissions, tracking features, goal validation, and dashboard calculations.

## Project Purpose

Wellness Tracker was developed as my CS50W Web Programming with Python and JavaScript final project.

The goal was to build a simple, organized application that brings wellness tracking and personal productivity together in one place.d