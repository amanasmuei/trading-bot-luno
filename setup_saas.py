#!/usr/bin/env python3
"""
SaaS Platform Setup Script
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header():
    """Print setup header"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 🚀 LUNO TRADING BOT SAAS SETUP              ║
║                     Platform Initialization                  ║
╚══════════════════════════════════════════════════════════════╝
""")


def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'uploads',
        'data',
        'backups',
        'migrations',
        'src/web/static/css',
        'src/web/static/js',
        'src/web/static/img'
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")


def setup_environment():
    """Setup environment configuration"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path('.env.saas')
    env_example = Path('.env.saas.example')
    
    if not env_file.exists() and env_example.exists():
        print("   📝 Creating .env.saas from example...")
        subprocess.run(['cp', str(env_example), str(env_file)])
        print("   ✅ Environment file created")
        print("   ⚠️  Please edit .env.saas with your configuration")
    elif env_file.exists():
        print("   ✅ Environment file already exists")
    else:
        print("   ❌ No environment example found")


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("   ✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        return False
    
    return True


def initialize_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    
    try:
        # Create the database initialization script
        init_script = """
import os
import sys
sys.path.append(os.getcwd())

from src.saas_app import create_app
from src.models.base import init_db

app = create_app()
with app.app_context():
    init_db(app)
    print("Database initialized successfully!")
"""
        
        # Write and execute the script
        with open('temp_init_db.py', 'w') as f:
            f.write(init_script)
        
        subprocess.run([sys.executable, 'temp_init_db.py'], check=True)
        
        # Clean up
        os.remove('temp_init_db.py')
        
        print("   ✅ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to initialize database: {e}")
        return False


def create_admin_user():
    """Create admin user"""
    print("\n👤 Creating admin user...")
    
    try:
        email = input("   Admin email: ")
        password = input("   Admin password: ")
        first_name = input("   First name: ")
        last_name = input("   Last name: ")
        
        # Create admin user script
        admin_script = f"""
import os
import sys
sys.path.append(os.getcwd())

from src.saas_app import create_app
from src.auth.auth_manager import AuthManager

app = create_app()
with app.app_context():
    user, error = AuthManager.register_user(
        email='{email}',
        password='{password}',
        first_name='{first_name}',
        last_name='{last_name}'
    )
    if user:
        user.is_admin = True
        user.is_verified = True
        user.save()
        print("Admin user created successfully!")
    else:
        print(f"Error: {{error}}")
"""
        
        # Write and execute the script
        with open('temp_create_admin.py', 'w') as f:
            f.write(admin_script)
        
        subprocess.run([sys.executable, 'temp_create_admin.py'], check=True)
        
        # Clean up
        os.remove('temp_create_admin.py')
        
        print("   ✅ Admin user created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create admin user: {e}")
        return False


def create_nginx_config():
    """Create nginx configuration"""
    print("\n🌐 Creating nginx configuration...")
    
    nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream saas_app {
        server saas-app:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://saas_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/src/web/static/;
        }
    }
}
"""
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("   ✅ Nginx configuration created")


def create_prometheus_config():
    """Create prometheus configuration"""
    print("\n📊 Creating prometheus configuration...")
    
    prometheus_config = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'saas-app'
    static_configs:
      - targets: ['saas-app:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
"""
    
    with open('prometheus.yml', 'w') as f:
        f.write(prometheus_config)
    
    print("   ✅ Prometheus configuration created")


def create_gitignore():
    """Create .gitignore file"""
    print("\n📝 Creating .gitignore...")
    
    gitignore_content = """
# Environment files
.env*
!.env.example
!.env.saas.example

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Uploads
uploads/
data/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# Backups
backups/
*.backup
*.dump

# SSL certificates
ssl/
*.pem
*.key
*.crt

# Temporary files
temp_*.py
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("   ✅ .gitignore created")


def print_next_steps():
    """Print next steps"""
    print("""
🎉 SaaS Platform Setup Complete!

📋 Next Steps:
1. Edit .env.saas with your configuration:
   - Database URL
   - JWT secret keys
   - Stripe API keys
   - Email settings
   - Redis URL

2. Start the platform:
   Development: python launch_saas.py --dev
   Production:  python launch_saas.py --prod

3. Access the platform:
   - Landing Page: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin
   - API Docs: http://localhost:5000/docs

4. Monitor the platform:
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

📚 Documentation:
   - Read SAAS_README.md for detailed instructions
   - Check API documentation at /docs
   - Join our Discord for support

🚀 Happy Trading!
""")


def main():
    """Main setup function"""
    print_header()
    
    # Check if we're in the right directory
    if not Path('requirements.txt').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Run setup steps
    create_directories()
    setup_environment()
    
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        sys.exit(1)
    
    if not create_admin_user():
        print("❌ Setup failed at admin user creation")
        sys.exit(1)
    
    create_nginx_config()
    create_prometheus_config()
    create_gitignore()
    
    print_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
