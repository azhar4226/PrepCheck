#!/bin/bash

# PrepCheck API Testing Script
echo "🧪 PrepCheck API Testing"
echo "========================"

BASE_URL="http://localhost:8000"

# Test admin login and get token
echo "1. Testing admin login..."
ADMIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@prepcheck.com",
    "password": "admin123"
  }')

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Failed to get admin token"
    echo "Response: $ADMIN_RESPONSE"
    exit 1
fi

echo "✅ Admin login successful"

# Test analytics overview
echo ""
echo "2. Testing analytics overview..."
ANALYTICS_RESPONSE=$(curl -s -X GET $BASE_URL/api/analytics/overview \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if echo $ANALYTICS_RESPONSE | grep -q "stats"; then
    echo "✅ Analytics overview working"
    echo "📊 Total users: $(echo $ANALYTICS_RESPONSE | grep -o '"total_users":[0-9]*' | cut -d':' -f2)"
else
    echo "❌ Analytics overview failed"
    echo "Response: $ANALYTICS_RESPONSE"
fi

# Test notifications
echo ""
echo "3. Testing notifications..."
NOTIFICATIONS_RESPONSE=$(curl -s -X GET $BASE_URL/api/notifications/ \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if echo $NOTIFICATIONS_RESPONSE | grep -q "notifications"; then
    echo "✅ Notifications endpoint working"
    UNREAD_COUNT=$(echo $NOTIFICATIONS_RESPONSE | grep -o '"unread_count":[0-9]*' | cut -d':' -f2)
    echo "📬 Unread notifications: $UNREAD_COUNT"
else
    echo "❌ Notifications failed"
    echo "Response: $NOTIFICATIONS_RESPONSE"
fi

# Test send test notification
echo ""
echo "4. Testing send test notification..."
TEST_NOTIF_RESPONSE=$(curl -s -X POST $BASE_URL/api/notifications/send-test \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if echo $TEST_NOTIF_RESPONSE | grep -q "Test notification sent"; then
    echo "✅ Test notification sent successfully"
else
    echo "❌ Test notification failed"
    echo "Response: $TEST_NOTIF_RESPONSE"
fi

# Test regular user endpoints
echo ""
echo "5. Testing regular user login..."
USER_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }')

USER_TOKEN=$(echo $USER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
    echo "❌ Failed to get user token"
else
    echo "✅ User login successful"
    
    # Test user notifications
    echo ""
    echo "6. Testing user notifications..."
    USER_NOTIF_RESPONSE=$(curl -s -X GET $BASE_URL/api/notifications/ \
      -H "Authorization: Bearer $USER_TOKEN")
    
    if echo $USER_NOTIF_RESPONSE | grep -q "notifications"; then
        echo "✅ User notifications working"
    else
        echo "❌ User notifications failed"
    fi
fi

echo ""
echo "🎉 API testing completed!"
echo "💡 Frontend is available at: http://localhost:3001"
echo "💡 Production frontend at: http://localhost"
