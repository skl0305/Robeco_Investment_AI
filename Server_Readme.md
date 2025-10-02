# Robeco Investment AI Server Management

## Quick Commands Reference

### 🚀 Start Server (Background Mode)
```bash
cd ~/Robeco_Investment_AI
source venv/bin/activate
cd src/robeco/backend
nohup ../../../venv/bin/python professional_streaming_server.py > ../../../robeco_server.log 2>&1 &
```

### 📊 Check Server Status
```bash
ps aux | grep professional_streaming_server | grep -v grep
```

### 📝 Monitor Real-time Logs
```bash
cd ~/Robeco_Investment_AI && tail -f robeco_server.log
```

### 🛑 Stop Server
```bash
pkill -f "professional_streaming_server.py"
```

### 🔄 Update Code from GitHub
```bash
cd ~/Robeco_Investment_AI
git stash
git pull origin main
```

### 🔍 Check Consistency with GitHub
```bash
cd ~/Robeco_Investment_AI
git status
git diff HEAD origin/main
git log --oneline -5
git log origin/main --oneline -5
```

### 🔒 Force Sync with GitHub (100% Identical)
```bash
cd ~/Robeco_Investment_AI
git fetch origin
git reset --hard origin/main
git clean -fd
```

### ✅ Verify Complete Consistency
```bash
cd ~/Robeco_Investment_AI
git status
echo "Local HEAD:" && git rev-parse HEAD
echo "Remote HEAD:" && git rev-parse origin/main
git diff --stat HEAD origin/main
```

### 📤 Commit & Push Changes to GitHub
```bash
cd ~/Robeco_Investment_AI
git add .
git status
git commit -m "Update server configuration

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

### 🔍 Check Commit Status
```bash
cd ~/Robeco_Investment_AI
git status
git log --oneline -3
```

### 🔄 Full Restart (Safe Update + Restart)
```bash
cd ~/Robeco_Investment_AI
pkill -f "professional_streaming_server.py"
git stash
git pull origin main
source venv/bin/activate
cd src/robeco/backend
nohup ../../../venv/bin/python professional_streaming_server.py > ../../../robeco_server.log 2>&1 &
ps aux | grep professional_streaming_server | grep -v grep
```

### 🚨 Nuclear Restart (Force Identical + Restart)
```bash
cd ~/Robeco_Investment_AI
pkill -f "professional_streaming_server.py"
git fetch origin
git reset --hard origin/main
git clean -fd
source venv/bin/activate
cd src/robeco/backend
nohup ../../../venv/bin/python professional_streaming_server.py > ../../../robeco_server.log 2>&1 &
ps aux | grep professional_streaming_server | grep -v grep
```

### 🌍 Server URLs
- **Main App**: http://47.236.59.51:8005/
- **Workbench**: http://47.236.59.51:8005/workbench
- **Health Check**: http://47.236.59.51:8005/health

### 🔧 Troubleshooting

**If server won't start (missing dependencies):**
```bash
cd ~/Robeco_Investment_AI
source venv/bin/activate
pip install -r requirements.txt
```

**If PDF generation fails:**
```bash
cd ~/Robeco_Investment_AI/src/robeco/backend
npm install puppeteer
```

**Check server health:**
```bash
curl -s http://localhost:8005/health
```

### 📋 One-liner Commands

**Quick Status Check:**
```bash
cd ~/Robeco_Investment_AI && ps aux | grep professional_streaming_server | grep -v grep && tail -5 robeco_server.log
```

**Quick Restart:**
```bash
cd ~/Robeco_Investment_AI && pkill -f "professional_streaming_server.py" && source venv/bin/activate && cd src/robeco/backend && nohup ../../../venv/bin/python professional_streaming_server.py > ../../../robeco_server.log 2>&1 &
```

**Quick Commit:**
```bash
cd ~/Robeco_Investment_AI && git add . && git commit -m "Server updates" && git push origin main
```

### 🔑 Key Files
- **Server Script**: `~/Robeco_Investment_AI/src/robeco/backend/professional_streaming_server.py`
- **Log File**: `~/Robeco_Investment_AI/robeco_server.log`
- **Virtual Environment**: `~/Robeco_Investment_AI/venv/`
- **Dependencies**: `~/Robeco_Investment_AI/requirements.txt`

---
*Generated for efficient server management* 🤖