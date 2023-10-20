from setuptools import find_packages, setup

core_requirements = [
    'langchain',
    'langchain_experimental',
    'google-api-python-client',
    'openai',
    'tiktoken',
    'SQLAlchemy',
    'elevenlabs==0.2.24',
    'google_auth_oauthlib',
    'google-auth-httplib2',
    'pyaudio',
    'pydub',
    'numpy',
    'google',
    'google-cloud-speech',
    'cloud-sql-python-connector',
    'pg8000',
    'pinecone-client',
    'pgvector',
    'pandas',
    'openpyxl',
    'gspread==5.11.3'
]

setup(
    name='sayvai_tools',
    version='0.0.1',
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
    
