from setuptools import setup, find_packages

reqs = [
    'arrow',
    'click',
    'daiquiri',
    'flask',
    'flask_jwt_extended',
    'gunicorn',
    'pandas',
    'psycopg2-binary',
    'requests',
    'uuid',
    'xkcdpass',
    'xlrd'
]

test_reqs = ['pytest', 'pytest-sugar', 'pytest-cov', 'pylint']

setup(
    name='shir_connect',
    description='etl pipeline and dashboard for temple rodef shalom',
    author='Temple Rodef Shalom',
    author_email='nsmuckler@templerodefshalom.org',
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
