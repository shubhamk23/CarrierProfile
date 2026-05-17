#!/usr/bin/env python3
"""
Deployment Validation Script for Career Profile Backend
Validates database connectivity, environment variables, and deployment readiness
"""

import os
import sys
import asyncio
from urllib.parse import urlparse
import socket
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed")


class DeploymentValidator:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []

    def add_result(self, status: str, message: str):
        """Add validation result"""
        symbol = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
        self.results.append(f"{symbol} {message}")
        if status == "fail":
            self.errors.append(message)
        elif status == "warn":
            self.warnings.append(message)

    def validate_env_file(self):
        """Check if .env file exists and contains required variables"""
        print("\n📋 Validating Environment Configuration...")
        print("=" * 60)

        env_path = Path(__file__).parent / ".env"
        if not env_path.exists():
            self.add_result("fail", ".env file not found")
            return False

        self.add_result("pass", ".env file exists")

        # Check required environment variables
        required_vars = ["DATABASE_URL"]
        optional_vars = ["SECRET_KEY", "ALLOWED_ORIGINS"]

        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mask password in DATABASE_URL
                if var == "DATABASE_URL" and "@" in value:
                    parts = value.split("@")
                    masked = f"{parts[0].split(':')[0]}://***:***@{parts[1]}"
                    self.add_result("pass", f"{var} is set: {masked}")
                else:
                    self.add_result("pass", f"{var} is set")
            else:
                self.add_result("fail", f"{var} is not set")

        for var in optional_vars:
            value = os.getenv(var)
            if value:
                self.add_result("pass", f"{var} is set")
            else:
                self.add_result("warn", f"{var} is not set (optional)")

        return True

    def validate_database_url(self):
        """Validate DATABASE_URL format and connectivity"""
        print("\n🗄️  Validating Database Configuration...")
        print("=" * 60)

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            self.add_result("fail", "DATABASE_URL not set")
            return False

        # Parse URL
        try:
            parsed = urlparse(db_url)
            self.add_result("pass", f"Database URL format is valid")

            # Check components
            if parsed.scheme not in ["postgresql", "postgresql+asyncpg"]:
                self.add_result("fail", f"Invalid database scheme: {parsed.scheme}")
            else:
                self.add_result("pass", f"Database scheme: {parsed.scheme}")

            if parsed.hostname:
                self.add_result("pass", f"Database host: {parsed.hostname}")

                # Test DNS resolution
                try:
                    socket.gethostbyname(parsed.hostname)
                    self.add_result("pass", f"Database host is reachable (DNS resolved)")
                except socket.gaierror:
                    self.add_result("fail", f"Cannot resolve database host: {parsed.hostname}")
                    self.add_result("warn", "This could mean:")
                    self.add_result("warn", "  1. Supabase project ID is incorrect")
                    self.add_result("warn", "  2. Supabase database is paused or deleted")
                    self.add_result("warn", "  3. Network connectivity issue")
            else:
                self.add_result("fail", "Database host not specified")

            if parsed.port:
                self.add_result("pass", f"Database port: {parsed.port}")
            else:
                self.add_result("warn", "Database port not specified (will use default)")

            if parsed.path and parsed.path != "/":
                db_name = parsed.path.lstrip("/")
                self.add_result("pass", f"Database name: {db_name}")
            else:
                self.add_result("warn", "Database name not specified")

        except Exception as e:
            self.add_result("fail", f"Invalid DATABASE_URL format: {str(e)}")
            return False

        return True

    async def test_database_connection(self):
        """Test actual database connection"""
        print("\n🔌 Testing Database Connection...")
        print("=" * 60)

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            self.add_result("fail", "DATABASE_URL not set, skipping connection test")
            return False

        try:
            # Try to import SQLAlchemy
            from sqlalchemy import create_engine, text
            from sqlalchemy.exc import OperationalError

            # For sync connection test (needed for alembic)
            sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

            try:
                engine = create_engine(sync_url)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    self.add_result("pass", "Database connection successful")

                    # Check if tables exist
                    result = conn.execute(text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public'"
                    ))
                    tables = [row[0] for row in result]

                    if tables:
                        self.add_result("pass", f"Found {len(tables)} table(s): {', '.join(tables)}")
                    else:
                        self.add_result("warn", "No tables found - migrations may not have run")

                engine.dispose()
                return True

            except OperationalError as e:
                self.add_result("fail", f"Database connection failed: {str(e)}")
                return False

        except ImportError:
            self.add_result("warn", "SQLAlchemy not installed, skipping connection test")
            return False

    def validate_alembic_setup(self):
        """Validate Alembic migration setup"""
        print("\n🔄 Validating Database Migrations...")
        print("=" * 60)

        alembic_dir = Path(__file__).parent / "alembic"
        if not alembic_dir.exists():
            self.add_result("fail", "Alembic directory not found")
            return False

        self.add_result("pass", "Alembic directory exists")

        # Check for alembic.ini
        alembic_ini = Path(__file__).parent / "alembic.ini"
        if alembic_ini.exists():
            self.add_result("pass", "alembic.ini file exists")
        else:
            self.add_result("fail", "alembic.ini file not found")

        # Check for migrations
        versions_dir = alembic_dir / "versions"
        if versions_dir.exists():
            migrations = list(versions_dir.glob("*.py"))
            if migrations:
                self.add_result("pass", f"Found {len(migrations)} migration(s)")
            else:
                self.add_result("warn", "No migrations found")
        else:
            self.add_result("fail", "Alembic versions directory not found")

        return True

    def validate_deployment_files(self):
        """Validate deployment configuration files"""
        print("\n📦 Validating Deployment Files...")
        print("=" * 60)

        # Check for vercel.json
        vercel_json = Path(__file__).parent / "vercel.json"
        if vercel_json.exists():
            self.add_result("pass", "vercel.json exists")
        else:
            self.add_result("warn", "vercel.json not found (may not be needed)")

        # Check for requirements.txt
        requirements = Path(__file__).parent / "requirements.txt"
        if requirements.exists():
            self.add_result("pass", "requirements.txt exists")
        else:
            self.add_result("fail", "requirements.txt not found")

        # Check for api/index.py (Vercel serverless entry point)
        api_index = Path(__file__).parent / "api" / "index.py"
        if api_index.exists():
            self.add_result("pass", "api/index.py exists (Vercel entry point)")
        else:
            self.add_result("warn", "api/index.py not found")

        return True

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        for result in self.results:
            print(result)

        print("\n" + "=" * 60)
        print(f"Total Checks: {len(self.results)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")

        if not self.errors:
            print("\n✅ All critical checks passed!")
        else:
            print("\n❌ Some critical checks failed. Please address the errors above.")

        print("=" * 60 + "\n")

    async def run_all_validations(self):
        """Run all validation checks"""
        print("\n" + "=" * 60)
        print("🚀 CAREER PROFILE BACKEND - DEPLOYMENT VALIDATION")
        print("=" * 60)

        self.validate_env_file()
        self.validate_database_url()
        await self.test_database_connection()
        self.validate_alembic_setup()
        self.validate_deployment_files()

        self.print_summary()

        return len(self.errors) == 0


async def main():
    """Main validation entry point"""
    validator = DeploymentValidator()
    success = await validator.run_all_validations()

    if success:
        print("✅ Deployment validation completed successfully!")
        print("Next steps:")
        print("  1. Run: alembic upgrade head (to create database tables)")
        print("  2. Deploy to Vercel: vercel --prod")
        print("  3. Set environment variables in Vercel dashboard")
        return 0
    else:
        print("❌ Deployment validation failed!")
        print("Please fix the errors above before deploying.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
