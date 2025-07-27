#!/bin/sh
set -e

echo "📍 Checking out master..."
git checkout master

echo "🌳 Current branches:"
git branch -a

echo "🔗 Current remotes:"
git remote

# echo "📥 Pulling latest from origin/master..."
# git pull origin

# Set environment variable
API_ENDPOINT="http://localhost:5000/docufy"
DOCUBUDDY_URL="$API_ENDPOINT"

if [ -z "$DOCUBUDDY_URL" ]; then
    echo "❌ Environment variable API_ENDPOINT is not set"
    exit 1
fi

echo "🌐 Using API endpoint: $DOCUBUDDY_URL"

echo "🔍 Getting git diff between HEAD~1 and HEAD:"
DIFF=$(git diff HEAD~1 HEAD)
echo "--------- BEGIN DIFF ---------"
echo "$DIFF"
echo "---------- END DIFF ----------"

echo "📤 Sending diff to API and receiving patch..."

PATCH=$(curl -X GET "$DOCUBUDDY_URL")

echo "📨 API response received:"
echo "--------- BEGIN PATCH ---------"
echo "$PATCH"
echo "---------- END PATCH ----------"


echo "📌 Applying patch using git apply..."
echo "$PATCH" | git apply -v -

echo "✅ Patch applied successfully."