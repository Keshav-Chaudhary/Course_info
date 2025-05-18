import json
import re
from collections import defaultdict
from flask import Flask, render_template, request

app = Flask(__name__)

with open('data/Directory_2ndyear.json', 'r') as f:
    COURSES = json.load(f)
with open('data/courses.json', 'r') as f:
    courses = json.load(f)
@app.route("/", methods=["GET", "POST"])
def index():
    selected_branch = None
    selected_semester = None
    grouped_courses = {}
    error_message = None

    if request.method == "POST":
        selected_branch = request.form.get("branch")
        selected_semester = request.form.get("semester")

        if not selected_branch or not selected_semester:
            error_message = "Please select both branch and semester to filter courses."
        else:
            filtered_courses = [c for c in COURSES if selected_branch in c.get('Programs', {})]

            filtered_courses = [
                c for c in filtered_courses
                if str(c.get("Semester", "")).strip() == selected_semester.strip()
            ]

            if not filtered_courses:
                error_message = "Under Development"

            temp_grouped = defaultdict(list)
            for course in filtered_courses:
                group_code = course['Programs'][selected_branch]
                temp_grouped[group_code].append(course)

            def sort_key(group):
                match = re.search(rf'{selected_branch}(\d+)', group)
                return int(match.group(1)) if match else 9999

            sorted_group_keys = sorted(temp_grouped.keys(), key=sort_key)
            grouped_courses = {k: temp_grouped[k] for k in sorted_group_keys}

    return render_template(
        "index.html",
        grouped_courses=grouped_courses,
        selected_branch=selected_branch,
        selected_semester=selected_semester,
        error_message=error_message
    )

@app.route("/tags")
def tags():
    selected_semester = request.args.get("semester")  # None or empty if not selected

    tag_to_courses = defaultdict(list)
    for course in COURSES:
        # If semester is selected, filter courses by semester
        if selected_semester:
            if str(course.get("Semester", "")).strip() != selected_semester.strip():
                continue
        
        # Collect tags from filtered courses
        for tag in course['Mandatory_Elective'].split(','):
            tag_clean = tag.strip()
            tag_to_courses[tag_clean].append(course['Course_Name'])

    # Sort tags alphabetically
    sorted_tags = dict(sorted(tag_to_courses.items(), key=lambda x: x[0].lower()))
    return render_template("tags.html", tag_to_courses=sorted_tags, selected_semester=selected_semester)

@app.route("/tag/<path:tag_name>")
def tag_filter(tag_name):
    filtered_courses = [
        c for c in COURSES
        if any(tag_name.lower() == tag.strip().lower() for tag in c['Mandatory_Elective'].split(','))
    ]
    return render_template("tag_courses.html", tag_name=tag_name, courses=filtered_courses)



@app.route('/course/<course_code>')
def course_detail(course_code):
    course = next((c for c in courses if c["Course_Code"] == course_code), None)
    if course:
        return render_template('course_detail.html', course=course)
    else:
        return "Course not found", 404


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
