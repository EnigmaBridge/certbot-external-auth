from setuptools import setup
from setuptools import find_packages

version = '0.1.2'

install_requires = [
    'acme',
    'josepy',
    'certbot>=0.15',
]

setup(
    name='certbot-ext-auth',
    version=version,
    description="External authenticator for Certbot",
    url='https://github.com/EnigmaBridge/certbot-external-auth',
    author="Enigma Bridge",
    author_email='support@keychest.net',
    package_data={'certbot-ext-auto': ['LICENSE']},
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type="text/markdown",
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
