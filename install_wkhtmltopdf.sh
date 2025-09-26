#!/bin/bash

# Install wkhtmltopdf for PDF generation
# This script installs wkhtmltopdf on macOS and Linux

echo "🔧 Installing wkhtmltopdf for PDF generation..."

# Detect the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📱 Detected macOS - Installing via Homebrew..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install wkhtmltopdf
    echo "⬇️ Installing wkhtmltopdf..."
    brew install wkhtmltopdf
    
    if command -v wkhtmltopdf &> /dev/null; then
        echo "✅ wkhtmltopdf installed successfully!"
        echo "📍 Location: $(which wkhtmltopdf)"
        wkhtmltopdf --version
    else
        echo "❌ wkhtmltopdf installation failed"
        exit 1
    fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Detected Linux - Installing via package manager..."
    
    # Detect Linux distribution
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        echo "📦 Using apt-get (Ubuntu/Debian)..."
        sudo apt-get update
        sudo apt-get install -y wkhtmltopdf
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        echo "📦 Using yum (CentOS/RHEL)..."
        sudo yum install -y wkhtmltopdf
        
    elif command -v dnf &> /dev/null; then
        # Fedora
        echo "📦 Using dnf (Fedora)..."
        sudo dnf install -y wkhtmltopdf
        
    else
        echo "❌ Unsupported Linux distribution. Please install wkhtmltopdf manually."
        echo "   Visit: https://wkhtmltopdf.org/downloads.html"
        exit 1
    fi
    
    if command -v wkhtmltopdf &> /dev/null; then
        echo "✅ wkhtmltopdf installed successfully!"
        echo "📍 Location: $(which wkhtmltopdf)"
        wkhtmltopdf --version
    else
        echo "❌ wkhtmltopdf installation failed"
        exit 1
    fi

else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please install wkhtmltopdf manually from: https://wkhtmltopdf.org/downloads.html"
    exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo "💡 You can now use the PDF conversion feature in Robeco Investment Platform"
echo "🔄 Step 1: Generate HTML report → Step 2: Convert to Word/PDF document"