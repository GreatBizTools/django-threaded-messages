from distutils.core import setup

setup(
    name='django-threaded-messages',
    version=__import__('threaded_messages').__version__,
    description='User-to-user threaded messaging system (similar to facebook) for Django',
    author='Philipp Wassibauer, John Debs',
    author_email='phil@gidsy.com',
    url='https://github.com/Gidsy/django-threaded-messages',
    download_url='https://github.com/Gidsy/django-threaded-messages',
    packages=(
        'threaded_messages',
        'threaded_messages.migrations',
        'threaded_messages.templatetags',
    ),
    package_data={
        'threaded_messages': [
            'templates/django_messages/*.html',
            'locale/*/LC_MESSAGES/*',
            'static/js/*.js',
            'static/css/*.css',
        ],
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Framework :: Django',
    ),
)