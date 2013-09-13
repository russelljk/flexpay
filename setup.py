#!/usr/bin/env python

from setuptools import setup

setup(name='flexpay',
      version='0.1',
      description='A wrapper for the Amazon Flexible Payments (FPS) REST API.',
      author='Russell Kyle',
      author_email='russell.j.kyle@gmail.com',
      url='http://russellkyle.com/flexpay/',
      download_url='https://github.com/russelljk/flexpay/archive/master.tar.gz',
      packages=['flexpay'],
      include_package_data=True,
      keywords=['Amazon FPS', 'payments', 'e-commerc']
)