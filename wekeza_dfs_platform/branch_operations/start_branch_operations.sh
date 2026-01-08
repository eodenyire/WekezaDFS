#!/bin/bash
# Wekeza DFS Branch Operations System - Unix Startup Script

echo "========================================"
echo "🏦 Wekeza DFS Branch Operations System"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup.py first:"
    echo "   python3 setup.py"
    echo
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Check if main application exists
if [ ! -f "main_branch_system.py" ]; then
    echo "❌ Main application file not found!"
    echo "Please ensure you're in the correct directory."
    echo
    exit 1
fi

# Start the application
echo "🚀 Starting Branch Operations System..."
echo
echo "📍 Application will be available at:"
echo "   http://localhost:8501"
echo
echo "🔑 Default login credentials:"
echo "   Staff Code: SUP001"
echo "   Password: password123"
echo
echo "💡 Press Ctrl+C to stop the application"
echo "========================================"
echo

# Start Streamlit application
streamlit run main_branch_system.py --server.port 8501

# If we get here, the application has stopped
echo
echo "🛑 Application stopped."