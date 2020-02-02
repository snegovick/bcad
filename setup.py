import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

data_files = [('/usr/bin', ['bcad-launcher'])]+[[os.path.join('/usr/share/python3-bcad/', dp), [os.path.join(dp, f) for f in fn]] for dp, dn, fn in list(os.walk('ext/usr'))[1:]]
print(data_files)
setup(
    name = "bcad",
    version = "0.1",
    author = "Konstantin Kirik (snegovick)",
    author_email = "snegovick@uprojects.org",
    description = ("B-tier CAD."),
    license = "BSD",
    keywords = ["CAD", "OpenCASCADE"],
    url = "http://snegovick.me",
    packages=['bcad', 'bcad/binterpreter'],
    long_description=read('README.md'),
    dependency_links = [],
    install_requires = [],
    data_files = data_files,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: BSD",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
)
