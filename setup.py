from setuptools import setup, find_packages

setup(
    name='mess',
    version='0.1',
    discription='A small framework for message triggered jobs',
    url='http://github.com/dimakuz/mess',
    author='Dima Kuznetsov',
    author_email='dmitrykuzn@gmail.com',
    license='GPLv2',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: System :: Distributed Computing',
        'Programming Language :: Python :: 2.7',
    ],
    packages=['mess'],
    install_requires=['gevent', 'sqlalchemy'],
    extras_require={
        'test': 'pytest',
    },
)
