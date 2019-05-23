import setuptools

from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version = '0.1.2'

setuptools.setup(
    name='airflow-workflows',
    packages=setuptools.find_packages(),
    version=version,
    license='apache-2.0',
    description='Provides a powerful, Django-inspired class-based DAG syntax for Apache Airflow.',
    long_description=long_description,
    author='Max Goodridge',
    author_email='max.goodridge@hotmail.co.uk',
    url='https://github.com/maxg203/airflow-workflows',
    download_url='https://github.com/maxg203/airflow-workflows/archive/{}.tar.gz'.format(version),
    keywords=['airflow', 'DAG', 'workflows', 'ETL'],
    install_requires=['apache-airflow'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    long_description_content_type='text/markdown',
)
