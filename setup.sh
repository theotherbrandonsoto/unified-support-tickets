#!/bin/bash
# setup.sh - Unified Support Tickets Project Setup Script
# Automates the entire setup process in one command
# Usage: bash setup.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║        🚀 Unified Support Tickets - Automated Setup                        ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check Python
echo "📋 Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ Found $PYTHON_VERSION"
echo ""

# Step 2: Create virtual environment
echo "📋 Step 2: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Step 3: Activate virtual environment
echo "📋 Step 3: Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 4: Install dependencies
echo "📋 Step 4: Installing dependencies from requirements.txt..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Step 5: Check if database exists, if not generate it
echo "📋 Step 5: Setting up database..."
if [ ! -f "unified_support_tickets.duckdb" ]; then
    echo "   Generating synthetic data..."
    python3 generate_raw_data.py
    echo "✅ Synthetic data generated (7,000 tickets)"
else
    echo "✅ Database already exists"
fi
echo ""

# Step 6: Initialize dbt and run models
echo "📋 Step 6: Building data pipeline with dbt..."
dbt seed --profiles-dir . -q --no-partial-parse
dbt run --profiles-dir . -q --no-partial-parse
echo "✅ Data pipeline complete"
echo ""

# Step 7: Verify setup
echo "📋 Step 7: Verifying setup..."
TICKET_COUNT=$(python3 -c "import duckdb; print(duckdb.connect('unified_support_tickets.duckdb', read_only=True).execute('SELECT COUNT(*) FROM main_mart.fct_unified_support_tickets').fetchall()[0][0])")
echo "✅ Unified fact table has $TICKET_COUNT tickets"
echo ""

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                                      ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Start the MCP server (for Claude Desktop):"
echo "   python mcp_server.py"
echo ""
echo "2. Query the metrics directly in Python:"
echo "   python3 -c \"import duckdb; conn = duckdb.connect('unified_support_tickets.duckdb'); print(conn.execute('SELECT COUNT(*) FROM main_mart.fct_unified_support_tickets').df())\""
echo ""
echo "3. Or run dbt commands:"
echo "   dbt run --profiles-dir ."
echo "   dbt test --profiles-dir ."
echo ""
echo "📚 For more info, see:"
echo "   - README.md           - Full documentation"
echo "   - QUICKSTART.md       - Quick setup guide"
echo "   - MCP_SETUP.md        - Claude Desktop integration"
echo ""
