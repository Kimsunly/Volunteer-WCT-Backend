#!/bin/bash

# ============================================
# Admin Backend - Startup Script
# ============================================

echo "🚀 Starting Admin Backend Setup..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the Backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found${NC}"
    echo "Please run this script from the Backend directory:"
    echo "  cd Backend"
    echo "  ./start_backend.sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found Backend directory"

# Step 1: Check Python
echo ""
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installed: $PYTHON_VERSION"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Step 2: Check/Create Virtual Environment
echo ""
echo "Step 2: Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Step 3: Install Dependencies
echo ""
echo "Step 3: Installing dependencies..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt --quiet
echo -e "${GREEN}✓${NC} Dependencies installed"

# Step 4: Check Environment Variables
echo ""
echo "Step 4: Checking environment variables..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo ""
    echo "Creating .env template..."
    cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Application Settings
APP_NAME=Volunteer Web Admin API
VERSION=1.0.0
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
EOF
    echo -e "${YELLOW}⚠️  Please edit .env file with your Supabase credentials${NC}"
    echo ""
    echo "To get your Supabase credentials:"
    echo "  1. Go to https://supabase.com/dashboard"
    echo "  2. Select your project"
    echo "  3. Go to Settings > API"
    echo "  4. Copy:"
    echo "     - Project URL → SUPABASE_URL"
    echo "     - service_role key → SUPABASE_KEY"
    echo "     - JWT Secret → SUPABASE_JWT_SECRET"
    echo ""
    echo "After updating .env, run this script again!"
    exit 1
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Step 5: Check if Database Migration is Done
echo ""
echo "Step 5: Database setup check..."
echo -e "${YELLOW}ℹ️  Have you run the database migration?${NC}"
echo ""
echo "If not, please:"
echo "  1. Open Supabase SQL Editor"
echo "  2. Execute: database_migration_admin.sql"
echo ""
read -p "Press Enter to continue (or Ctrl+C to exit and run migration first)..."

# Step 6: Start the Server
echo ""
echo "Step 6: Starting FastAPI server..."
echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 Admin Backend Starting...${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo "Server will be available at:"
echo "  • http://localhost:8000"
echo "  • http://127.0.0.1:8000"
echo ""
echo "API Documentation:"
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo ""
echo "Health Check:"
echo "  • http://localhost:8000/health"
echo ""
echo "Admin Endpoints:"
echo "  • http://localhost:8000/admin/metrics"
echo "  • http://localhost:8000/admin/organizers"
echo "  • http://localhost:8000/admin/categories"
echo "  • ... and 25 more endpoints"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo "════════════════════════════════════════════"
echo ""

# Start uvicorn using the virtual environment's Python
.venv/bin/uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
