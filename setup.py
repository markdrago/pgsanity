from setuptools import setup

setup(
    name='pgsanity',
    version='0.2.9',
    author='Mark Drago',
    author_email='markdrago@gmail.com',
    url='http://github.com/markdrago/pgsanity',
    download_url='http://pypi.python.org/pypi/pgsanity',
    description='Check syntax of sql for PostgreSQL',
    license='MIT',
    packages=['pgsanity'],
    entry_points={
        'console_scripts': [
            'pgsanity = pgsanity.pgsanity:main'
        ]
    },
    test_suite='test',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'
    ],
    long_description="""
**PgSanity checks the syntax of Postgresql SQL files.**

It does this by leveraging the ecpg command which is traditionally
used for preparing C files with embedded sql for compilation.
However, as part of that preparation, ecpg checks the embedded SQL
statements for syntax errors using the exact same parser that is
in PostgreSQL.

So the approach that PgSanity takes is to take a file that has a
list of bare SQL in it, make that file look like a C file with
embedded SQL, run it through ecpg and let ecpg report on the syntax
errors of the SQL.
"""
)
