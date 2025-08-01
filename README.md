# Home Budget App

A modern, streamlined home budgeting application with SimpleFIN integration, budget rollover functionality, and comprehensive financial management features.

## Features

- **Budget Rollover**: Transfer overages/deficits between months with per-item control
- **SimpleFIN Integration**: Secure bank transaction import
- **AI Receipt Processing**: Google AI-powered receipt scanning and transaction splitting
- **QuickBooks Sync**: GL categorization and accounting integration
- **Net Worth Tracking**: Comprehensive asset and liability management
- **OCR Import**: Bank/investment statement processing when API unavailable
- **Secure Document Storage**: Encrypted storage for important financial documents

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React with Next.js
- **Database**: PostgreSQL with encryption
- **Deployment**: Ubuntu 22.04.5 LTS server
- **Security**: OAuth2, JWT, end-to-end encryption

## Setup Instructions

1. Run the setup script: `./scripts/setup-ubuntu.sh`
2. Configure environment variables: `cp .env.example .env`
3. Initialize database: `./scripts/init-db.sh`
4. Start development servers: `./scripts/dev-start.sh`

## Project Structure

```
home-budget-app/
├── backend/          # FastAPI application
├── frontend/         # React/Next.js application
├── database/         # Database schemas and migrations
├── scripts/          # Setup and utility scripts
├── docs/            # Documentation
└── docker/          # Docker configuration
```

## Security Notes

This application handles sensitive financial data. All setup scripts include security hardening steps and encryption configuration.
