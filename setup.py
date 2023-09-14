from setuptools import setup, find_packages
from src.sayvai_tools import __version__

core_requirements = [
    'langchain',
    'langchain_experimental',
    'google-api-python-client',
    'openai',
    'SQLAlchemy',
    'elevenlabs==0.2.24',
    'google_auth_oauthlib',
    'google-auth-httplib2',
]

setup(
    name='sayvai_tools',
    version=__version__,
    description='Tools for the assistant',
    author='sayvai-io',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=core_requirements,
    extras_require={
        'dev': [
            'pytest',
            'pylint',
        ],
    },
    zip_safe=False
)
    