# -*- coding: utf-8 -*-
#
# setup.py for dumpanalyze
# Copyright 2017 IPONWEB Ltd. See License Notice in LICENSE
#

import re
from setuptools import setup


with open('requirements.txt') as fh:
    install_requires = fh.read().splitlines()


def version():
    pyfile = 'dumpanalyze/__init__.py'
    with open(pyfile) as fp:
        data = fp.read()

    match = re.search('__version__ = [\'\"](.+)[\'\"]', data)
    assert match, 'cannot find version in {}'.format(pyfile)
    return match.group(1)


setup(
    name='dumpanalyze',
    version=version(),
    description='Toolkit for processing LuaJIT plain text dumps',
    long_description=open('README.md').read(),
    author='Anton Soldatov',
    author_email='asoldatov@iponweb.net',
    license='MIT',
    # url='https://github.com/iponweb/dumpanalyze',
    packages=['dumpanalyze', 'dumpanalyze.view'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'dumpanalyze=dumpanalyze.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    keywords='luajit dump',
    setup_requires=['pytest-runner'],
    install_requires=install_requires,
    tests_require=['pytest', 'flake8'],
)
