@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete! To run the application:
echo 1. Edit .env with your API keys
echo 2. Start Backend: uvicorn backend.main:app --reload
echo 3. Start Frontend: streamlit run frontend/app.py
pause
