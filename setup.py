from setuptools import setup, find_packages

# Package metadata
NAME = 'tex_table'
VERSION = '1.0'
DESCRIPTION = 'TexTable is a simple Python class that converts array-like objects such as Pandas DataFrames and Series, NumPy arrays, PyTorch tensors, and Python lists to $\LaTeX$ table representations.'
URL = 'https://github.com/dan-the-meme-man/tex-table'
AUTHOR = 'Dan DeGenaro'
AUTHOR_EMAIL = 'drd92@georgetown.edu'
LICENSE = 'MIT'
KEYWORDS = ['tex', 'latex', 'table', 'tables']

# Read the contents of your README file
with open('README.md', 'r') as f:
    long_description = f.read()

# Define dependencies
INSTALL_REQUIRES = [
    'requests>=2.25.1',
    # Add other dependencies here
]

# Package configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    keywords=KEYWORDS,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
)
