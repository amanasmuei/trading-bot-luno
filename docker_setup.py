#!/usr/bin/env python3
"""
🐳 Luno Trading Bot - Docker Setup
=================================

Easy Docker deployment for the Luno Trading Bot.
Perfect for production environments and cloud deployment.
"""

import os
import sys
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Docker found: {result.stdout.strip()}{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Docker not found{Colors.END}")
            return False
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Docker not installed{Colors.END}")
        return False


def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Docker Compose found: {result.stdout.strip()}{Colors.END}")
            return True
        else:
            # Try legacy docker-compose
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Docker Compose (legacy) found: {result.stdout.strip()}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Docker Compose not found{Colors.END}")
                return False
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Docker Compose not installed{Colors.END}")
        return False


def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if env_file.exists():
        print(f"{Colors.GREEN}✅ Configuration file (.env) found{Colors.END}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠️  No .env file found{Colors.END}")
        print(f"{Colors.CYAN}💡 Run setup wizard first: python setup_wizard.py{Colors.END}")
        return False


def build_image():
    """Build the Docker image"""
    print(f"\n{Colors.BLUE}🔨 Building Docker image...{Colors.END}")
    
    try:
        result = subprocess.run([
            'docker', 'build', '-t', 'luno-trading-bot', '.'
        ], check=True)
        
        print(f"{Colors.GREEN}✅ Docker image built successfully{Colors.END}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to build Docker image: {e}{Colors.END}")
        return False


def run_container(dry_run=True):
    """Run the Docker container"""
    mode = "dry-run" if dry_run else "live"
    mode_text = "SIMULATION" if dry_run else "LIVE TRADING"
    
    print(f"\n{Colors.BLUE}🚀 Starting container in {mode_text} mode...{Colors.END}")
    
    try:
        cmd = ['docker', 'run', '-d', '--name', 'luno-trading-bot']
        cmd.extend(['-p', '5000:5000'])
        cmd.extend(['-v', f'{os.getcwd()}/logs:/app/logs'])
        cmd.extend(['-v', f'{os.getcwd()}/.env:/app/.env:ro'])
        cmd.extend(['--restart', 'unless-stopped'])
        cmd.append('luno-trading-bot')
        
        if dry_run:
            cmd.extend(['python', 'scripts/run_bot.py', '--dry-run'])
        else:
            cmd.extend(['python', 'scripts/run_bot.py'])
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        container_id = result.stdout.strip()
        
        print(f"{Colors.GREEN}✅ Container started successfully{Colors.END}")
        print(f"{Colors.CYAN}Container ID: {container_id[:12]}{Colors.END}")
        print(f"{Colors.CYAN}Dashboard: http://localhost:5000{Colors.END}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to start container: {e}{Colors.END}")
        return False


def run_with_compose(dry_run=True):
    """Run using Docker Compose"""
    print(f"\n{Colors.BLUE}🚀 Starting with Docker Compose...{Colors.END}")
    
    try:
        # Check which compose command to use
        compose_cmd = ['docker', 'compose']
        result = subprocess.run(compose_cmd + ['version'], capture_output=True)
        if result.returncode != 0:
            compose_cmd = ['docker-compose']
        
        # Start the services
        result = subprocess.run(compose_cmd + ['up', '-d'], check=True)
        
        print(f"{Colors.GREEN}✅ Services started successfully{Colors.END}")
        print(f"{Colors.CYAN}Dashboard: http://localhost:5000{Colors.END}")
        print(f"{Colors.CYAN}View logs: docker compose logs -f{Colors.END}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to start services: {e}{Colors.END}")
        return False


def stop_container():
    """Stop and remove the container"""
    print(f"\n{Colors.BLUE}🛑 Stopping container...{Colors.END}")
    
    try:
        subprocess.run(['docker', 'stop', 'luno-trading-bot'], check=True)
        subprocess.run(['docker', 'rm', 'luno-trading-bot'], check=True)
        print(f"{Colors.GREEN}✅ Container stopped and removed{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to stop container: {e}{Colors.END}")
        return False


def show_logs():
    """Show container logs"""
    print(f"\n{Colors.BLUE}📋 Container logs:{Colors.END}")
    
    try:
        subprocess.run(['docker', 'logs', '-f', 'luno-trading-bot'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Failed to show logs: {e}{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Log viewing stopped{Colors.END}")


def show_menu():
    """Show the main menu"""
    print(f"\n{Colors.WHITE}🐳 Docker Management Menu:{Colors.END}")
    print(f"  1. 🔨 Build Docker image")
    print(f"  2. 🎮 Start container (Simulation)")
    print(f"  3. 💰 Start container (Live Trading)")
    print(f"  4. 🚀 Start with Docker Compose")
    print(f"  5. 🛑 Stop container")
    print(f"  6. 📋 View logs")
    print(f"  7. 🔧 Setup configuration")
    print(f"  8. ❌ Exit")
    print()


def main():
    """Main Docker setup function"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("🐳 LUNO TRADING BOT - DOCKER SETUP")
    print("=" * 50)
    print(f"{Colors.END}")
    
    # Check prerequisites
    if not check_docker():
        print(f"\n{Colors.RED}Please install Docker first: https://docs.docker.com/get-docker/{Colors.END}")
        sys.exit(1)
    
    check_docker_compose()
    has_config = check_env_file()
    
    while True:
        show_menu()
        
        try:
            choice = input(f"{Colors.WHITE}Enter your choice (1-8): {Colors.END}").strip()
            
            if choice == "1":
                build_image()
                
            elif choice == "2":
                if not has_config:
                    print(f"{Colors.RED}❌ Please set up configuration first (option 7){Colors.END}")
                else:
                    run_container(dry_run=True)
                    
            elif choice == "3":
                if not has_config:
                    print(f"{Colors.RED}❌ Please set up configuration first (option 7){Colors.END}")
                else:
                    print(f"{Colors.RED}⚠️  WARNING: This will start live trading!{Colors.END}")
                    confirm = input("Are you sure? (yes/no): ").lower()
                    if confirm == "yes":
                        run_container(dry_run=False)
                    else:
                        print(f"{Colors.GREEN}✅ Cancelled for safety{Colors.END}")
                        
            elif choice == "4":
                if not has_config:
                    print(f"{Colors.RED}❌ Please set up configuration first (option 7){Colors.END}")
                else:
                    run_with_compose()
                    
            elif choice == "5":
                stop_container()
                
            elif choice == "6":
                show_logs()
                
            elif choice == "7":
                print(f"\n{Colors.BLUE}🔧 Running setup wizard...{Colors.END}")
                try:
                    subprocess.run([sys.executable, 'setup_wizard.py'], check=True)
                    has_config = check_env_file()
                except subprocess.CalledProcessError:
                    print(f"{Colors.RED}❌ Setup failed{Colors.END}")
                    
            elif choice == "8":
                print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.END}")
                break
                
            else:
                print(f"{Colors.YELLOW}⚠️  Invalid choice. Please enter 1-8.{Colors.END}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Goodbye!{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}")


if __name__ == "__main__":
    main()
