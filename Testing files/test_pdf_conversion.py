#!/usr/bin/env python3
"""
Test script to verify PDF conversion API endpoint is working
"""

import requests
import json

# Test data
test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #005F90; }
        .content { padding: 20px; background: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Test Investment Report</h1>
    <div class="content">
        <p>This is a test HTML report for PDF conversion.</p>
        <h2>Investment Analysis</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    </div>
</body>
</html>
"""

def test_pdf_conversion():
    """Test PDF conversion API endpoint"""
    
    url = "http://127.0.0.1:8005/api/professional/convert"
    
    data = {
        "html_content": test_html,
        "company_name": "Test Company",
        "ticker": "TEST",
        "format": "pdf"
    }
    
    print("🧪 Testing PDF conversion API...")
    print(f"📍 URL: {url}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF conversion successful!")
            print(f"📄 Status: {result.get('status')}")
            print(f"📁 File path: {result.get('file_path')}")
            print(f"💬 Message: {result.get('message')}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on port 8005?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - PDF conversion may be taking too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_word_conversion():
    """Test Word conversion API endpoint for comparison"""
    
    url = "http://127.0.0.1:8005/api/professional/convert"
    
    data = {
        "html_content": test_html,
        "company_name": "Test Company", 
        "ticker": "TEST",
        "format": "word"
    }
    
    print("\n🧪 Testing Word conversion API...")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Word conversion successful!")
            print(f"📄 Status: {result.get('status')}")
            print(f"📁 File path: {result.get('file_path')}")
            return True
        else:
            print(f"❌ Word API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Word conversion error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PDF Conversion API Test")
    print("=" * 50)
    
    # Test PDF conversion
    pdf_success = test_pdf_conversion()
    
    # Test Word conversion for comparison
    word_success = test_word_conversion()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"PDF Conversion: {'✅ PASS' if pdf_success else '❌ FAIL'}")
    print(f"Word Conversion: {'✅ PASS' if word_success else '❌ FAIL'}")
    
    if pdf_success and word_success:
        print("\n🎉 All tests passed! PDF conversion feature is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the server logs for more details.")