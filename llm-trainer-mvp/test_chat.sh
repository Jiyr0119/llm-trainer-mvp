#!/bin/bash

# Test script for chat backend

# Step 1: Login and get token
echo "Step 1: Logging in..."
TOKEN=$(curl -s -X POST 'http://localhost:8001/api/auth/login/json' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  exit 1
fi

echo "Token obtained"

# Step 2: Create a conversation
echo -e "\nStep 2: Creating conversation..."
CONV_RESPONSE=$(curl -s -X POST 'http://localhost:8001/api/chat/conversations' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Test Chat","model":"qwen-1.5-0.5b"}')

echo "$CONV_RESPONSE" | python3 -m json.tool

CONV_ID=$(echo "$CONV_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$CONV_ID" ]; then
  echo "Failed to create conversation"
  exit 1
fi

echo "Conversation ID: $CONV_ID"

# Step 3: Test streaming chat
echo -e "\nStep 3: Testing streaming chat..."
curl -X POST 'http://localhost:8001/api/chat/completions' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"model\": \"qwen-1.5-0.5b\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Hello, write a simple python hello world\"}],
    \"temperature\": 0.7,
    \"max_tokens\": 2048,
    \"stream\": true
  }"

echo -e "\n\nTest complete!"
