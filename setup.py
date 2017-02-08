# coding: utf-8

from setuptools import setup, find_packages

readme = open('README').read()

setup(
    name='starmachine',
    version='${version}',
    description=readme.partition('\n')[0],
    author='zhenchaozhu',
    author_email='zhenchaozhu@outlook.com',
    url='',
    packages=find_packages(exclude=['*.pyc']),
    include_package_data=True,
    install_requires=[
        'tornado>=3.1',
        'redis>=2.10',
        'torndb>=0.3',
        'MySQL-python>=1.2.3',
        'pyOpenSSL==0.14',
        'oss>=0.1.3',
        'rq>=0.5.1',
        'beautifulsoup4>=4.3.2',
        'requests',
        'qiniu',
        'xlrd',
        'pycrypto',
        'apscheduler',
    ],
    entry_points={
        'console_scripts': [
            'starmachine = starmachine.server:run'
        ]
    }
)