# Aduk's Job Finder

Live Demo: http://54.152.31.168

Demo Video: (link here)

A web app that lets you search for real jobs from LinkedIn, Indeed, Glassdoor and more. You can filter by keyword, location, and job type, sort by date or salary, and click straight through to apply. Built with Flask and the JSearch API for my Web Infrastructure summative at ALU.

## What It Does

Search jobs with:

- Filter by keyword, location, and job type
- Sort results by date or salary
- See job title, company, location, salary, date posted, and a short description
- Click "Apply Now" to go straight to the job listing
- Error handling — if the API is down or returns nothing, you get a clear message instead of a broken page
- Works on mobile and desktop

## How To Run It Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/AdukNyang/alu-job-search-app.git
   cd alu-job-search-app
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Create a `.env` file and add your API key:
   ```
   RAPIDAPI_KEY=your_api_key_here
   ```

4. Start the app:
   ```bash
   python3 app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser — that's it.

## What's In The Code

- `app.py`: Flask backend. Handles the `/search` route, calls the JSearch API, sorts results, and returns JSON.
- `templates/index.html`: The main page — search form and results grid.
- `static/style.css`: All the styling (blue theme, responsive card grid).
- `static/script.js`: Handles the search button, Enter key, fetches results, and renders job cards.
- `requirements.txt`: Flask, requests, python-dotenv.
- `.env`: Stores the API key — not in the repo.

## Deployment

I deployed the app on two web servers and set up a load balancer to split traffic between them.

### Servers
- **web-01**: `3.86.250.240`
- **web-02**: `54.152.16.128`
- **lb-01 (Load Balancer)**: `54.152.31.168`

### What I did on each web server

1. SSH in:
   ```bash
   ssh -i ~/.ssh/school ubuntu@<server-ip>
   ```

2. Install git and pip:
   ```bash
   sudo apt update && sudo apt install git python3-pip -y
   ```

3. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/AdukNyang/alu-job-search-app.git
   cd alu-job-search-app
   pip3 install -r requirements.txt
   ```

4. Add the `.env` file:
   ```bash
   echo "RAPIDAPI_KEY=your_api_key_here" > .env
   ```

5. Set up Nginx as a reverse proxy so Flask is accessible from outside:
   ```bash
   sudo tee /etc/nginx/sites-available/job-search << 'EOF'
   server {
       listen 80;
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   EOF
   sudo ln -s /etc/nginx/sites-available/job-search /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl restart nginx
   ```

6. Start Flask in the background:
   ```bash
   nohup python3 app.py &
   ```

### Load balancer setup (lb-01)

Used HAProxy with round-robin to split traffic evenly between the two servers:

```bash
sudo tee /etc/haproxy/haproxy.cfg << 'EOF'
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client 50000
    timeout server 50000

frontend web-frontend
    bind *:80
    default_backend web-backend

backend web-backend
    balance roundrobin
    server web-01 3.86.250.240:80 check
    server web-02 54.152.16.128:80 check
EOF
sudo systemctl restart haproxy
```

Access the app through the load balancer: `http://54.152.31.168`

## Challenges I Ran Into

- **pip wasn't installed on the servers** — had to install `python3-pip` before anything else would work.
- **Flask only ran on localhost** — it wasn't reachable from outside until I set up Nginx as a reverse proxy in front of it.
- **Some jobs have missing data** — the API sometimes returns listings without a location, date, or salary. Handled that with fallbacks (`N/A`, `Not disclosed`) so the app doesn't break.

## Why This Way?

- **Flask**: Lightweight and straightforward for a small API-driven app.
- **Nginx + HAProxy**: Nginx handles the reverse proxy on each server, HAProxy handles load balancing — same setup I've been learning in the Web Infrastructure track.
- **JSearch API**: Aggregates jobs from multiple platforms in one call, so users get broader results without needing multiple API integrations.

## Technologies

- Python 3 / Flask
- HTML5, CSS3, Vanilla JavaScript
- JSearch API (via RapidAPI)
- Nginx (reverse proxy)
- HAProxy (load balancer)

## Credits

- [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) by letscrape on RapidAPI
- [Flask](https://flask.palletsprojects.com/)
- [HAProxy](https://www.haproxy.org/)
- [Nginx](https://nginx.org/)

## Contact

Email: a.nyang@alustudent.com  
GitHub: AdukNyang

## License

Educational project for ALU coursework.
