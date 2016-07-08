from setuptools import setup


setup(
    name='Flask-OpenTracing',
    version='0.1',
    # url='http://example.com/flask-sqlite3/',
    license='MIT',
    # author='Your Name',
    # author_email='your-email@example.com',
    description='OpenTracing support for Flask applications',
    # long_description=__doc__,
    packages=['flask_opentracing'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'opentracing'
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