

all:
	python manage.py makemigrations --no-color 
	python manage.py migrate --no-color

check:
	flake8 euser/ | grep -v /migrations/ || true
	flake8 swsm/ | grep -v /migrations/ || true

clean:
	rm -f db.sqlite3 
	find . -type d -name __pycache__ | xargs rm -rf
	rm -f swsm/migrations/0*.py euser/migrations/0*.py
