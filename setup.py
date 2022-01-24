from setuptools import find_packages, setup

setup(
    name='myapp',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-marshmallow',
        'Flask-Login',
        'Flask-SQLAlchemy',
        'marshmallow-sqlalchemy',
        'marshmallow',
        'pytest',
        'Werkzeug',
        'coverage',
        'webargs',
        'mysqlclient'
    ],
)