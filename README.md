# Marketplace

A Flask-based marketplace web application with buyer and seller functionality.

## Prerequisites

- Python 3.12+
- PostgreSQL

## Setup & Run

### 1. Clone & Navigate
```bash
cd Marketplace
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root:
```bash
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/marketplace_db
SECRET_KEY=your_secret_key
```

### 5. Create the Database
```bash
psql -U postgres -c "CREATE DATABASE marketplace_db;"
```

### 6. Run Migrations
```bash
flask --app server.py db upgrade
```

### 7. Start the Server
```bash
flask --app server.py run
```

The app will be available at **http://127.0.0.1:5000**
