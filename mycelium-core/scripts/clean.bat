@echo off
REM ============================================================
REM MYCELIUM CORE - Project deep clean (Windows CMD)
REM ============================================================
REM Удаляет: chain-data, logs, exports, runtime, build, dist,
REM          __pycache__, .pytest_cache, *.spec, ABI артефакты
REM Не трогает: .env, app.cfg, исходный код, тесты
REM ============================================================

setlocal enabledelayedexpansion

cd /d "%~dp0\.."

echo.
echo ============================================================
echo   MYCELIUM CORE - Project Clean
echo   Working dir: %CD%
echo ============================================================
echo.
echo  WARNING: this will delete:
echo    - data\chain-data\ (blockchain state)
echo    - data\logs\       (all session logs)
echo    - data\exports\    (exported JSON/CSV)
echo    - data\runtime\    (cache)
echo    - build\           (PyInstaller temp)
echo    - dist\            (built EXE)
echo    - contracts\abi\   (compiled contract artifacts)
echo    - All __pycache__\ folders
echo    - All .pytest_cache, .mypy_cache folders
echo    - *.spec files
echo.
echo  WILL NOT TOUCH:
echo    - .env, app.cfg (your config)
echo    - src\, contracts\VotingCore.sol (source code)
echo    - tests\ (tests)
echo    - bin\geth.exe (binary)
echo.

set /p CONFIRM="Continue? [y/N]: "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.
echo Cleaning...
echo ------------------------------------------------------------

REM Removing folders
for %%D in (
    "data\chain-data\active"
    "data\chain-data\archives"
    "data\logs\active"
    "data\logs\archive"
    "data\exports"
    "data\runtime"
    "build"
    "dist"
    "contracts\abi"
    ".pytest_cache"
) do (
    if exist %%D (
        rmdir /s /q %%D 2>nul
        if exist %%D (
            echo   [FAIL] %%D - locked or in use
        ) else (
            echo   [OK]   %%D
        )
    )
)

REM Removing __pycache__ recursively
echo   Searching __pycache__...
set /a PYCACHE_COUNT=0
for /f "delims=" %%P in ('dir /s /b /ad __pycache__ 2^>nul') do (
    rmdir /s /q "%%P" 2>nul
    set /a PYCACHE_COUNT+=1
)
echo   [OK]   Removed !PYCACHE_COUNT! __pycache__ folders

REM Removing .mypy_cache recursively
for /f "delims=" %%P in ('dir /s /b /ad .mypy_cache 2^>nul') do (
    rmdir /s /q "%%P" 2>nul
)

REM Removing *.spec files in root
for %%F in (*.spec) do (
    del /q "%%F" 2>nul
    echo   [OK]   %%F
)

REM Removing .pyc files
for /r %%F in (*.pyc) do (
    del /q "%%F" 2>nul
)

echo ------------------------------------------------------------
echo.
echo Done!
echo.
echo To start fresh:
echo   1. python main.py
echo   2. Deploy contract again
echo.

endlocal
pause