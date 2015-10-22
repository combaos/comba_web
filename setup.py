__author__ = 'michel'
from setuptools import setup

setup(name='comba_web',
      version='0.1',
      description='The Comba web main module',
      url='https://gitlab.janguo.de/comba/comba_web',
      author='Michael Liebler',
      author_email='michael-liebler@janguo.de',
      license='GPLv3',
      packages=['comba_web','comba_web_api','comba_web_monitor','comba_web_programme'],
      zip_safe=False)
