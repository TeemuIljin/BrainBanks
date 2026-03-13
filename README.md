## BrainBanks – Gamified STEM Learning Platform

BrainBanks is a web-based learning platform focused on **STEM subjects** with a strong emphasis on **practice, streaks, and gamification**.  
Learners progress through short courses and quizzes, earn points, build daily streaks, purchase power‑ups, and compete on a global leaderboard.

---

### What BrainBanks Actually Does

- **Courses**
  - Courses have a title, description, difficulty level (Beginner / Intermediate / Advanced), and HTML content.
  - Each course is paired with a quiz that reinforces the core concepts.

- **Quizzes & Practice**
  - Each course has a multiple‑choice quiz with questions and options, including which options are correct.
  - Correct answers award points and contribute to your progress in that course.
  - Quizzes are taken question by question, with results and points summarized at the end.

- **Points, Streaks & Progression**
  - Each user has a **Player Profile** that tracks:
    - Total points
    - Current streak and longest streak
    - Last activity date
  - Daily activity (finishing quizzes) maintains or grows your streak; missing days can reset it unless you use certain power‑ups.

- **Shop & Power‑Ups**
  - A built‑in **Shop** lets users spend earned points on special items:
    - **Streak freeze**: protects a streak if you miss a day.
    - **Fired up streak**: temporarily triples streak progression.
    - **Experience festival**: temporarily grants 3× points from correct answers.
  - Purchases are tracked in a **Purchase history** and can be activated later from the user’s profile.

- **Leaderboard**
  - A global **Leaderboard** ranks players based on their points.
  - Leaderboard data is cached for performance and periodically synced from player profiles.

- **Profiles & Settings**
  - Each user has:
    - A **Profile** (bio, picture, location, birth date).
    - A **Player Profile** (points, streaks, power‑ups).
    - **User settings** (theme: system / light / dark, email notifications, profile visibility).
  - Users can view their profile, inventory, and activate items from their account area.

- **REST API**
  - Core entities (profiles, courses, player profiles, shop items, purchases, quizzes, questions, options, completed quizzes, leaderboard entries) are exposed via a **Django REST Framework** API for future frontend or mobile clients.

---

### Main User Flows

- **Visitor / New User**
  - Browse the home page and a list of available courses.
  - Open course detail pages to see what is covered.
  - Create an account using the **Create profile** flow.

- **Returning Learner**
  - Sign in with username and password.
  - Browse or search courses, open a course, and start its quiz.
  - Answer multiple‑choice questions and see a summary screen with score and points gained.
  - Earn points, grow daily streaks, and unlock items in the shop.
  - Visit the **Shop**, purchase items with points, and later **use** those items from the profile page to protect streaks or boost points.
  - Check progress on the **Leaderboard** and manage theme / visibility / notifications from **Settings**.

- **Admin / Content Creator**
  - Use the standard Django **admin panel** to:
    - Create and manage courses, quizzes, questions, and options.
    - Manage shop items and user data as needed.

---

### Target Audience & Subjects

- **Target audience**
  - Secondary school and early university students.
  - Self‑learners and career switchers who prefer **short practice sessions** with game‑like progression.

- **Subjects (current & planned)**
  - Core **STEM** topics, such as:
    - Mathematics (algebra, calculus foundations, discrete math).
    - Programming fundamentals (Python basics, problem‑solving).
    - Science topics suitable for quiz‑based learning.
  - The content model is generic enough to later support humanities or language learning as well.

---

### Measurable Goals

- **Content goals**
  - Short‑term: at least **20** high‑quality STEM courses with quizzes.
  - Medium‑term: **50–100** courses across multiple difficulty levels.

- **User & engagement goals**
  - Support at least **2 user types**:
    - Casual learners (occasional use).
    - Power users (daily streak‑focused learners).
  - Encourage:
    - Average quiz completion rate of **≥ 70%** once a quiz is started.
    - At least **30%** of active users maintaining a streak of 7 days or more.

- **Performance & reliability**
  - Target **p95 page load** under **1.0 s** for main pages under normal load.
  - Handle at least **500–1,000** concurrent users on the hosted environment.
  - Aim for **≥ 99%** uptime on production hosting.

---

### Tech Stack & Architecture

- **Backend**
  - **Django 5** as the main web framework.
  - **Django REST Framework (DRF)** for JSON APIs (courses, profiles, shop, quizzes, leaderboard, etc.).

- **Database**
  - Local development: **SQLite** (simple file‑based DB).
  - Production: **PostgreSQL** (via `DATABASE_URL`, managed by the hosting provider).

- **Frontend**
  - Server‑rendered **Django templates** (HTML) with standard CSS/JS.
  - No separate React/SPA frontend yet, but the DRF API is ready for future React/mobile clients.

- **Infrastructure & Hosting**
  - Hosted on **Railway** (`RAILWAY_ENVIRONMENT`‑aware settings).
  - **Gunicorn** as the WSGI server.
  - **Whitenoise** for serving static files efficiently in production.
  - Environment variables managed via **python‑decouple**.
  - Database configuration via **dj‑database‑url**.

- **Caching & Logging**
  - Local development: in‑memory cache (`LocMemCache`).
  - Production: database‑backed cache (with the option to move to Redis later).
  - Structured logging to both console and log files, with a dedicated logger for the `courses` app.

---

### Running BrainBanks Locally (Summary)

1. **Create & activate a virtual environment** (Python 3.11+ recommended).
2. **Install dependencies**:
   - `pip install -r requirements.txt`
3. **Create a `.env` file** (or equivalent) with at least:
   - `SECRET_KEY=your_django_secret_key`
   - `DEBUG=True`
4. **Apply migrations**:
   - `python manage.py migrate`
5. **Create a superuser** to manage content:
   - `python manage.py createsuperuser`
6. **Run the development server**:
   - `python manage.py runserver`

You can then access:
- The main site at `http://localhost:8000/`
- The admin panel at `http://localhost:8000/admin/`

---

### Roadmap (High‑Level)

- Expand the course library across more STEM topics and levels.
- Add richer analytics for learners (per‑topic strengths/weaknesses).
- Introduce badges/achievements alongside streaks and points.
- Build a separate React or mobile client on top of the existing DRF API.
