from setuptools import setup

'''
Flask-OpenTracing
-----------------

This extension provides simple integration of OpenTracing in Flask applications.
'''
version = open('VERSION').read()
setup(
    name='Flask-OpenTracing',
    version=version,
    url='http://github.com/opentracing-contrib/python-flask',
    download_url='https://github.com/opentracing-contrib/python-flask/tarball/'+version,
    license='BSD',
    author='Kathy Camenzind',
    author_email='kcamenzind@lightstep.com',
    description='OpenTracing support for Flask applications',
    long_description=open('README.rst').read(),
    packages=['flask_opentracing', 'tests'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'opentracing>=1.1,<1.2'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
