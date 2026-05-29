@echo off
echo ?? Starting HinglishMind...

echo.
echo [1/2] Starting Flask API Server...
start "HinglishMind API" cmd /k "cd api && python app.py"

timeout /t 3 /nobreak > nul

echo.
echo [2/2] Starting Gradio Web Interface...
start "HinglishMind Web" cmd /k "cd api && python gradio_app.py"

echo.
echo ? HinglishMind is starting!
echo ?? Web Interface will open at: http://127.0.0.1:7860
echo ?? API running at: http://127.0.0.1:5000
echo.
echo Press any key to close this window (servers will keep running)
pause > nul
