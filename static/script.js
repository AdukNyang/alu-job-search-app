const statusBar = document.getElementById("status-bar");
const resultsGrid = document.getElementById("results-grid");
const searchBtn = document.getElementById("search-btn");

function setStatus(message, type) {
    statusBar.textContent = message;
    statusBar.className = type;
}

function searchJobs() {
    const query = document.getElementById("query").value.trim();
    const location = document.getElementById("location").value.trim();
    const job_type = document.getElementById("job_type").value;
    const sort_by = document.getElementById("sort_by").value;

    if (!query) {
        setStatus("Please enter a job title or keyword.", "error");
        return;
    }

    setStatus("Searching for jobs...", "loading");
    resultsGrid.innerHTML = "";
    searchBtn.disabled = true;

    const params = new URLSearchParams({ query, location, job_type, sort_by });

    fetch(`/search?${params}`)
        .then(res => res.json())
        .then(data => {
            searchBtn.disabled = false;
            if (data.error) {
                setStatus(data.error, "error");
                return;
            }
            if (data.jobs.length === 0) {
                setStatus("No jobs found. Try different keywords or location.", "error");
                return;
            }
            setStatus(`Found ${data.count} job(s) matching your search.`, "success");
            renderJobs(data.jobs);
        })
        .catch(() => {
            searchBtn.disabled = false;
            setStatus("Network error. Please check your connection and try again.", "error");
        });
}

function sanitize(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function renderJobs(jobs) {
    resultsGrid.innerHTML = jobs.map(job => `
        <div class="job-card">
            <h3>${sanitize(job.title)}</h3>
            <div class="company">${sanitize(job.company)}</div>
            <div class="meta">
                <span>Location: ${sanitize(job.location)}</span>
                <span>Type: ${sanitize(job.type)}</span>
                <span>Posted: ${sanitize(job.posted)}</span>
            </div>
            <div class="salary">Salary: ${sanitize(job.salary)}</div>
            <div class="description">${sanitize(job.description)}</div>
            <a href="${sanitize(job.apply_link)}" target="_blank">Apply Now</a>
        </div>
    `).join("");
}

document.addEventListener("keydown", function(e) {
    if (e.key === "Enter") searchJobs();
});
