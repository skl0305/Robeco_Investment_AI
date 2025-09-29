#!/bin/bash
# Robeco Investment AI System - Complete Dependency Installation Script
# For SSH servers to match local Mac environment exactly

echo "🚀 Installing Robeco Investment AI System Dependencies..."
echo "🎯 Ensuring identical behavior between local and server environments"

# 1. System-level dependencies (Chrome for Puppeteer)
echo "📦 Installing system dependencies..."

# Update package list
sudo apt-get update

# Install Chrome and required libraries
echo "🌐 Installing Chrome dependencies..."
sudo apt-get install -y \
    libasound2t64 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libdrm2 \
    libgtk-3-0t64 \
    libgtk-4-1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libgconf-2-4 \
    libxtst6 \
    libxfixes3 \
    libxi6 \
    libxcursor1 \
    libnss3 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libasound2t64 \
    libpangocairo-1.0-0 \
    libatk1.0-0t64 \
    libcairo-gobject2 \
    libgtk-3-0t64 \
    libgdk-pixbuf2.0-0 \
    libappindicator3-1

# Install Chrome browser
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install PDF processing tools
echo "📄 Installing PDF processing tools..."
sudo apt-get install -y wkhtmltopdf xvfb

# Install fonts for proper rendering
echo "🔤 Installing fonts..."
sudo apt-get install -y fonts-liberation fonts-dejavu-core fonts-freefont-ttf

# 2. Python dependencies
echo "🐍 Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# 3. Node.js dependencies
echo "📦 Installing Node.js dependencies..."

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install npm packages
npm install

# 4. Test installations
echo "🔍 Testing installations..."

# Test Puppeteer
echo "🧪 Testing Puppeteer..."
node -e "
const puppeteer = require('puppeteer');
(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });
    console.log('✅ Puppeteer working correctly');
    await browser.close();
  } catch (error) {
    console.log('❌ Puppeteer error:', error.message);
    process.exit(1);
  }
})();
"

# Test Python imports with PYTHONPATH
echo "🧪 Testing Python modules..."
PYTHONPATH="$(pwd)/src:$PYTHONPATH" python -c "
try:
    from robeco.backend.template_report_generator import RobecoTemplateReportGenerator
    from google import genai
    import fastapi, uvicorn, websockets
    print('✅ All Python modules working correctly')
except Exception as e:
    print(f'❌ Python module error: {e}')
    exit(1)
"

echo ""
echo "🎉 Installation completed successfully!"
echo "✅ All dependencies installed and tested"
echo ""
echo "🚀 To start the server, run:"
echo "   ./start_robeco_server.sh"
echo ""
echo "🌍 Or manually with:"
echo "   PYTHONPATH=\"$(pwd)/src:\$PYTHONPATH\" python run_professional_system.py"