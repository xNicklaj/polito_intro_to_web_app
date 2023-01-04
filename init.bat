pip3 install -r requirements.txt
cd app\db
sqlite3 App.db ".read init.sql"
cd ..\static
mkdir audio
mkdir images
mkdir tmp
cd ..\..\
set FLASK_APP=app\__init__.py
flask run --host=0.0.0.0