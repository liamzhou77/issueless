from setuptools import find_packages, setup

requires = [
    'flask',
    'authlib',
    'flask-bootstrap',
    'flask-login',
    'flask-migrate',
    'flask-principal',
    'flask-sqlalchemy',
    'flask-wtf',
    'psycopg2',
    'requests',
    'six',
    'python-dotenv',
]

setup(
    name='issue_tracker',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
