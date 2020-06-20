from setuptools import find_packages, setup

requires = [
    'flask',
    'authlib',
    'flask-login',
    'flask-migrate',
    'flask-sqlalchemy',
    'psycopg2',
    'requests',
    'python-dotenv',
]

setup(
    name='issueless',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={'test': ['pytest', 'coverage']},
)
