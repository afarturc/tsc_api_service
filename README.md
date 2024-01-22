# Tower Sections Catalogue API service

Tower sections are the main object of this service. They consist of a series of shells assembled vertically.

## Development

This service was developed using FastAPI, a modern web framework for building Python APIs. This was decided because of the requirements of the service and previous knowladge of the framework.\
The project was organized using the recommended FastAPI folder structure, described in the documentation:

```
.
├── Dockerfile
├── README.md
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── database.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   └── sql_app.db
└── tests
    ├── __init__.py
    ├── sql_app.db
    └── test_services.py
```

The database used was SQLite with two instances, one for development and the other for tests.\
All the API documentation can be found after running the project using FastAPI OpenAPI automatic UI documentation, where the models, endpoints and constraints are described.

## How to run

### Docker

Requirements:
- Have Docker installed [Docker Desktop recommended](https://www.docker.com/products/docker-desktop/)

Build the image:

```
docker build -t tsc .
```

Create and run the container:

```
docker run -d --name tsc_api_service -p 80:80 tsc
```

With the server up check the documentation at:
- [Documentation](http://localhost/docs)

### Local

Requirements:
- Have python installed [Version 3.10.12 recommended](https://www.python.org/downloads/release/python-31012/)

Create a new python virtual environment:

```
python3 -m venv env
```

Activate the environment:

```
source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Run the server:

```
uvicorn src.main:app --reload
```

With the server up check the documentation at:
- [Documentation](http://127.0.0.1:8000/docs)
