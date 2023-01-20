If(!(Test-Path -Path venv)){
    python -m venv venv
}
$Env:FLASK_APP = "app/__init__.py"
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
./venv/Scripts/Activate.ps1
pip3 install -r requirements.txt
python ./setup.py
flask run --host=0.0.0.0