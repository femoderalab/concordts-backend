@echo off
echo 🚀 Starting custom build process...
echo 🐍 Python version: 
python --version
echo 📦 Pip version:
pip --version

echo 📦 Installing dependencies...
pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies
    exit /b %ERRORLEVEL%
)

echo ✅ Dependencies installed successfully

echo 🔍 Verifying critical packages...
python -c "
import sys
try:
    import setuptools
    print('✅ setuptools version: ' + setuptools.__version__)
    import drf_spectacular
    print('✅ drf_spectacular installed')
    import django
    print('✅ Django version: ' + django.get_version())
    print('✅ All critical packages verified')
except ImportError as e:
    print('❌ Import error: ' + str(e))
    sys.exit(1)
"

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Package verification failed
    exit /b %ERRORLEVEL%
)

echo 📦 Collecting static files...
python manage.py collectstatic --noinput

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to collect static files
    exit /b %ERRORLEVEL%
)

echo ✅ Build completed successfully!