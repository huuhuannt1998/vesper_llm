@echo off
echo Installing VESPER Smart Home Addon to Blender...

REM Set source and destination paths
set SOURCE_DIR=C:\Users\hbui11\Desktop\vesper_llm\blender\addons\vesper_smart_home
set DEST_DIR=C:\Users\hbui11\AppData\Roaming\UPBGE\Blender\4.4\scripts\addons\vesper_smart_home

REM Create destination directory if it doesn't exist
if not exist "%DEST_DIR%" (
    echo Creating addon directory...
    mkdir "%DEST_DIR%"
)

REM Copy the addon files
echo Copying addon files...
copy "%SOURCE_DIR%\__init__.py" "%DEST_DIR%\__init__.py"

REM Check if copy was successful
if exist "%DEST_DIR%\__init__.py" (
    echo ✅ Successfully installed VESPER Smart Home addon to Blender!
    echo.
    echo Next steps:
    echo 1. Open Blender/UPBGE
    echo 2. Go to Edit ^> Preferences ^> Add-ons
    echo 3. Search for "VESPER Smart Home Integration"
    echo 4. Enable the addon
    echo 5. Look for the VESPER tab in the 3D Viewport sidebar (press N)
    echo.
    echo Addon features:
    echo - Virtual device management (spawn, delete, control)
    echo - Sensor management (motion, item sensors)
    echo - Backend console API integration
    echo - Same functionality as web UI but in Blender
) else (
    echo ❌ Failed to copy addon files
    echo Check if source file exists: %SOURCE_DIR%\__init__.py
)

echo.
pause
