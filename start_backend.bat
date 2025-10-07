@echo off
echo Starting Lumbar X-ray Analyzer Backend with Gemini AI...
cd "C:\Users\my\OneDrive\Desktop\LUMBARANDVERTEBRAE\xray-medical-backend"

REM Activate virtual environment and start server
"C:\Users\my\OneDrive\Desktop\LUMBARANDVERTEBRAE\.venv\Scripts\python.exe" -c "import os; os.chdir('C:\\Users\\my\\OneDrive\\Desktop\\LUMBARANDVERTEBRAE\\xray-medical-backend'); import uvicorn; uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=False)"

pause