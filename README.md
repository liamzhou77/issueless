## Issueless

A web application used to track project issues and bugs, built with Python, Flask, SQLAlchemy, PostgreSQL, Bootstrap 4, JavaScript, HTML/CSS.

https://issueless.herokuapp.com/

## Getting Started

### Installing Dependencies

#### Python 3.8

Follow instructions to install the latest version of python in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

Virtual environment is recommended whenever using Python for projects. This keeps dependencies for each project separate and organaized. Instructions for setting up a virual enviornment can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once virtual environment is setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages within the `requirements.txt` file.

##### Key Dependencies

-   [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

-   [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM used to handle database.

#### JavaScript Packages

Put all downloaded packages in `/issueless/static/packages` directory, including

-   [autosize](https://www.jacklmoore.com/autosize/)

-   [draggable](https://shopify.github.io/draggable/)

-   [dropzone](https://www.dropzonejs.com/)

-   [flatpickr](https://flatpickr.js.org/)

-   [list](https://listjs.com/)

-   [moment](https://momentjs.com/)

-   [prism](https://prismjs.com/)

-   [swap-animation](https://shopify.github.io/draggable/examples/swap-animation.html/)

-   [pipeline](https://pipeline.mediumra.re/)

## Configuration

Create your own `config.py` in `/issueless/instance` directory. Required configurations:

-   SQLALCHEMY_DATABASE_URI

-   AUTH0_CLIENT_SECRET

-   S3_ACCESS_KEY

-   S3_SECRET_KEY

-   S3_BUCKET_NAME

## Database Setup

Run the following commends:

```bash
flask db upgrade
flask insert-roles
```

## Running the server

First ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=issueless
export FLASK_ENV=development
flask run
```
