# VidyaMitra Backend Deployment Guide

## Local Development Setup

### 1. Prerequisites
- Python 3.10 or higher
- pip package manager
- Virtual environment tool

### 2. Installation Steps

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file in backend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
SECRET_KEY=your-secret-key-generate-random-string
OPENAI_API_KEY=sk-...

# Optional but recommended
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional external APIs
YOUTUBE_API_KEY=your-youtube-api-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-custom-search-engine-id
PEXELS_API_KEY=your-pexels-api-key
```

### 4. Run Development Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## API Key Setup

### OpenAI API Key (Required)
1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to API Keys section
4. Create new secret key
5. Copy and add to `.env` as `OPENAI_API_KEY`

### Supabase (Recommended)
1. Go to https://supabase.com
2. Create new project
3. Get URL and anon key from Settings > API
4. Add to `.env`

### YouTube API (Optional)
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to `.env` as `YOUTUBE_API_KEY`

### Google Custom Search (Optional)
1. Go to https://console.cloud.google.com
2. Enable Custom Search API
3. Create API key
4. Create Custom Search Engine at https://cse.google.com
5. Add both to `.env`

### Pexels API (Optional)
1. Go to https://www.pexels.com/api
2. Sign up and get API key
3. Add to `.env` as `PEXELS_API_KEY`

---

## Production Deployment

### Option 1: Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add environment variables in Railway dashboard

4. Deploy:
```bash
railway up
```

### Option 2: Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: vidyamitra-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
```

2. Connect GitHub repo to Render
3. Add environment variables in dashboard
4. Deploy

### Option 3: AWS EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3.10 python3-pip nginx
```

4. Clone repository and setup:
```bash
git clone <your-repo>
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Create systemd service:
```bash
sudo nano /etc/systemd/system/vidyamitra.service
```

```ini
[Unit]
Description=VidyaMitra API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/backend
Environment="PATH=/home/ubuntu/backend/venv/bin"
EnvironmentFile=/home/ubuntu/backend/.env
ExecStart=/home/ubuntu/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

6. Start service:
```bash
sudo systemctl start vidyamitra
sudo systemctl enable vidyamitra
```

7. Configure Nginx as reverse proxy

---

## Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t vidyamitra-api .
docker run -p 8000:8000 --env-file .env vidyamitra-api
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| SECRET_KEY | Yes | JWT secret key (generate random string) |
| OPENAI_API_KEY | Yes | OpenAI API key for GPT-4 |
| SUPABASE_URL | Recommended | Supabase project URL |
| SUPABASE_KEY | Recommended | Supabase anon key |
| YOUTUBE_API_KEY | Optional | YouTube Data API key |
| GOOGLE_API_KEY | Optional | Google API key |
| GOOGLE_CSE_ID | Optional | Custom Search Engine ID |
| PEXELS_API_KEY | Optional | Pexels API key |

---

## Monitoring and Logging

### View Logs
```bash
# Development
# Logs appear in terminal

# Production (systemd)
sudo journalctl -u vidyamitra -f

# Docker
docker logs -f <container-id>
```

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "openai": true,
    "supabase": true,
    "youtube": false,
    "google": false
  }
}
```

---

## Troubleshooting

### Import Errors
```bash
# Ensure you're in virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### OpenAI API Errors
- Check API key is valid
- Verify you have credits
- Check rate limits

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Module Not Found
```bash
# Ensure correct Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

---

## Security Best Practices

1. Never commit `.env` file
2. Use strong SECRET_KEY (32+ random characters)
3. Enable HTTPS in production
4. Implement rate limiting
5. Validate all inputs
6. Keep dependencies updated
7. Use environment-specific configs
8. Monitor API usage and costs

---

## Performance Optimization

1. Enable response caching for repeated queries
2. Use connection pooling for database
3. Implement request queuing for AI calls
4. Add CDN for static assets
5. Use async operations where possible
6. Monitor OpenAI token usage

---

## Cost Management

### OpenAI Costs
- GPT-4: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- Estimate: ~$0.10-0.50 per resume analysis
- Set usage limits in OpenAI dashboard

### Recommendations
- Cache AI responses when possible
- Use GPT-3.5-turbo for less critical tasks
- Implement user quotas
- Monitor daily spending
