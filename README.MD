
# Medical clinic site - backend

Project contains medical clinic site backend in django.

There are two types of accounts and their relationships, doctor and patient. Making appointments - choosing a doctor of the day and time. History and appointments. Private chat between doctor and patient. Home page with announcements available without logging in.

To do:

Visit notes

Doctor's evaluation after the visit + comments
## Deployment

To deploy this project run:

```bash
  pip install -r requirements.txt
  python manage.py makemigrations
  python manage.py migrate --run-syncdb
  python manage.py runserver
```

