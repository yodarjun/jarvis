
from setuptools import setup, find_packages

setup(
    name='jarvis-hal',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openai',
        'anthropic',
        'google-generativeai',
        'prompt_toolkit',
        'python-dotenv',
        'rich',
        'wcwidth'
    ],
    entry_points={
        'console_scripts': [
            'jarvis=jarvis.main:main',
        ],
    },
)
