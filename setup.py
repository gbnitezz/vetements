from setuptools import setup

setup(
    name='vetementsFindFinal',
    version='1.0',
    packages=['vetementsFindFinal'],
    include_package_data=True,
    install_requires=[
        'Flask',
        'requests',
        'beautifulsoup4',
        'ebaysdk',
        'pyVinted',
        'selenium'
    ],
)