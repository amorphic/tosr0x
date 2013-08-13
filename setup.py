from distutils.core import setup

#Fix Windows Binary Build
import codecs 
try: 
    codecs.lookup('mbcs') 
except LookupError: 
    ascii = codecs.lookup('ascii') 
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs') 
    codecs.register(func) 

setup(
    name='tosr0x',
    version='0.1.0',
    py_modules=['tosr0x'],
    description='An interface to the tinysine.com line of USB-controlled relays.',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy",
    ],
)
