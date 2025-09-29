#!/bin/bash
# Robeco Investment AI System - One-Click Startup Script
# Ensures identical behavior between local Mac and SSH server environments

echo "🚀 Starting Robeco Investment AI System..."
echo "📍 Project Directory: $(pwd)"

# 1. Set Python Path for module imports
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
echo "✅ PYTHONPATH configured: $PYTHONPATH"

# 2. Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found - using system Python"
fi

# 3. Check critical dependencies
echo "🔍 Checking dependencies..."

# Check Python packages
python -c "import fastapi, uvicorn, websockets; print('✅ FastAPI/WebSocket OK')" || {
    echo "❌ Missing FastAPI dependencies"
    exit 1
}

python -c "from google import genai; print('✅ Google Genai OK')" || {
    echo "❌ Missing Google Genai"
    exit 1
}

# Check Node.js dependencies
if [ -f "package.json" ]; then
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    echo "✅ Node.js dependencies OK"
fi

# 4. Test Robeco module imports
python -c "from robeco.backend.template_report_generator import RobecoTemplateReportGenerator; print('✅ Robeco modules OK')" || {
    echo "❌ Robeco module import failed - check PYTHONPATH"
    exit 1
}

# 5. Set Chrome path for Puppeteer (OS-specific)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux (server)
    export PUPPETEER_EXECUTABLE_PATH=/root/.cache/puppeteer/chrome/linux-140.0.7339.207/chrome-linux64/chrome
    echo "✅ Chrome path configured for Linux server"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (local) - let Puppeteer find Chrome automatically
    echo "✅ Using system Chrome on macOS"
else
    echo "⚠️  Unknown OS type: $OSTYPE"
fi

# 5. Start the server
echo "🌟 Starting Robeco Professional System..."
echo "📡 Server will be available at: http://0.0.0.0:8005"
echo "🌍 External access: http://188.95.54.49:8005/"
echo "⌨️  Press Ctrl+C to stop"

# Check running mode - DEFAULT to BACKGROUND for better user experience
if [[ "$1" == "--foreground" || "$1" == "-f" ]]; then
    echo "💻 Starting server in FOREGROUND mode (interactive)..."
    python -u run_professional_system.py
else
    # DEFAULT: Background mode (most users want persistent server)
    echo "🔄 Starting server in BACKGROUND mode (survives SSH disconnect)..."
    echo "💡 Use --foreground if you want interactive mode instead"
    nohup python -u run_professional_system.py > robeco_server.log 2>&1 &
    echo $! > robeco_server.pid
    echo "✅ Server started in background with PID: $(cat robeco_server.pid)"
    echo "📄 View logs: tail -f robeco_server.log"
    echo "🛑 Stop: kill $(cat robeco_server.pid) or just restart this script"
    echo ""
    echo "🌍 Server is now running persistently!"
    echo "   📍 Safe to close SSH window now!"
fi