from setuptools import setup
from setuptools import find_packages

install_requires = [
    'acme',
    'certbot'
]

setup(
    name='certbot-external-auth',
    description="External authenticator for Certbot",
    url='https://github.com/EnigmaBridge/certbot-external-auth',
    author="Dusan Klinec",
    author_email='dusan@enigmabridge.com',
    license='Apache License 2.0',
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={
        'certbot.plugins': [
            'external = certbot_external_auth.plugin:Authenticator',
        ],
    },
)
