from setuptools import setup
from setuptools import find_packages

version = '0.1.0'

install_requires = [
    'acme',
    'josepy',
    'certbot>=0.15',
]

setup(
    name='certbot-external-auth',
    version=version,
    description="External authenticator for Certbot",
    url='https://github.com/EnigmaBridge/certbot-external-auth',
    author="Dusan Klinec",
    author_email='dusan@enigmabridge.com',
    license=open('LICENSE.txt').read(),
    long_description=open('README.rst').read(),
    python_requires='>=2.6,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    classifiers=[
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Environment :: Plugins',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
    ],

    install_requires=install_requires,
    packages=find_packages(),
    entry_points={
        'certbot.plugins': [
            'out = certbot_external_auth.plugin:AuthenticatorOut',
        ],
    },
)
