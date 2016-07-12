from setuptools import setup

'''
Flask-OpenTracing
-----------------

This extension provides simple integration of OpenTracing in Flask applications.
'''

setup(
    name='Flask-OpenTracing',
    version='0.1.0',
    url='http://example.com/flask-sqlite3/',
    download_url='https://github.com/kcamenzind/flask_opentracing/tarball/0.1.0',
    license='MIT',
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
        'opentracing >= 2.0.0.dev0'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)