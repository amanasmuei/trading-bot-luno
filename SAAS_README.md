# 🚀 Luno Trading Bot SaaS Platform

A comprehensive multi-tenant Software-as-a-Service platform that provides automated cryptocurrency trading services to multiple users with subscription-based pricing, advanced features, and enterprise-grade infrastructure.

## 🌟 Features

### 🔐 Multi-Tenant Architecture
- **User Management**: Secure registration, authentication, and profile management
- **Role-Based Access Control**: Admin, Premium, Basic, and Free user tiers
- **Tenant Isolation**: Complete data separation between users
- **API Key Management**: Individual API credentials for each user

### 💳 Subscription Management
- **Tiered Pricing Plans**: Free, Basic, Premium, and Enterprise plans
- **Feature-Based Access Control**: Different capabilities per subscription tier
- **Billing Integration**: Automated invoicing and payment processing
- **Usage Tracking**: Monitor API calls, bot usage, and trading pairs

### 🤖 Trading Bot Services
- **Multi-Bot Support**: Users can run multiple trading bots simultaneously
- **Strategy Configuration**: Customizable trading strategies per bot
- **Real-Time Monitoring**: Live bot performance tracking
- **Risk Management**: Advanced stop-loss and take-profit mechanisms

### 📊 Analytics & Reporting
- **Performance Dashboards**: Comprehensive trading analytics
- **Real-Time Metrics**: Live trading data and bot status
- **Historical Reports**: Detailed trading history and performance
- **Export Capabilities**: Download reports in multiple formats

### 🔔 Notification System
- **Multi-Channel Alerts**: Email, SMS, Discord, Slack notifications
- **Customizable Preferences**: User-defined notification settings
- **Real-Time Updates**: Instant alerts for trading activities
- **System Notifications**: Platform updates and maintenance alerts

### 🛡️ Security & Compliance
- **JWT Authentication**: Secure token-based authentication
- **API Rate Limiting**: Prevent abuse and ensure fair usage
- **Data Encryption**: Secure storage of sensitive information
- **Audit Logging**: Complete activity tracking for compliance

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with Redis for caching
- **Authentication**: JWT with Flask-JWT-Extended
- **Task Queue**: Celery with Redis broker
- **Payments**: Stripe integration for billing
- **Monitoring**: Prometheus and Grafana
- **Deployment**: Docker with Docker Compose

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   API Gateway   │    │  Admin Panel    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                    SaaS Application Layer                        │
├─────────────────┬───────────────┼───────────────┬─────────────────┤
│  Authentication │  Subscription │  Trading Bot  │   Billing       │
│     Service     │   Management  │   Management  │   Service       │
└─────────────────┴───────────────┼───────────────┴─────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                     Data Layer                                   │
├─────────────────┬───────────────┼───────────────┬─────────────────┤
│   PostgreSQL    │     Redis     │   File Store  │   Monitoring    │
│   (Primary DB)  │   (Cache)     │   (Uploads)   │   (Metrics)     │
└─────────────────┴───────────────┴───────────────┴─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/luno-trading-saas.git
   cd luno-trading-saas
   ```

2. **Set up environment variables**
   ```bash
   cp .env.saas.example .env.saas
   # Edit .env.saas with your configuration
   ```

3. **Start the platform with Docker**
   ```bash
   docker-compose -f docker-compose.saas.yml up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose -f docker-compose.saas.yml exec saas-app python -c "
   from src.saas_app import app
   from src.models.base import init_db
   with app.app_context():
       init_db(app)
   "
   ```

5. **Create admin user**
   ```bash
   docker-compose -f docker-compose.saas.yml exec saas-app python -c "
   from src.saas_app import app
   from src.auth.auth_manager import AuthManager
   with app.app_context():
       user, error = AuthManager.register_user(
           email='admin@example.com',
           password='secure_password',
           first_name='Admin',
           last_name='User'
       )
       if user:
           user.is_admin = True
           user.is_verified = True
           user.save()
           print('Admin user created successfully')
       else:
           print(f'Error: {error}')
   "
   ```

### Development Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up local database**
   ```bash
   # PostgreSQL
   createdb saas_trading_bot
   
   # Or use SQLite for development
   export DATABASE_URL=sqlite:///saas_trading_bot.db
   ```

3. **Run the application**
   ```bash
   export FLASK_APP=src.saas_app:app
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000
   ```

## 📋 Subscription Plans

### Free Plan
- 1 Trading Bot
- 1 Trading Pair
- 100 API calls/hour
- Email notifications
- Community support

### Basic Plan ($29.99/month)
- 3 Trading Bots
- 5 Trading Pairs
- 1,000 API calls/hour
- Email + SMS notifications
- Email support
- Basic backtesting

### Premium Plan ($99.99/month)
- 10 Trading Bots
- 20 Trading Pairs
- 10,000 API calls/hour
- All notification channels
- Priority support
- Advanced backtesting
- Custom indicators
- API access

### Enterprise Plan ($299.99/month)
- Unlimited Trading Bots
- Unlimited Trading Pairs
- Unlimited API calls
- All features
- Dedicated support
- White-label options
- 99.9% SLA

## 🔌 API Documentation

### Authentication
```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

### Trading Management
```bash
# Create trading configuration
POST /api/v1/trading/configs
Authorization: Bearer <token>
{
  "name": "BTC/MYR Strategy",
  "trading_pair": "XBTMYR",
  "luno_api_key": "your_api_key",
  "luno_api_secret": "your_api_secret",
  "strategy_type": "basic"
}

# Start trading bot
POST /api/v1/trading/bots/<bot_id>/start
Authorization: Bearer <token>
```

### Subscription Management
```bash
# Get available plans
GET /api/v1/subscriptions/plans

# Upgrade subscription
POST /api/v1/subscriptions/upgrade
Authorization: Bearer <token>
{
  "plan_id": 2
}
```

## 🛠️ Administration

### Admin Dashboard
Access the admin dashboard at `/admin` with admin credentials to:
- Monitor system health
- Manage users and subscriptions
- View revenue analytics
- Handle support requests
- Configure system settings

### Monitoring
- **Application Metrics**: http://localhost:9090 (Prometheus)
- **Dashboards**: http://localhost:3000 (Grafana)
- **Health Check**: http://localhost:5000/health

## 🔧 Configuration

### Environment Variables
Key configuration options in `.env.saas`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/saas_trading_bot

# Security
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-flask-secret

# Payments
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📈 Scaling

### Horizontal Scaling
- Multiple application instances behind load balancer
- Separate Celery workers for background tasks
- Database read replicas for improved performance
- Redis clustering for high availability

### Performance Optimization
- Database connection pooling
- Redis caching for frequently accessed data
- API response caching
- Background task processing

## 🔒 Security

### Best Practices
- JWT token expiration and refresh
- API rate limiting per user/plan
- Input validation and sanitization
- SQL injection prevention
- CORS configuration
- HTTPS enforcement

### Data Protection
- Encrypted storage of API credentials
- PII data anonymization
- GDPR compliance features
- Regular security audits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.yourdomain.com](https://docs.yourdomain.com)
- **Community**: [Discord Server](https://discord.gg/your-server)
- **Email**: support@yourdomain.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/luno-trading-saas/issues)

---

**Built with ❤️ for the cryptocurrency trading community**
