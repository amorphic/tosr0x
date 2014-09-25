from setuptools import setup, find_packages

setup(
    name='tosr0x',
    version='0.2.0',
    author='James Stewart',
    author_email='jstewart101@gmail.com',
    url='https://github.com/amorphic/tosr0x',
    py_modules=['tosr0x'],
    description='An interface to tinysine.com tosr0x relay modules.',
    long_description=open('README.md').read()
    install_requires=[
        'pyserial>=2.0',
    ]
)
