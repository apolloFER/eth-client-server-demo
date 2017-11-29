from setuptools import setup

setup(
    name='Eth Python Project',
    packages=['eth'],
    version='0.0.1',
    description='Client and server implementaton of the Eth project',
    author='Darko Ronic',
    author_email='darko.ronic@gmail.com',
    install_requires=[
        'click',
        'requests',
        'PyMySQL',
        'redis',
        'SQLAlchemy'
    ],
    entry_points='''
        [console_scripts]
        eth=eth.cli:main

    ''',
)
