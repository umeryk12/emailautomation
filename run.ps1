# PowerShell script to run the Flask app
$env:SECRET_KEY="c987a5b4b8680ef773a4ea2593b5338e568f9b4da253f96652b39d8e8103e63e"
$env:FLASK_ENV="development"
Write-Host "Starting Email Automation Website..."
Write-Host "Open your browser to: http://localhost:5000"
Write-Host ""
python app.py

