#!/bin/bash

echo "=== Korean Study App Starter ==="

# Check for python
if ! command -v python3 &> /dev/null
then
    echo "Python3 tidak ditemukan. Silakan install python3 terlebih dahulu."
    exit
fi

# Install requirements
echo "Checking dependencies..."
pip install -r requirements.txt --quiet

# Initialize database if not exists
if [ ! -f "database.db" ]; then
    echo "Initializing database..."
    python3 init_db.py
fi

# Run app
echo "Aplikasi berjalan di http://localhost:5000"
python3 app.py
