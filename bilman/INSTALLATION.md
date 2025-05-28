# Complete Step-by-Step Installation Guide

## System Requirements

1. **Operating System**
```bash
# Ubuntu 20.04 or later recommended
# Check OS version
lsb_release -a
```

2. **Node.js Installation**
```bash
# Install Node.js 18.x (recommended for Next.js 13+)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation (should show v18.x.x)
node --version
npm --version

# Install required global packages
sudo npm install -g pm2
```

3. **PostgreSQL Installation**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

## PostgreSQL Database Setup

1. **Switch to postgres user**
```bash
# Switch to postgres user
sudo su - postgres

# Now you're in postgres user shell
```

2. **Create Database and User**
```bash
# Start PostgreSQL command prompt
psql

# Once you see 'postgres=#', run these commands one by one:

# Create database
CREATE DATABASE bilman;

# Create user and set password (replace with your actual password)
CREATE USER bilman_user WITH ENCRYPTED PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bilman TO bilman_user;

# Connect to the bilman database
\c bilman

# Grant schema privileges to the user
GRANT ALL ON SCHEMA public TO bilman_user;

# Verify the user and database
\du  # List users
\l   # List databases

# Exit PostgreSQL
\q

# Exit postgres user shell
exit
```

3. **Test Database Connection**
```bash
# Test connection with the new user
psql -U bilman_user -h localhost -d bilman
# Enter your password when prompted
```

## Project Installation

1. **Prepare Installation Directory**
```bash
# Create www directory if it doesn't exist
sudo mkdir -p /var/www

# Set proper permissions
sudo chown -R $USER:$USER /var/www
sudo chmod -R 755 /var/www

# Navigate to directory
cd /var/www

# Clone the repository
git clone https://github.com/Iscgrou/bilman.git

# Navigate to project directory
cd bilman
```

2. **Environment Configuration**
```bash
# Create and edit .env file
nano .env
```

Add the following configuration to your `.env` file (replace the values with your actual configuration):
```env
# Database configuration
DATABASE_URL="postgresql://bilman_user:your_actual_password@localhost:5432/bilman"

# JWT configuration (generate a secure random string)
JWT_SECRET="generate-a-secure-random-string-here"

# Application configuration
NODE_ENV="production"
PORT=3000

# Optional: Additional security settings
NEXTAUTH_URL="https://your-domain.com"  # Replace with your domain
NEXTAUTH_SECRET="generate-another-secure-random-string"  # For NextAuth.js
```

To generate secure random strings for secrets:
```bash
# Generate random string for JWT_SECRET
openssl rand -base64 32

# Generate random string for NEXTAUTH_SECRET
openssl rand -base64 32
```

3. **Install Dependencies**
```bash
# Install project dependencies
npm install

# Install TypeScript and other required dependencies
npm install --save-dev typescript ts-node @types/node
npm install --save-dev @types/bcryptjs
npm install bcryptjs

# Fix npm vulnerabilities (optional but recommended)
npm audit fix --force
```

4. **Database Setup**
```bash
# Generate Prisma client
npx prisma generate

# Run database migrations
npx prisma migrate deploy
```

5. **Database Seeding**
First, create the seed file:
```bash
# Create prisma directory if it doesn't exist
mkdir -p prisma

# Create tsconfig.json for TypeScript configuration
cat > tsconfig.json << EOL
{
  "compilerOptions": {
    "target": "es2017",
    "module": "commonjs",
    "lib": ["es2017", "esnext.asynciterable"],
    "skipLibCheck": true,
    "sourceMap": true,
    "outDir": "./dist",
    "moduleResolution": "node",
    "removeComments": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitThis": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "resolveJsonModule": true,
    "baseUrl": "."
  },
  "exclude": ["node_modules"],
  "include": ["./prisma/**/*.ts"]
}
EOL

# Create seed file
cat > prisma/seed.ts << EOL
import { PrismaClient, UserRole } from '@prisma/client';
import { hash } from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
    try {
        // Create default admin user with hashed password
        const hashedPassword = await hash('admin123', 12);
        
        // Create or update admin user
        const admin = await prisma.user.upsert({
            where: { 
                username: 'admin' 
            },
            update: {
                password: hashedPassword,
                role: UserRole.ADMIN
            },
            create: {
                username: 'admin',
                password: hashedPassword,
                role: UserRole.ADMIN
            }
        });

        console.log('Database seeded successfully');
        console.log('Admin user created:', {
            id: admin.id,
            username: admin.username,
            role: admin.role
        });
    } catch (error) {
        console.error('Error seeding database:', error);
        throw error;
    } finally {
        await prisma.$disconnect();
    }
}

main()
    .catch((error) => {
        console.error('Error during seeding:', error);
        process.exit(1);
    });
EOL
```

Then, update package.json to add the seed configuration:
```bash
# Backup existing package.json
cp package.json package.json.backup

# Create a temporary file with the prisma configuration
cat > prisma.json << EOL
{
  "prisma": {
    "seed": "ts-node prisma/seed.ts"
  }
}
EOL

# Install jq if not already installed
sudo apt-get update && sudo apt-get install -y jq

# Merge the prisma configuration into package.json
jq -s '.[0] * .[1]' package.json prisma.json > package.json.new
mv package.json.new package.json
rm prisma.json

# Now run the seed command
npx prisma db seed
```

6. **Build Application**
```bash
# Build the application
npm run build

# Verify build
ls .next
```

[Rest of the file remains unchanged...]
