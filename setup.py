import os
import io
from setuptools import setup

dir = os.path.dirname(__file__)

with io.open(os.path.join(dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytrends',
    version='3.1.0',
    description='Pseudo API for Google Trends',
    long_description=long_description,
    url='https://github.com/dreyco676/pytrends',
    author=['John Hogue', 'Burton DeWilde'],
    author_email='dreyco676@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License'
        ],
    install_requires=["requests", "BeautifulSoup4", "pandas", 'lxml'],
    keywords='google trends api search',
    packages=['pytrends'],
)
