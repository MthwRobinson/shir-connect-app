from setuptools import setup, find_packages

reqs = [
    'click',
    'daiquiri',
    'flask',
    'gunicorn',
    'pandas',
    'psycopg2',
    'uuid'
]

test_reqs = ['pytest', 'pytest-sugar', 'pytest-cov', 'pylint']

setup(
    name='trs_dashboard',
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
        'console_scripts':'trs_dashboard=trs_dashboard.__main__:main'
    }
)
