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
        'opentracing>=2.0,<3',
    ],
    extras_require={
        'tests': [
            'flake8<3',  # see https://github.com/zheller/flake8-quotes/issues/29
            'flake8-quotes',
            'mock',
            'pytest>=3.6,<4',
            'pytest-cov',
        ],
    },
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
