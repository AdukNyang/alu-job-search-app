from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "d0cf81360emshdce6def090048cdp1f086ejsn966b39af2e7a")
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()
    sort_by = request.args.get("sort_by", "date").strip()

    if not query:
        return jsonify({"error": "Please enter a job title or keyword."}), 400

    search_query = f"{query} in {location}" if location else query

    params = {
        "query": search_query,
        "num_pages": "1",
        "date_posted": "all"
    }

    if job_type:
        params["employment_types"] = job_type

    try:
        response = requests.get(JSEARCH_URL, headers=HEADERS, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        jobs = data.get("data", [])

        if sort_by == "salary":
            jobs.sort(key=lambda x: x.get("job_min_salary") or 0, reverse=True)
        else:
            jobs.sort(key=lambda x: x.get("job_posted_at_timestamp") or 0, reverse=True)

        results = []
        for job in jobs:
            results.append({
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": ", ".join(filter(None, [job.get("job_city"), job.get("job_country")])) or "N/A",
                "type": job.get("job_employment_type", "N/A"),
                "salary": f"${job['job_min_salary']:,.0f} - ${job['job_max_salary']:,.0f}" if job.get("job_min_salary") and job.get("job_max_salary") else "Not disclosed",
                "posted": job.get("job_posted_at_datetime_utc", "N/A")[:10] if job.get("job_posted_at_datetime_utc") else "N/A",
                "apply_link": job.get("job_apply_link", "#"),
                "description": (job.get("job_description") or "")[:300] + "..."
            })

        return jsonify({"jobs": results, "count": len(results)})

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Network error. Check your internet connection."}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"API error: {str(e)}"}), response.status_code
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
