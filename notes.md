# Test Results Dashboard admin notes

## Setup the project

https://www.djangoproject.com/start/

```
pip install Django
```

From within project folder:
```
django-admin startproject dash
cd dash
python manage.py runserver
```

then from same dir as manage.py:
```
python manage.py startapp results
```

Enusre in settings.py
```
TIME_ZONE = 'UTC'
```

## Model Updates

Check if migration needed or other problem:
```
python manage.py check
```

If a migration needed:
```
python manage.py makemigrations results
```

Optional step - view what will change
```
python manage.py sqlmigrate results 0001
```

Finally, do the migration:
```
python manage.py migrate
```

If the database becomes corrupted, delete and start over: https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

## To manage Django and DB:
```
python manage.py shell
```

Create admin user and testing password

## Test Reference
https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing
https://realpython.com/blog/python/testing-in-django-part-1-best-practices-and-examples/ (coverage)
http://toastdriven.com/blog/2011/apr/10/guide-to-testing-in-django/
https://dezoito.github.io/2015/09/21/how-to-test-django-applications_pt1.html (Selenium)


## Test Client from shell

```
from django.test.utils import setup_test_environment
setup_test_environment()

rom django.test import Client
client = Client()
```

Use it:
```
response = client.get('/')
response.status_code

from django.urls import reverse
response = client.get(reverse('polls:index'))

response.status_code
response.content
response.context['latest_question_list']
```

## SQLite3

### View tables

```
import sqlite3
con = sqlite3.connect('database.db')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
```

### View columns

```
cursor = con.execute('select * from polls_question')
names = list(map(lambda x: x[0], cursor.description))
names
```

## Reference:

MongoDB with Django
* http://www.chrisumbel.com/article/django_python_mongodb_engine_mongo
* https://django-mongodb-engine.readthedocs.io/en/latest/
* https://staltz.com/djangoconfi-mongoengine/#/
* https://medium.com/@vasjaforutube/django-mongodb-django-rest-framework-mongoengine-ee4eb5857b9a
* https://www.ibm.com/developerworks/library/os-django-mongo/
