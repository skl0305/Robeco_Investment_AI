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

### 🔄 Update Code from GitHub (Safe Method)
```bash
cd ~/Robeco_Investment_AI
git stash push -m "Auto-stash before pull $(date)"
git pull origin main
git stash list  # Check if stash was created
```

### 🔍 Check Consistency with GitHub
```bash
cd ~/Robeco_Investment_AI
echo "=== Local Status ==="
git status
echo "=== Compare with Remote ==="
git fetch origin
git diff HEAD origin/main --stat
echo "=== Local vs Remote Commits ==="
echo "Local commits:" && git log --oneline -5
echo "Remote commits:" && git log origin/main --oneline -5
echo "=== Files that differ ==="
git diff --name-only HEAD origin/main
```

### 🔒 Force Sync with GitHub (100% Identical - DESTRUCTIVE)
```bash
cd ~/Robeco_Investment_AI
echo "⚠️ WARNING: This will DELETE all local changes!"
echo "Current status:" && git status
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5
git fetch origin
git reset --hard origin/main
git clean -fd
echo "✅ Server is now 100% identical to GitHub"
```

### ✅ Verify Complete Consistency
```bash
cd ~/Robeco_Investment_AI
echo "=== Consistency Check ==="
git status
echo "Local HEAD: $(git rev-parse HEAD)"
echo "Remote HEAD: $(git rev-parse origin/main)"
if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
    echo "✅ SERVER IS IDENTICAL TO GITHUB"
else
    echo "❌ SERVER DIFFERS FROM GITHUB"
    git diff --stat HEAD origin/main
fi
```

### 🔄 Smart Update (Handles Conflicts Automatically)
```bash
cd ~/Robeco_Investment_AI
echo "=== Starting Smart Update ==="
# Save current state
git add .
git stash push -m "Auto-backup before sync $(date)"

# Try normal pull first
echo "Attempting normal pull..."
if git pull origin main; then
    echo "✅ Normal pull successful"
else
    echo "⚠️ Pull failed, forcing sync..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
    echo "✅ Forced sync complete"
fi

echo "=== Update Complete ==="
git status
echo "Local HEAD: $(git rev-parse HEAD)"
echo "Remote HEAD: $(git rev-parse origin/main)"
```

### 📤 Commit & Push Changes to GitHub
```bash
cd ~/Robeco_Investment_AI
git add .
git status
git commit -m "Update server configuration"
git push origin main
```

### 🔍 Check Commit Status
```bash
cd ~/Robeco_Investment_AI
git status
git log --oneline -3
```

### 🎯 GUARANTEE 100% CONSISTENCY (Recommended)
```bash
cd ~/Robeco_Investment_AI
echo "=== Ensuring 100% GitHub Consistency ==="

# Stop server
echo "Stopping server..."
pkill -f "professional_streaming_server.py"

# Backup any local changes
echo "Backing up local changes..."
git add .
git stash push -m "Pre-sync backup $(date)"

# Force sync with GitHub
echo "Syncing with GitHub..."
git fetch origin
git reset --hard origin/main
git clean -fd

# Verify consistency
echo "Verifying consistency..."
if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
    echo "✅ SERVER IS 100% IDENTICAL TO GITHUB"
else
    echo "❌ SYNC FAILED - manual intervention needed"
    exit 1
fi

# Restart server
echo "Restarting server..."
source venv/bin/activate
cd src/robeco/backend
nohup ../../../venv/bin/python professional_streaming_server.py > ../../../robeco_server.log 2>&1 &

# Verify server started
sleep 3
if ps aux | grep professional_streaming_server | grep -v grep > /dev/null; then
    echo "✅ SERVER RESTARTED SUCCESSFULLY"
    echo "🌍 Available at: http://47.236.59.51:8005/"
else
    echo "❌ SERVER FAILED TO START"
    tail -20 ../../../robeco_server.log
fi
```

### 🔄 Full Restart (Safe Update + Restart)
```bash
cd ~/Robeco_Investment_AI
pkill -f "professional_streaming_server.py"
git stash push -m "Auto-stash $(date)"
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