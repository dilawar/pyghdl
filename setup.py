import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
        name='hdltb.py'
        , version='0.1.0'
        , description='A command-line tool to generate testbeches from vhdl design'
        , long_description= read('README.rst') 
        , url = 'https://github.com/dilawar/pyghdl'
        , licence = 'GNU-GPL'
        , author = 'Dilawar Singh'
        , author_email = 'dilawars@iitb.ac.in'
        , maintainer = 'Dilawar Singh'
        , maintainer_email = 'dilawars@iitb.ac.in'
        , requires = ['Python (>=2.6)']
        , packages=['vhdl'
            , 'debug'
            , 'curses'
            , 'testbench'
            ]
        , include_package_data = True
        , classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Environment :: Console',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            ],
        entry_points="""
        [console_scripts]
        hdltb.py=testbench.main:main
        """
        )


