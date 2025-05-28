#!/bin/bash
# Node.js Application Startup Script - Added by deployment fix

echo "Starting Node.js application..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the application
echo "Starting server..."
npm start
