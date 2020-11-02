from setuptools import setup
setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='LiveObjects',
    url='https://github.com/jladan/package_demo',
    author='Kacper Sawicki, Krzysztof Krześlak',
    #author_email='example@example.com',
    # Needed to actually package something
    packages=['LiveObjectsSDK'],
    # Needed for dependencies
    install_requires=['paho-mqtt'],
    # *strongly* suggested for sharing
    version='1.0',
    # The license can be anything you like
    license='MIT',
    description='This module allows to easy send data to Orange LiveObjects',

    #additional filees
    data_files=[("Lib/site-packages/LiveObjectsSDK",["LiveObjectsSDK/certfile.cer"])]
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)