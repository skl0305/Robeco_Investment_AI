#!/bin/bash
# Automatic Port Forwarding Script for Robeco
# Multiple methods to enable http://138.199.60.185:8005 access

echo "🌐 Robeco Automatic Port Forwarding Setup"
echo "🎯 Goal: Enable http://138.199.60.185:8005 global access"
echo ""

# Method 1: UPnP Automatic Configuration
echo "📡 Method 1: UPnP Automatic Port Forwarding..."
if command -v upnpc &> /dev/null; then
    echo "✅ UPnP client found, attempting automatic setup..."
    upnpc -a 10.7.7.2 8005 8005 TCP
    if [ $? -eq 0 ]; then
        echo "✅ UPnP port forwarding successful!"
        echo "🌍 http://138.199.60.185:8005 should now be accessible globally"
        exit 0
    else
        echo "⚠️  UPnP failed, trying next method..."
    fi
else
    echo "⚠️  UPnP client not found, installing..."
    brew install miniupnpc 2>/dev/null
    if command -v upnpc &> /dev/null; then
        upnpc -a 10.7.7.2 8005 8005 TCP
        if [ $? -eq 0 ]; then
            echo "✅ UPnP port forwarding successful!"
            echo "🌍 http://138.199.60.185:8005 should now be accessible globally"
            exit 0
        fi
    fi
fi

# Method 2: Router Detection and Instructions
echo ""
echo "📡 Method 2: Router Configuration Instructions..."

# Try to detect router
ROUTER_IP=$(route -n get default 2>/dev/null | grep gateway | awk '{print $2}' | head -1)
if [ -z "$ROUTER_IP" ]; then
    ROUTER_IP=$(netstat -rn | grep default | grep en0 | awk '{print $2}' | head -1)
fi
if [ -z "$ROUTER_IP" ]; then
    ROUTER_IP="172.20.10.1"  # Fallback to known IP
fi

echo "📍 Detected router IP: $ROUTER_IP"

# Try common router access methods
echo "🔍 Testing router accessibility..."
for ip in "$ROUTER_IP" "192.168.1.1" "192.168.0.1" "10.0.0.1" "172.20.10.1"; do
    if curl -s --connect-timeout 3 "http://$ip" > /dev/null 2>&1; then
        echo "✅ Router accessible at: http://$ip"
        open "http://$ip" 2>/dev/null
        ROUTER_FOUND="$ip"
        break
    fi
done

if [ -n "$ROUTER_FOUND" ]; then
    echo ""
    echo "🎯 ROUTER CONFIGURATION INSTRUCTIONS:"
    echo "============================================"
    echo "Router Admin Panel: http://$ROUTER_FOUND"
    echo ""
    echo "1. Login to router admin panel (check router label for password)"
    echo "2. Find 'Port Forwarding' or 'Virtual Server' section"
    echo "3. Add new rule:"
    echo "   • Service Name: Robeco"
    echo "   • External Port: 8005"
    echo "   • Internal IP: 10.7.7.2"
    echo "   • Internal Port: 8005"
    echo "   • Protocol: TCP"
    echo "4. Save and restart router"
    echo ""
    echo "🌍 After setup: http://138.199.60.185:8005 will work globally!"
else
    echo "⚠️  Router not accessible via web interface"
    echo "💡 Manual router configuration may be needed"
fi

# Method 3: Alternative Access Methods
echo ""
echo "📡 Method 3: Alternative Access Information..."
echo "If router configuration is not possible, you have these options:"
echo ""
echo "🔗 SSH Tunnel (Already Working):"
echo "   Global URL: Check your running Robeco server for the serveo.net URL"
echo "   ✅ No router setup needed"
echo "   ✅ Works immediately"
echo ""
echo "📱 Mobile Hotspot Method:"
echo "   1. Enable mobile hotspot on your phone"
echo "   2. Connect Mac to phone hotspot"
echo "   3. Share phone's IP with users"
echo "   ✅ Bypasses router completely"
echo ""
echo "🎯 Current Status:"
echo "   • Local access: http://10.7.7.2:8005"
echo "   • Target global: http://138.199.60.185:8005"
echo "   • SSH tunnel: Active (check Robeco logs)"

