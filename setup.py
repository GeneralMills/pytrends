
import io
import os.path
from setuptools import setup

here = os.path.abspath(path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytrends',
    version='0.1.0',
    description='Pseudo API for Google Trends',
    long_description=long_description,
    url='https://github.com/dreyco676/pytrends',
    author='John Hogue',
    author_email='abc@xyz',  # TODO
    license='MIT',  # TODO
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'  ## TODO
        ],
    keywords='google trends pseudo-API',
    packages=['pytrends'],
)
