#!/usr/bin/env python3
"""
SaaS Trading Bot Platform Launcher
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Print application header"""
    print(f"""
{Colors.BLUE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                 🚀 LUNO TRADING BOT SAAS PLATFORM           ║
║                     Multi-Tenant Trading Platform            ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
""")


def check_requirements():
    """Check if required tools are installed"""
    requirements = {
        'docker': 'Docker is required for containerized deployment',
        'docker-compose': 'Docker Compose is required for multi-service deployment',
        'python3': 'Python 3.11+ is required for development mode'
    }
    
    missing = []
    for tool, description in requirements.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"{Colors.GREEN}✅ {tool} is installed{Colors.END}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Colors.RED}❌ {tool} is not installed - {description}{Colors.END}")
            missing.append(tool)
    
    return len(missing) == 0


def setup_environment():
    """Set up environment configuration"""
    env_file = Path('.env.saas')
    env_example = Path('.env.saas.example')
    
    if not env_file.exists():
        if env_example.exists():
            print(f"{Colors.YELLOW}⚠️  Creating .env.saas from example...{Colors.END}")
            subprocess.run(['cp', str(env_example), str(env_file)])
            print(f"{Colors.GREEN}✅ Environment file created{Colors.END}")
            print(f"{Colors.YELLOW}📝 Please edit .env.saas with your configuration{Colors.END}")
            return False
        else:
            print(f"{Colors.RED}❌ No environment configuration found{Colors.END}")
            return False
    
    print(f"{Colors.GREEN}✅ Environment configuration found{Colors.END}")
    return True


def start_development():
    """Start development server"""
    print(f"{Colors.BLUE}🔧 Starting development server...{Colors.END}")
    
    # Check if virtual environment exists
    venv_path = Path('venv')
    if not venv_path.exists():
        print(f"{Colors.YELLOW}📦 Creating virtual environment...{Colors.END}")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    
    # Install dependencies
    pip_cmd = 'venv/bin/pip' if os.name != 'nt' else 'venv\\Scripts\\pip.exe'
    python_cmd = 'venv/bin/python' if os.name != 'nt' else 'venv\\Scripts\\python.exe'
    
    print(f"{Colors.YELLOW}📦 Installing dependencies...{Colors.END}")
    subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'])
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_APP'] = 'src.saas_app:app'
    env['FLASK_ENV'] = 'development'
    env['PYTHONPATH'] = str(Path.cwd())
    
    # Start Flask development server
    print(f"{Colors.GREEN}🚀 Starting SaaS platform on http://localhost:5000{Colors.END}")
    subprocess.run([python_cmd, '-m', 'flask', 'run', '--host=0.0.0.0', '--port=5000'], env=env)


def start_production():
    """Start production deployment with Docker"""
    print(f"{Colors.BLUE}🐳 Starting production deployment...{Colors.END}")
    
    # Build and start services
    subprocess.run(['docker-compose', '-f', 'docker-compose.saas.yml', 'up', '--build', '-d'])
    
    print(f"{Colors.GREEN}✅ SaaS platform started successfully!{Colors.END}")
    print(f"""
{Colors.BLUE}📊 Service URLs:{Colors.END}
- SaaS Platform: http://localhost:5000
- Admin Dashboard: http://localhost:5000/admin
- Grafana Monitoring: http://localhost:3000
- Prometheus Metrics: http://localhost:9090

{Colors.YELLOW}📝 Next Steps:{Colors.END}
1. Create admin user: python launch_saas.py --create-admin
2. Access the platform at http://localhost:5000
3. Monitor services with Grafana at http://localhost:3000
""")


def stop_services():
    """Stop all services"""
    print(f"{Colors.YELLOW}🛑 Stopping SaaS platform...{Colors.END}")
    subprocess.run(['docker-compose', '-f', 'docker-compose.saas.yml', 'down'])
    print(f"{Colors.GREEN}✅ Services stopped{Colors.END}")


def create_admin_user():
    """Create admin user"""
    print(f"{Colors.BLUE}👤 Creating admin user...{Colors.END}")
    
    email = input("Admin email: ")
    password = input("Admin password: ")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    
    # Create admin user via Docker
    cmd = f"""
from src.saas_app import app
from src.auth.auth_manager import AuthManager
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
        print('Admin user created successfully')
    else:
        print(f'Error: {{error}}')
"""
    
    subprocess.run([
        'docker-compose', '-f', 'docker-compose.saas.yml', 
        'exec', 'saas-app', 'python', '-c', cmd
    ])


def show_logs():
    """Show service logs"""
    subprocess.run(['docker-compose', '-f', 'docker-compose.saas.yml', 'logs', '-f'])


def show_status():
    """Show service status"""
    subprocess.run(['docker-compose', '-f', 'docker-compose.saas.yml', 'ps'])


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='SaaS Trading Bot Platform Launcher')
    parser.add_argument('--dev', action='store_true', help='Start development server')
    parser.add_argument('--prod', action='store_true', help='Start production deployment')
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    parser.add_argument('--logs', action='store_true', help='Show service logs')
    parser.add_argument('--status', action='store_true', help='Show service status')
    parser.add_argument('--create-admin', action='store_true', help='Create admin user')
    parser.add_argument('--setup', action='store_true', help='Setup environment only')
    
    args = parser.parse_args()
    
    print_header()
    
    if args.setup:
        setup_environment()
        return
    
    if args.create_admin:
        create_admin_user()
        return
    
    if args.logs:
        show_logs()
        return
    
    if args.status:
        show_status()
        return
    
    if args.stop:
        stop_services()
        return
    
    # Check requirements
    if not check_requirements():
        print(f"{Colors.RED}❌ Please install missing requirements{Colors.END}")
        return
    
    # Setup environment
    if not setup_environment():
        print(f"{Colors.YELLOW}⚠️  Please configure .env.saas before starting{Colors.END}")
        return
    
    if args.dev:
        start_development()
    elif args.prod:
        start_production()
    else:
        # Interactive mode
        print(f"{Colors.BLUE}🎯 Choose deployment mode:{Colors.END}")
        print("1. Development (Flask dev server)")
        print("2. Production (Docker containers)")
        print("3. Setup environment only")
        print("4. Exit")
        
        choice = input(f"\n{Colors.YELLOW}Enter your choice (1-4): {Colors.END}")
        
        if choice == '1':
            start_development()
        elif choice == '2':
            start_production()
        elif choice == '3':
            setup_environment()
        elif choice == '4':
            print(f"{Colors.GREEN}👋 Goodbye!{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Invalid choice{Colors.END}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operation cancelled{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)
