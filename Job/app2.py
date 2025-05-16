from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Mock fallback jobs
MOCK_JOBS = [
    {
        "id": 1,
        "title": "Python Developer",
        "company": "TechCorp",
        "location": "Remote",
        "skills_required": ["Python", "Django", "REST"],
        "description": "Develop backend APIs using Django and REST framework."
    },
]

PROJECTS_AND_COURSES = {
    "Python": {
        "courses": [
            {"name": "Python for Everybody", "link": "https://www.coursera.org/specializations/python"},
            {"name": "Automate the Boring Stuff", "link": "https://automatetheboringstuff.com/"}
        ],
        "projects": [
            {"name": "Web Scraper", "link": "https://realpython.com/python-web-scraping-practical-introduction/"}
        ]
    },
    "React": {
        "courses": [
            {"name": "React - The Complete Guide", "link": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
        ],
        "projects": [
            {"name": "Build a Todo App", "link": "https://reactjs.org/tutorial/tutorial.html"}
        ]
    },
    "Django": {
        "courses": [
            {"name": "Django for Beginners", "link": "https://djangoforbeginners.com/"},
        ],
        "projects": [
            {"name": "Blog Project", "link": "https://learndjango.com/tutorials/getting-started-with-django"}
        ]
    }
}
RAPIDAPI_KEY = 'ef14936ad9msh183ca4a783b0601p11e8f4jsn9ed6e3eb866a'
RAPIDAPI_HOST = 'jsearch.p.rapidapi.com'
def fetch_real_jobs(query="developer", num_jobs=10):
    url = "https://jsearch.p.rapidapi.com/search"

    params = {
        "query": query,
        "num_pages": 1
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    KNOWN_SKILLS = ["python", "django", "react", "javascript", "java", "sql", "aws", "docker", "flask","C","c++", "html", "css", "typescript", "nodejs", "ruby", "swift", "kotlin", "go", "php"]

    jobs = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        for idx, item in enumerate(data.get("data", [])):
            full_desc = item.get("job_description", "").strip()

            # Try to split by sentence first
            sentences = full_desc.split('. ')
            short_desc = '. '.join(sentences[:2]).strip() + '.' if sentences else ''

            # Limit to 200 characters max, clean and add ellipsis
            if len(short_desc) > 200:
                short_desc = short_desc[:197].rstrip() + '...'

            skills_required = [skill.title() for skill in KNOWN_SKILLS if skill in full_desc.lower()]

            jobs.append({
                "id": idx,
                "title": item.get("job_title", "No Title"),
                "company": item.get("employer_name", "Unknown Company"),
                "location": item.get("job_city", "Unknown Location"),
                "skills_required": skills_required,
                "description": short_desc
            })

    except Exception as e:
        print(f"Error fetching jobs from RapidAPI: {e}")

    return jobs

              

   

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    interests = [i.lower() for i in data.get('interests', [])]
    user_skills = [s.lower() for s in data.get('skills', [])]

    jobs = fetch_real_jobs() or MOCK_JOBS
    matched_jobs = []

    for job in jobs:
        searchable = (job['title'] + job['company']).lower()  # description is removed
        if any(interest in searchable for interest in interests):
            matched_jobs.append(job)

    matched_jobs = matched_jobs or jobs

    # Extract skills from the 'skills_required' field, not description
    all_skills = set()
    for job in matched_jobs:
        for skill in job.get("skills_required", []):
            all_skills.add(skill.lower())

    skill_gaps = sorted(set(all_skills) - set(user_skills))

    suggestions = []
    for skill in skill_gaps:
        title = skill.title()
        if title in PROJECTS_AND_COURSES:
            suggestions.append({
                "skill": title,
                "courses": PROJECTS_AND_COURSES[title]["courses"],
                "projects": PROJECTS_AND_COURSES[title]["projects"]
            })
        else:
            suggestions.append({
                "skill": title,
                "courses": [{"name": f"Search {title} courses", "link": f"https://google.com/search?q={title}+courses"}],
                "projects": [{"name": f"Search {title} projects", "link": f"https://google.com/search?q={title}+projects"}]
            })

    return jsonify({
        "jobs": matched_jobs,
        "skill_gaps": skill_gaps,
        "suggestions": suggestions
    })



if __name__ == '__main__':
    app.run(debug=True)
