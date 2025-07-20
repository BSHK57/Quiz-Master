# Quiz Master

Quiz Master is a comprehensive, interactive quiz platform built with Django. It is designed to facilitate seamless interaction between students and educators, providing a robust system for creating, taking, and analyzing quizzes. The application supports distinct roles for Students, Educators, and Administrators, each with a dedicated dashboard and functionalities.

## Key Features

### For Students
- **Interactive Dashboard**: View available subjects and faculty.
- **Dynamic Quiz Taking**: Take quizzes by selecting a subject, difficulty, and number of questions.
- **Voice-Enabled Quizzing**: Navigate through questions and select answers using voice commands.
- **Performance Tracking**: Instantly view quiz results, including score, correct, and incorrect answers.
- **Quiz History**: Review past quiz attempts and scores in the "My Quizzes" section.
- **Achievements**: Track highest scores and latest attempts for each quiz.
- **Personalized Analytics**: A dedicated analytics dashboard to track average scores, progress over time, and subject-wise performance.
- **Leaderboard**: See how you rank against other students.

### For Educators
- **Quiz Management**: Create quizzes manually by adding questions and options, or upload them in bulk using an Excel file (`.xlsx`).
- **Edit Quizzes**: Easily modify existing quizzes, questions, and options.
- **Comprehensive Analytics**: Access a rich analytics dashboard with visualizations for:
    - Student Performance
    - Quiz Performance Over Time
    - Question Difficulty
    - Pass/Fail Ratios
    - Quiz Distribution by Subject
- **Student Monitoring**: View a "Students Board" to track the performance and attempts of all students on your quizzes.
- **Results Viewer**: Analyze detailed results for each quiz, including completion rates, average scores, and individual student attempts.

### For Admins
- **Admin Dashboard**: A simple dashboard to monitor the total number of registered users on the platform.

## Technical Stack

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite3 (default)
- **Deployment**: Gunicorn (configured via `Procfile` for Heroku-like services)
- **Libraries**:
    - `pandas`: For processing Excel file uploads.
    - `Chart.js`: For data visualization on analytics dashboards.
    - `dj-database-url`, `psycopg2-binary`: For potential PostgreSQL database integration.
    - `whitenoise`: For serving static files in production.

## Project Structure

The project is organized into modular Django applications, promoting separation of concerns and maintainability.

- **`Admin/`**: Handles user authentication (registration, login, logout), password reset, and the custom user model with roles (`Student`, `Educator`, `Admin`).
- **`Students/`**: Manages the student-facing features, including the student dashboard, quiz setup, question interface, and results pages.
- **`Educators/`**: Contains all logic for the educator role, such as quiz creation, analytics dashboards, and student performance tracking.
- **`Quizzes/`**: Defines the core data models for quizzes, questions, options, and student attempts. It also includes views for the student's analytics dashboard.
- **`templates/`**: Contains all HTML templates, organized by application, along with associated CSS and JavaScript files.

## Installation and Setup

To get a local copy up and running, follow these simple steps.

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/bshk57/quiz-master.git
    cd quiz-master
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```sh
    python manage.py migrate
    ```

5.  **Create a superuser to access the admin panel:**
    ```sh
    python manage.py createsuperuser
    ```
    Follow the prompts to create an administrator account.

6.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## Usage

1.  Navigate to the homepage and select **Register**.
2.  Create an account by choosing your role (Student or Educator). The form will dynamically show fields relevant to your selected role.
3.  Log in with your new credentials. You will be redirected to your respective dashboard.

-   **As an Educator**:
    -   Start by creating a new quiz from your dashboard. You can add questions manually or use the "Upload Questions" feature with an Excel file.
    -   View your created quizzes and their statistics on the dashboard or "My Quizzes" page.
    -   Explore the "Analytics" tab to visualize performance data.
    -   Check the "Students Board" to monitor student progress.

-   **As a Student**:
    -   On your dashboard, select a subject to see the available faculty and start a quiz.
    -   Set up your quiz by choosing the difficulty and number of questions.
    -   Answer questions on the quiz page. You can use voice commands like "next", "previous", "read", and "option [number]" for a hands-free experience.
    -   Submit the quiz to see your results immediately.
    -   Visit "My Performance", "My Quizzes", and "Achievements" to track your progress.
