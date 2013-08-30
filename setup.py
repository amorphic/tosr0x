from distutils.core import setup

setup(
    name='tosr0x',
    version='0.1.0',
    py_modules=['tosr0x'],
    description='An interface to the tinysine.com tosr0x line of USB-controlled relays.',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy",
    ],
)
