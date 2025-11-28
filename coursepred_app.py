from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DB_PATH = "medical_allotment.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

@app.route("/", methods=["GET", "POST"])

def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT course FROM allotted_seats ORDER BY course")
    courses = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT allotted_quota FROM allotted_seats ORDER BY allotted_quota")
    quotas = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT allotted_category FROM allotted_seats ORDER BY allotted_category")
    categories = [r[0] for r in cur.fetchall()]    

    selected_course = None
    selected_quota = None
    selected_category = None
    last_rank = None
    my_rank = None
    eligible_courses = []

    if request.method == "POST":
        selected_course = request.form.get("course")
        selected_quota = request.form.get("quota")
        selected_category = request.form.get("category")
        my_rank_str = request.form.get("my_rank")
        
        #last rank for the specific course, category & quota

        if selected_course and selected_category and selected_quota:
            cur.execute("""
                        SELECT MAX(rank)
                        FROM allotted_seats
                        WHERE course = ? AND allotted_quota = ? AND allotted_category = ?;
                        """, (selected_course, selected_quota, selected_category))
            row = cur.fetchone()
            if row and row[0] is not None:
                last_rank = int(row[0])
        
        #all courses possible for the given rank, per category & quota
        if my_rank_str and selected_category and selected_quota:
            my_rank = int(my_rank_str)
            cur.execute("""
                        SELECT course, allotted_quota, allotted_category, MAX(rank) AS last_rank
                        FROM allotted_seats
                        WHERE allotted_category = ? AND allotted_quota = ?
                        GROUP BY course, allotted_category
                        HAVING last_rank >= ?
                        ORDER BY last_rank;
                        """, (selected_category,selected_quota, my_rank))
            eligible_courses = cur.fetchall()
    conn.close()
    return render_template("index.html",
                courses=courses,
                quotas=quotas,
                categories=categories,
                selected_course=selected_course,
                selected_quota=selected_quota,
                selected_category=selected_category,
                my_rank=my_rank,
                last_rank=last_rank,
                eligible_courses=eligible_courses)

if __name__=='__main__':
    app.run(debug=True)
