from setuptools import setup, find_packages
import os
import cms

setup(
    author="Patrick Lauber",
    author_email="digi@treepy.com",
    name='django-cms-timetravel',
    version=cms.__version__,
    description='An Advanced Django CMS',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    url='http://www.django-cms.org/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    requires=[
        'django (>1.1.0)',
    ],
    packages=find_packages(),
    package_dir={
        'cms': 'cms',
        'mptt': 'mptt',
        'publisher': 'publisher',
    },
    zip_safe = False,
    include_package_data=True,
)
