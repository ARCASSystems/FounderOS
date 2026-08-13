@echo off
rem Start Founder OS - double-click this file to begin (Windows).
rem
rem What it does: opens Claude Code in this folder. On a fresh install it
rem starts the setup wizard for you; after that it just opens your OS.
rem It installs nothing and sends nothing anywhere.
rem
rem If Windows showed a security warning before running this: that is normal
rem for a downloaded script. This file is plain text - right-click it and
rem choose Edit to read everything it does.

setlocal
cd /d "%~dp0"
title Founder OS

rem -- Is Claude Code installed?
where claude >nul 2>nul
if errorlevel 1 goto no_claude

rem -- Early heads-up only: Python 3.11+ check. The setup wizard runs the
rem -- real preflight; this just saves you a surprise twenty minutes in.
set "PY_OK="
python -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 set "PY_OK=1"
if not defined PY_OK (
  python3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
  if not errorlevel 1 set "PY_OK=1"
)
if not defined PY_OK (
  py -3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
  if not errorlevel 1 set "PY_OK=1"
)
if not defined PY_OK (
  echo One heads-up: Python 3.11 or newer was not found on this machine.
  echo Founder OS scripts need it. Free download: https://www.python.org/downloads/
  echo In the installer, tick "Add python.exe to PATH".
  echo You can continue now - the setup wizard will remind you before it starts.
  echo.
)

rem -- A finished OS opens. An interrupted setup resumes where it stopped.
rem -- A fresh install starts the wizard. The completion marker is written by
rem -- setup only after its final health check, so an identity file alone is
rem -- no longer read as "setup finished" - it lands five phases early. An
rem -- install set up before the markers existed has identity and neither
rem -- marker; it opens normally, exactly as it always has.
if exist "state\setup-complete.json" (
  claude
) else (
  if exist "state\setup-progress.json" (
    claude "continue Founder OS setup where it left off"
  ) else (
    if exist "core\identity.md" (
      claude
    ) else (
      claude "set up Founder OS"
    )
  )
)
goto :eof

:no_claude
echo.
echo Claude Code is not installed yet - the free app Founder OS runs inside.
echo.
echo   1. Download it at https://claude.ai/code  (opening that page now)
echo   2. Install it and sign in with your Claude account (Pro or Max plan)
echo   3. Double-click this file again
echo.
start "" "https://claude.ai/code"
pause
