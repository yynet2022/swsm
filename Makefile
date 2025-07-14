

all:
	python manage.py makemigrations --no-color 
	python manage.py migrate --no-color

check:
	flake8 --exclude migrations euser/ || true
	flake8 --exclude migrations swsm/  || true
	flake8 contrib/  || true

clean:
	rm -f db.sqlite3 
	find . -type d -name __pycache__ | xargs rm -rf
	rm -f swsm/migrations/0*.py euser/migrations/0*.py
