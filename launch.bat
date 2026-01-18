@echo off
title TurboShells Launcher
echo.
echo  ====================================
echo   TurboShells Web - Quick Start
echo  ====================================
echo.

:: Start Backend (using venv python)
echo [1/3] Starting Python backend (port 8765)...
start "TurboShells Backend" cmd /k "cd /d c:\Github\TurboShells && .venv\Scripts\python -m uvicorn src.server.app:app --port 8765 --reload"

:: Wait for backend to initialize
echo [2/3] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [3/3] Starting Vite frontend (port 5173)...
start "TurboShells Frontend" cmd /k "cd /d c:\Github\TurboShells\web && npm run dev"

:: Wait for frontend to initialize
timeout /t 3 /nobreak >nul

:: Open Chrome
echo.
echo Opening Chrome...
start chrome http://localhost:5173

echo.
echo  ====================================
echo   🏁 TurboShells is running!
echo  ====================================
echo.
echo   Backend:  http://localhost:8765
echo   Frontend: http://localhost:5173
echo.
echo   Press any key to close this launcher.
echo   (Servers will keep running)
echo.
pause >nul
