@echo off
echo Setting up FreelanceHub Application...
echo.
echo Installing required packages...
C:\Users\kolektif\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt
echo.
echo Setting up database with sample data...
C:\Users\kolektif\AppData\Local\Programs\Python\Python311\python.exe sample_data.py
echo.
echo Setup complete! You can now run start_freelancehub.bat to start the application.
echo.
pause 