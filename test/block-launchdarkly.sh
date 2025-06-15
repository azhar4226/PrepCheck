#!/bin/bash

# LaunchDarkly Blocker Script
# This script blocks LaunchDarkly tracking domains system-wide

echo "🛡️ LaunchDarkly Domain Blocker"
echo "=============================="

# Backup hosts file
if [ ! -f /etc/hosts.backup ]; then
    echo "📝 Creating backup of hosts file..."
    sudo cp /etc/hosts /etc/hosts.backup
    echo "✅ Backup created at /etc/hosts.backup"
fi

# LaunchDarkly domains to block
DOMAINS=(
    "events.launchdarkly.com"
    "app.launchdarkly.com" 
    "client.launchdarkly.com"
    "mobile.launchdarkly.com"
    "stream.launchdarkly.com"
    "clientstream.launchdarkly.com"
    "clientsdk.launchdarkly.com"
)

echo "🚫 Adding domains to hosts file..."

# Add blocking entries
for domain in "${DOMAINS[@]}"; do
    if ! grep -q "$domain" /etc/hosts; then
        echo "127.0.0.1 $domain" | sudo tee -a /etc/hosts > /dev/null
        echo "   ✅ Blocked: $domain"
    else
        echo "   ⚠️  Already blocked: $domain"
    fi
done

echo ""
echo "🎉 LaunchDarkly tracking domains have been blocked!"
echo ""
echo "To unblock (restore original hosts file):"
echo "sudo cp /etc/hosts.backup /etc/hosts"
echo ""
echo "To verify blocking:"
echo "ping events.launchdarkly.com"
echo "(Should resolve to 127.0.0.1)"
