from setuptools import setup

setup(
    name='tosr0x',
    version='0.6.4',
    author='James Stewart',
    author_email='jstewart101@gmail.com',
    url='https://github.com/amorphic/tosr0x',
    description='An interface to tinyos.com TOSR0x relay modules.',
    long_description=open('README.md').read(),
    license='LICENSE.txt',
    py_modules=['tosr0x'],
    install_requires=[
        'pyserial>=3.0,<4.0',
    ],
)
