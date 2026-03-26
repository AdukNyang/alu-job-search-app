# Aduk's Job Finder

A web application that allows users to search for real job listings from platforms like LinkedIn, Indeed, and Glassdoor using the JSearch API. Users can filter by keyword, location, job type, and sort results by date or salary.

## Features

- Search jobs by keyword, location, and job type
- Sort results by date or salary
- Displays job title, company, location, salary, date posted, description, and apply link
- Error handling for API downtime and invalid responses
- Responsive UI

## APIs Used

- **JSearch API** via [RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) — provides job listings from LinkedIn, Indeed, Glassdoor, and more.

## How to Run Locally

### Prerequisites
- Python 3.x
- pip

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/AdukNyang/alu-job-search-app.git
   cd alu-job-search-app
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your API key:
   ```
   RAPIDAPI_KEY=your_api_key_here
   ```

4. Run the app:
   ```bash
   python3 app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000`

## Deployment

The application is deployed on two web servers with a load balancer distributing traffic between them.

### Servers
- **web-01**: `3.86.250.240`
- **web-02**: `54.152.16.128`
- **lb-01 (Load Balancer)**: `54.152.31.168`

### Steps Taken on Each Web Server (web-01 and web-02)

1. SSH into the server:
   ```bash
   ssh -i ~/.ssh/school ubuntu@<server-ip>
   ```

2. Install git and pip:
   ```bash
   sudo apt update && sudo apt install git python3-pip -y
   ```

3. Clone the repository:
   ```bash
   git clone https://github.com/AdukNyang/alu-job-search-app.git
   cd alu-job-search-app
   ```

4. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

5. Create the `.env` file:
   ```bash
   echo "RAPIDAPI_KEY=your_api_key_here" > .env
   ```

6. Configure Nginx as a reverse proxy:
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

7. Start Flask in the background:
   ```bash
   nohup python3 app.py &
   ```

### Load Balancer Configuration (lb-01)

HAProxy was configured to distribute traffic between web-01 and web-02 using round-robin:

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

Access the app via the load balancer at: `http://54.152.31.168`

## Challenges

- **pip not found on servers**: Had to install `python3-pip` manually before installing dependencies.
- **Flask only binding to localhost**: Nginx reverse proxy was needed to expose Flask to the outside world.
- **API returning unexpected results**: Some job postings have missing fields (location, date, salary) — handled with fallback values like `N/A` and `Not disclosed`.

## Credits

- [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) by letscrape on RapidAPI
- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [HAProxy](https://www.haproxy.org/) — Load balancer
- [Nginx](https://nginx.org/) — Reverse proxy
