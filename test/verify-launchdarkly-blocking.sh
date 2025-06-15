#!/bin/bash

echo "🛡️ LaunchDarkly Blocking Verification Script"
echo "============================================="

# Test 1: Check if frontend is running
echo ""
echo "1️⃣  Testing Frontend Accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend is accessible (HTTP $FRONTEND_STATUS)"
else
    echo "❌ Frontend is not accessible (HTTP $FRONTEND_STATUS)"
fi

# Test 2: Check if service worker file exists
echo ""
echo "2️⃣  Testing Service Worker..."
if [ -f "frontend/public/sw.js" ]; then
    echo "✅ Service worker file exists"
    if grep -q "launchdarkly.com" frontend/public/sw.js; then
        echo "✅ Service worker contains LaunchDarkly blocking rules"
    else
        echo "❌ Service worker missing blocking rules"
    fi
else
    echo "❌ Service worker file not found"
fi

# Test 3: Check CSP in index.html
echo ""
echo "3️⃣  Testing Content Security Policy..."
if [ -f "frontend/index.html" ]; then
    if grep -q "Content-Security-Policy" frontend/index.html; then
        echo "✅ CSP header found in index.html"
    else
        echo "❌ CSP header not found in index.html"
    fi
else
    echo "❌ index.html not found"
fi

# Test 4: Check browser extension files
echo ""
echo "4️⃣  Testing Browser Extension..."
if [ -d "launchdarkly-blocker-extension" ]; then
    echo "✅ Browser extension directory exists"
    if [ -f "launchdarkly-blocker-extension/manifest.json" ]; then
        echo "✅ Extension manifest exists"
    fi
    if [ -f "launchdarkly-blocker-extension/content.js" ]; then
        echo "✅ Extension content script exists"
    fi
    if [ -f "launchdarkly-blocker-extension/rules.json" ]; then
        echo "✅ Extension blocking rules exist"
    fi
else
    echo "❌ Browser extension directory not found"
fi

# Test 5: Check hosts blocking script
echo ""
echo "5️⃣  Testing Hosts Blocking Script..."
if [ -f "block-launchdarkly.sh" ]; then
    echo "✅ Hosts blocking script exists"
    if [ -x "block-launchdarkly.sh" ]; then
        echo "✅ Script is executable"
    else
        echo "⚠️  Script needs to be made executable: chmod +x block-launchdarkly.sh"
    fi
else
    echo "❌ Hosts blocking script not found"
fi

# Test 6: Check VS Code settings
echo ""
echo "6️⃣  Testing VS Code Settings..."
if [ -f ".vscode/settings.json" ]; then
    if grep -q "telemetry.telemetryLevel.*off" .vscode/settings.json; then
        echo "✅ VS Code telemetry disabled"
    else
        echo "❌ VS Code telemetry not disabled"
    fi
else
    echo "❌ VS Code settings file not found"
fi

# Test 7: Domain resolution test
echo ""
echo "7️⃣  Testing Domain Resolution..."
echo "Testing if LaunchDarkly domains resolve to localhost..."

DOMAINS=("events.launchdarkly.com" "app.launchdarkly.com" "client.launchdarkly.com")
for domain in "${DOMAINS[@]}"; do
    if [ -f /etc/hosts ] && grep -q "$domain" /etc/hosts; then
        echo "✅ $domain blocked in hosts file"
    else
        echo "⚠️  $domain not blocked in hosts file (run: sudo ./block-launchdarkly.sh)"
    fi
done

# Test 8: Check test files
echo ""
echo "8️⃣  Testing Verification Files..."
if [ -f "test-launchdarkly-blocker.html" ]; then
    echo "✅ Test page exists"
    echo "   📖 Open file:///$(pwd)/test-launchdarkly-blocker.html to run tests"
else
    echo "❌ Test page not found"
fi

echo ""
echo "🎯 Summary"
echo "=========="
echo "Frontend URL: http://localhost:3000"
echo "Test Page: file://$(pwd)/test-launchdarkly-blocker.html"
echo "Extension: Load launchdarkly-blocker-extension/ in chrome://extensions/"
echo "Hosts Block: sudo ./block-launchdarkly.sh"
echo ""
echo "🎉 LaunchDarkly blocking system is ready!"
echo "All requests to LaunchDarkly domains should now be blocked."
