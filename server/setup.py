from setuptools import setup, find_packages

reqs = [
    'arrow',
    'apache-airflow',
    'click',
    'daiquiri',
    'Faker',
    'flask',
    'flask_jwt_extended',
    'gunicorn',
    'kml2geojson',
    'matplotlib',
    'networkx',
    'pandas',
    'psycopg2-binary',
    'pyyaml',
    'requests',
    'uszipcode',
    'uuid',
    'xkcdpass',
    'xlrd'
]

test_reqs = [
    'ipython',
    'pytest',
    'pytest-cov',
    'pylint',
    'pytest-sugar'
]

setup(
    name='shir_connect',
    description='Analytics in support of community engagement',
    author='Fiddler Analytics',
    author_email='info@fiddleranalytics.com',
    packages=find_packages(),
    version='0.1.1',
    install_requires=reqs,
    extras_require={
        'test': test_reqs
    },
    entry_points = {
        'console_scripts':'shir_connect=shir_connect.__main__:main'
    }
)
