from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "studentlifeos"


def init_db():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        category TEXT,
        status TEXT,
        task_date TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_tracker(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dsa INTEGER,
    sql_count INTEGER,
    java_count INTEGER,
    project_count INTEGER,
    study_date TEXT
    )
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS streaks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    streak_date TEXT UNIQUE
    )
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS placement_tracker(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    position TEXT,
    status TEXT,
    app_date TEXT,
    created_at TEXT
    )
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS habits(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_name TEXT,
    frequency TEXT,
    description TEXT,
    created_at TEXT
    )
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS fitness_tracker(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_type TEXT,
    duration INTEGER,
    calories INTEGER,
    intensity TEXT,
    notes TEXT,
    created_at TEXT
    )
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS mood_tracker(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mood TEXT,
    notes TEXT,
    sleep TEXT,
    diet TEXT,
    created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute( """  SELECT * FROM users WHERE email=?""",(email,))
        existing_user = cur.fetchone()

        if existing_user:
             conn.close()
             return render_template("signup.html")

        cur.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(?,?,?)
            """,
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            SELECT * FROM users
            WHERE email=? AND password=?
            """,
            (email, password)
        )

        user = cur.fetchone()

        print("EMAIL:", email)
        print("PASSWORD:", password)
        print("USER:", user)

        conn.close()

        if user:

            session["user_name"] = user[1]
            session["user_email"] = user[2]

            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user_name" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    today = str(date.today())

    if request.method == "POST":

        task_name = request.form["task_name"]
        category = request.form["category"]

        cur.execute(
            """
            INSERT INTO tasks(
                task_name,
                category,
                status,
                task_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                task_name,
                category,
                "Pending",
                today
            )
        )

        conn.commit()

    cur.execute(
        """
        SELECT * FROM tasks
        WHERE task_date=?
        """,
        (today,)
    )

    tasks = cur.fetchall()

    total_tasks = len(tasks)

    completed_tasks = 0

    for task in tasks:

        if task[3] == "Completed":

            completed_tasks += 1

    pending_tasks = total_tasks - completed_tasks

    if total_tasks == 0:

        completion_rate = 0

    else:

        completion_rate = (
            completed_tasks / total_tasks
        ) * 100
    

    cur.execute(
    """
    SELECT COUNT(*)
    FROM streaks
    """
    )

    streak_count = cur.fetchone()[0] 

    conn.close()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_rate=round(completion_rate, 2),
        current_date=today,
        user_name=session["user_name"],
        streak_count=streak_count
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/complete/<int:id>")
def complete(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET status='Completed'
        WHERE id=?
        """,
        (id,)
    )
    today = str(date.today())

    cur.execute("""INSERT OR IGNORE INTO streaks(streak_date)VALUES(?)""",(today,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/delete_task/<int:id>")
def delete_task(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM tasks
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/study", methods=["GET", "POST"])
def study():
    if "user_name" not in session:
        return redirect("/login")
    if request.method == "POST":

        dsa = request.form["dsa"]
        sql = request.form["sql"]
        java = request.form["java"]
        project = request.form["project"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO study_tracker(
                dsa,
                sql_count,
                java_count,
                project_count,
                study_date
            )
            VALUES(?,?,?,?,?)
            """,
            (
                dsa,
                sql,
                java,
                project,
                str(date.today())
            )
        )

        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM study_tracker")

    records = cur.fetchall()

    conn.close()

    return render_template(
        "study.html",
        records=records
    )

@app.route("/analytics")
def analytics():
    if "user_name" not in session:
        return redirect("/login")
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        SUM(dsa),
        SUM(sql_count),
        SUM(java_count),
        SUM(project_count)
        FROM study_tracker
        """
    )

    data = cur.fetchone()

    conn.close()

    total_dsa = data[0] or 0
    total_sql = data[1] or 0
    total_java = data[2] or 0
    total_projects = data[3] or 0

    grand_total = (
        total_dsa +
        total_sql +
        total_java +
        total_projects
    )

    if grand_total == 0:

        dsa_percent = 0
        sql_percent = 0
        java_percent = 0
        project_percent = 0

    else:

        dsa_percent = round(
            (total_dsa / grand_total) * 100, 2
        )

        sql_percent = round(
            (total_sql / grand_total) * 100, 2
        )

        java_percent = round(
            (total_java / grand_total) * 100, 2
        )

        project_percent = round(
            (total_projects / grand_total) * 100, 2
        )

    return render_template(
        "analytics.html",
        total_dsa=total_dsa,
        total_sql=total_sql,
        total_java=total_java,
        total_projects=total_projects,
        dsa_percent=dsa_percent,
        sql_percent=sql_percent,
        java_percent=java_percent,
        project_percent=project_percent
    )

@app.route("/placement", methods=["GET", "POST"])
def placement():
    if "user_name" not in session:
        return redirect("/login")

    if request.method == "POST":
        company = request.form["company"]
        position = request.form["position"]
        status = request.form["status"]
        app_date = request.form["app_date"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO placement_tracker(
                company,
                position,
                status,
                app_date,
                created_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                company,
                position,
                status,
                app_date,
                str(date.today())
            )
        )
        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM placement_tracker ORDER BY id DESC")
    placements = cur.fetchall()
    conn.close()

    return render_template(
        "placement.html",
        user_name=session["user_name"],
        placements=placements
    )

@app.route("/habit", methods=["GET", "POST"])
def habit():
    if "user_name" not in session:
        return redirect("/login")

    if request.method == "POST":
        habit_name = request.form["habit_name"]
        frequency = request.form["frequency"]
        description = request.form.get("description", "")

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO habits(
                habit_name,
                frequency,
                description,
                created_at
            )
            VALUES(?,?,?,?)
            """,
            (
                habit_name,
                frequency,
                description,
                str(date.today())
            )
        )
        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM habits ORDER BY id DESC")
    habits = cur.fetchall()
    conn.close()

    return render_template(
        "habit.html",
        user_name=session["user_name"],
        habits=habits
    )

@app.route("/fitness", methods=["GET", "POST"])
def fitness():
    if "user_name" not in session:
        return redirect("/login")

    if request.method == "POST":
        exercise_type = request.form["exercise_type"]
        duration = request.form["duration"]
        calories = request.form["calories"]
        intensity = request.form["intensity"]
        notes = request.form.get("notes", "")

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO fitness_tracker(
                exercise_type,
                duration,
                calories,
                intensity,
                notes,
                created_at
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                exercise_type,
                duration,
                calories,
                intensity,
                notes,
                str(date.today())
            )
        )
        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM fitness_tracker ORDER BY id DESC")
    workouts = cur.fetchall()
    conn.close()

    return render_template(
        "fitness.html",
        user_name=session["user_name"],
        workouts=workouts
    )

@app.route("/mood", methods=["GET", "POST"])
def mood():
    if "user_name" not in session:
        return redirect("/login")

    if request.method == "POST":
        mood_value = request.form["mood"]
        notes = request.form.get("notes", "")
        sleep = request.form["sleep"]
        diet = request.form["diet"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO mood_tracker(
                mood,
                notes,
                sleep,
                diet,
                created_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                mood_value,
                notes,
                sleep,
                diet,
                str(date.today())
            )
        )
        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM mood_tracker ORDER BY id DESC LIMIT 7")
    moods = cur.fetchall()
    conn.close()

    return render_template(
        "mood.html",
        user_name=session["user_name"],
        moods=moods
    )

@app.route("/dashboard_v2", methods=["GET", "POST"])
def dashboard_v2():

    if "user_name" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    today = str(date.today())

    if request.method == "POST":

        task_name = request.form["task_name"]
        category = request.form["category"]

        cur.execute(
            """
            INSERT INTO tasks(
                task_name,
                category,
                status,
                task_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                task_name,
                category,
                "Pending",
                today
            )
        )

        conn.commit()

    cur.execute(
        """
        SELECT * FROM tasks
        WHERE task_date=?
        """,
        (today,)
    )

    tasks = cur.fetchall()

    total_tasks = len(tasks)

    completed_tasks = 0

    for task in tasks:

        if task[3] == "Completed":

            completed_tasks += 1

    pending_tasks = total_tasks - completed_tasks

    if total_tasks == 0:

        completion_rate = 0

    else:

        completion_rate = (
            completed_tasks / total_tasks
        ) * 100

    cur.execute(
        """
        SELECT COUNT(*)
        FROM streaks
        """
    )

    streak_count = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard_v2.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_rate=round(completion_rate, 2),
        current_date=today,
        streak_count=streak_count,
        user_name=session["user_name"]
    )

@app.route("/study_v2", methods=["GET", "POST"])
def study_v2():

    if request.method == "POST":

        dsa = request.form["dsa"]
        sql = request.form["sql"]
        java = request.form["java"]
        project = request.form["project"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO study_tracker(
                dsa,
                sql_count,
                java_count,
                project_count,
                study_date
            )
            VALUES(?,?,?,?,?)
            """,
            (
                dsa,
                sql,
                java,
                project,
                str(date.today())
            )
        )

        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM study_tracker
        ORDER BY id DESC
        """
    )

    records = cur.fetchall()

    conn.close()

    return render_template(
        "study_v2.html",
        records=records
    )

@app.route("/placement_v2", methods=["GET", "POST"])
def placement_v2():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":

        company = request.form["company"]
        position = request.form["position"]
        status = request.form["status"]
        app_date = request.form["app_date"]

        cur.execute(
            """
            INSERT INTO placement_tracker(
                company,
                position,
                status,
                interview_date,
                created_date
            )
            VALUES(?,?,?,?,?)
            """,
            (
                company,
                position,
                status,
                app_date,
                str(date.today())
            )
        )

        conn.commit()

    cur.execute(
        """
        SELECT * FROM placement_tracker
        ORDER BY id DESC
        """
    )

    placements = cur.fetchall()

    conn.close()

    return render_template(
        "placement_v2.html",
        placements=placements
    )
@app.route("/habit_v2", methods=["GET", "POST"])
def habit_v2():

    if request.method == "POST":

        habit_name = request.form["habit_name"]
        frequency = request.form["frequency"]
        description = request.form.get("description", "")

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO habits(
                habit_name,
                frequency,
                description,
                created_at
            )
            VALUES(?,?,?,?)
            """,
            (
                habit_name,
                frequency,
                description,
                str(date.today())
            )
        )

        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM habits ORDER BY id DESC"
    )

    habits = cur.fetchall()

    conn.close()

    return render_template(
        "habit_v2.html",
        habits=habits
    )

@app.route("/fitness_v2", methods=["GET", "POST"])
def fitness_v2():

    if request.method == "POST":

        exercise_type = request.form["exercise_type"]
        duration = request.form["duration"]
        calories = request.form["calories"]
        intensity = request.form["intensity"]
        notes = request.form.get("notes", "")

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO fitness_tracker(
                exercise_type,
                duration,
                calories,
                intensity,
                notes,
                created_at
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                exercise_type,
                duration,
                calories,
                intensity,
                notes,
                str(date.today())
            )
        )

        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM fitness_tracker ORDER BY id DESC"
    )

    workouts = cur.fetchall()

    conn.close()

    return render_template(
        "fitness_v2.html",
        workouts=workouts
    )

@app.route("/mood_v2", methods=["GET", "POST"])
def mood_v2():

    if request.method == "POST":

        mood_value = request.form["mood"]
        notes = request.form.get("notes", "")
        sleep = request.form["sleep"]
        diet = request.form["diet"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO mood_tracker(
                mood,
                notes,
                sleep,
                diet,
                created_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                mood_value,
                notes,
                sleep,
                diet,
                str(date.today())
            )
        )

        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM mood_tracker ORDER BY id DESC LIMIT 7"
    )

    moods = cur.fetchall()

    conn.close()

    return render_template(
        "mood_v2.html",
        moods=moods
    )

@app.route("/analytics_v2")
def analytics_v2():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        SUM(dsa),
        SUM(sql_count),
        SUM(java_count),
        SUM(project_count)
        FROM study_tracker
        """
    )

    data = cur.fetchone()

    conn.close()

    total_dsa = data[0] or 0
    total_sql = data[1] or 0
    total_java = data[2] or 0
    total_projects = data[3] or 0

    grand_total = (
        total_dsa +
        total_sql +
        total_java +
        total_projects
    )

    if grand_total == 0:

        dsa_percent = 0
        sql_percent = 0
        java_percent = 0
        project_percent = 0

    else:

        dsa_percent = round(
            (total_dsa / grand_total) * 100, 2
        )

        sql_percent = round(
            (total_sql / grand_total) * 100, 2
        )

        java_percent = round(
            (total_java / grand_total) * 100, 2
        )

        project_percent = round(
            (total_projects / grand_total) * 100, 2
        )

    return render_template(
        "analytics_v2.html",
        total_dsa=total_dsa,
        total_sql=total_sql,
        total_java=total_java,
        total_projects=total_projects,
        dsa_percent=dsa_percent,
        sql_percent=sql_percent,
        java_percent=java_percent,
        project_percent=project_percent
    )
if __name__ == "__main__":
    app.run(debug=True)