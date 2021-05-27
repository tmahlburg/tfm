import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tfm',
    version='0.0.5dev',
    packages=['tfm', ],
    license='GPLv3',
    author='Till Mahlburg',
    # author_email="author@example.com",
    description='A simple and Qt file manager for Linux',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tmahlburg/tfm',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: X11 Applications :: Qt',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3'
        + ' (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Desktop Environment :: File Managers',
    ],
    python_requires='>=3.6',
)
