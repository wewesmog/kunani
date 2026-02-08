# Setup Instructions

## Prerequisites
- Python 3.9+ installed
- PostgreSQL installed and running
- pip (usually comes with Python)

## Step 1: Create Virtual Environment

### Windows (PowerShell):
```powershell
python -m venv venv
```

### Windows (Command Prompt):
```cmd
python -m venv venv
```

### Alternative (if python doesn't work):
```powershell
py -m venv venv
# or
python3 -m venv venv
```

## Step 2: Activate Virtual Environment

### Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
```

### Windows (Git Bash):
```bash
source venv/Scripts/activate
```

## Step 3: Install Requirements

Once activated (you'll see `(venv)` in your prompt):
```bash
pip install -r requirements.txt
```

## Step 4: Set Up Database

1. Create database and user:
```bash
createdb kunani
createuser kunani_user
# Set password when prompted
```

2. Run schema:
```bash
psql -U kunani_user -d kunani -f db.sql
```

Or use the setup script:
```bash
python setup_db.py
```

## Step 5: Configure Environment

```bash
cp env.example .env
```

Edit `.env` with your:
- Database credentials
- OpenAI API key
- Langfuse keys (optional)

## Step 6: Run the Application

```bash
python main.py
```

## Troubleshooting

### Python not found:
- Make sure Python is installed and in PATH
- Try `py` instead of `python` on Windows
- Try `python3` if you have multiple Python versions

### Virtual environment activation fails:
- Make sure you're in the project directory
- Check that `venv` folder was created
- Try using full path: `D:\kunani\venv\Scripts\activate`

### Database connection errors:
- Verify PostgreSQL is running
- Check credentials in `.env`
- Ensure database and user exist

