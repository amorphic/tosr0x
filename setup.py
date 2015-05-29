from distutils.core import setup

setup(
    name='tosr0x',
    version='0.3.0',
    author='James Stewart',
    author_email='jstewart101@gmail.com',
    url='https://github.com/amorphic/tosr0x',
    description='An interface to tinyos.com TOSR0x relay modules.',
    long_description=open('README.md').read(),
    license='LICENSE.txt',
    py_modules=['tosr0x'],
    install_requires=[
        'pyserial>=2.0,<3.0',
    ],
)
