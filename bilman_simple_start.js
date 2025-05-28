#!/usr/bin/env node

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🚀 Starting Bilman VPN Management System');
console.log('=====================================');

// Check if bilman directory exists
const bilmanDir = path.join(__dirname, 'bilman');
if (!fs.existsSync(bilmanDir)) {
    console.error('❌ Bilman directory not found');
    process.exit(1);
}

// Set environment variables
process.env.NODE_ENV = 'development';
process.env.PORT = '3000';

console.log('📂 Project directory:', bilmanDir);
console.log('🌐 Starting development server...');

// Change to bilman directory and start the application
process.chdir(bilmanDir);

// Start the Next.js development server
const server = exec('npm run dev', (error, stdout, stderr) => {
    if (error) {
        console.error('❌ Error starting server:', error);
        return;
    }
});

server.stdout.on('data', (data) => {
    console.log(data);
});

server.stderr.on('data', (data) => {
    console.error(data);
});

server.on('close', (code) => {
    console.log(`Server process exited with code ${code}`);
});

// Handle process termination
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server...');
    server.kill();
    process.exit(0);
});

console.log('✅ Server startup initiated');
console.log('📱 Access at: http://localhost:3000');