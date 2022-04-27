from setuptools import setup
setup(
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    name='LiveObjects',
    url='https://github.com/DatavenueLiveObjects/LiveObjects_SDK_for_Python',
    author='Kacper Sawicki, Krzysztof Krześlak, Tomasz Malek',
    #author_email='',

    packages=['LiveObjects'],
    include_package_data=True,
    install_requires=['paho-mqtt'],

    version='2.0.2',
    license='MIT',


    description='This module allows to easy send data to Orange LiveObjects using Python3 and uPython',
)
