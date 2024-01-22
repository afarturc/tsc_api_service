# Tower Sections Catalogue API service

Tower sections are the main object of this service. They consist of a series of shells assembled vertically.

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
