import setuptools
import ffsize

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ffsize",
    version=ffsize.VERSION,
    description="Counts all the files, folders, and total sizes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elesiuta/ffsize",
    py_modules=['ffsize'],
    entry_points={
        'console_scripts': [
            'ffsize = ffsize:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
    ],
)
