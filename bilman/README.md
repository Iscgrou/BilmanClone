# VPN Management System

A modern web application for managing VPN services, built with Next.js 13, Prisma, and PostgreSQL.

## Features

- 🔐 Secure Authentication System
- �� User Role Management (Admin, Operator, Representative)
- 💰 Invoice and Payment Tracking
- 📊 Analytics Dashboard
- 🔄 Referral System
- 🤖 Telegram Integration
- 🌐 Multi-language Support (Persian/English)
- 🔒 SSL Encryption
- 🐳 Docker Containerization

## Tech Stack

- **Frontend**: Next.js 13, Tailwind CSS
- **Backend**: Next.js API Routes
- **Database**: PostgreSQL
- **ORM**: Prisma
- **Authentication**: NextAuth.js
- **Deployment**: Docker

## Requirements

- Ubuntu 22.04 LTS
- Node.js 18.x or later
- PostgreSQL 14 or later
- Domain name (for production)
- Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Installation

For complete installation instructions, see [INSTALLATION.md](INSTALLATION.md).

Quick start:
```bash
# Clone the repository
git clone https://github.com/Iscgrou/bilman.git
cd bilman

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
npx prisma migrate deploy
npx prisma db seed

# Start development server
npm run dev
```

## Project Structure

```
├── prisma/               # Database schema and migrations
├── src/
│   ├── app/             # Next.js 13 app directory
│   ├── components/      # Reusable UI components
│   ├── contexts/        # React contexts
│   └── lib/            # Utility functions and configurations
├── public/             # Static assets
└── docker/            # Docker configuration files
```

## Development

Default development credentials:
- Admin User:
  - Username: admin
  - Password: admin123 (change immediately)

## Security Features

- Secure password hashing with bcrypt
- JWT-based authentication
- Role-based access control
- Rate limiting on API routes
- SSL encryption in production
- Secure session management

## Database Backups

Automated daily backups at 2 AM:
```bash
# Manual backup
pg_dump -U bilman_user bilman > backup.sql

# Restore from backup
psql -U bilman_user bilman < backup.sql
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and feature requests, please create an issue in the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
