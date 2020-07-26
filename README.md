# Unroutine Server

This is the server code for the Unroutine app. The server generates new figure skating sequences using a genetic algorithm and produces accompanying audio clips.

## Getting Started

Running this code locally requires PostgreSQL: [Installation instructions](https://www.postgresql.org/docs/current/installation.html)

To run the server:
```
> pip install requirements.txt
> python manage.py migrate
> python manage.py runserver
```

