from setuptools import setup, find_packages

setup(
    name='Pytwcla',
    version='0.1',
    description="Command-line app for collecting keyword-based Twitter data.",
    author='akisxyz',
    license='MIT',
    url='http://github.com/akisxyz/pytwcla',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'],
    keywords=['twitter', 'search', 'stream', 'database'],
    packages=find_packages(),
    install_requires = [],
    data_files=[('Docs', ['README.rst'])],
    include_package_data = True,
    zip_safe=False,
    entry_points = {
        'console_scripts': ['pytwcla = Pytwcla.pytwcla:main'],}
)