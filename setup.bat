@echo off
REM setup.bat - Unified Support Tickets Project Setup Script (Windows)
REM Automates the entire setup process in one command
REM Usage: setup.bat

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║        🚀 Unified Support Tickets - Automated Setup (Windows)              ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check Python
echo 📋 Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found %PYTHON_VERSION%
echo.

REM Step 2: Create virtual environment
echo 📋 Step 2: Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Step 3: Activate virtual environment
echo 📋 Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Step 4: Install dependencies
echo 📋 Step 4: Installing dependencies from requirements.txt...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt -q
echo ✅ Dependencies installed
echo.

REM Step 5: Check if database exists
echo 📋 Step 5: Setting up database...
if not exist "unified_support_tickets.duckdb" (
    echo    Generating synthetic data...
    python generate_raw_data.py
    echo ✅ Synthetic data generated (7,000 tickets)
) else (
    echo ✅ Database already exists
)
echo.

REM Step 6: Initialize dbt and run models
echo 📋 Step 6: Building data pipeline with dbt...
dbt seed --profiles-dir . -q --no-partial-parse
dbt run --profiles-dir . -q --no-partial-parse
echo ✅ Data pipeline complete
echo.

REM Step 7: Verify setup
echo 📋 Step 7: Verifying setup...
python -c "import duckdb; conn = duckdb.connect('unified_support_tickets.duckdb', read_only=True); print(f'✅ Setup verified: {conn.execute(\"SELECT COUNT(*) FROM main_mart.fct_unified_support_tickets\").fetchall()[0][0]} tickets in unified table')"
echo.

echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                    ✅ SETUP COMPLETE!                                      ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🚀 NEXT STEPS:
echo.
echo 1. Start the MCP server (for Claude Desktop):
echo    python mcp_server.py
echo.
echo 2. Or query the metrics directly in Python:
echo    python -c "import duckdb; conn = duckdb.connect('unified_support_tickets.duckdb'); print(conn.execute('SELECT COUNT(*) FROM main_mart.fct_unified_support_tickets').df())"
echo.
echo 3. Or run dbt commands:
echo    dbt run --profiles-dir .
echo    dbt test --profiles-dir .
echo.
echo 📚 For more info, see:
echo    - README.md           - Full documentation
echo    - QUICKSTART.md       - Quick setup guide
echo    - MCP_SETUP.md        - Claude Desktop integration
echo.
pause
