try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='Serializer',
    version='0.2.0',
    description=(
        'Easy object serialization. '
        'Mimics RoR ActiveRecord serializer.'
    ),
    long_description=__doc__,
    author='Konsta Vesterinen',
    author_email='konsta.vesterinen@gmail.com',
    url='http://github.com/kvesteri/serializer',
    packages=['serializer'],
    include_package_data=True,
    license='BSD',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'setuptools',
        'simplejson'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
