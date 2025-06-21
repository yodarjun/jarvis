from setuptools import setup, find_packages

setup(
    name='jarvis-hal',
    version='0.3.0',
    description='A multi-model AI assistant with personality',
    author='Arjun',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'anthropic>=0.8.0',
        'google-generativeai>=0.3.0',
        'prompt_toolkit>=3.0.0',
        'python-dotenv>=1.0.0',
        'rich>=13.0.0',
        'wcwidth>=0.2.0',
        'click>=8.0.0',
        'pydantic>=2.0.0',
        'loguru>=0.7.0',
        'typer>=0.9.0',  # Modern CLI framework
        'asyncio>=3.4.3',
        'aiohttp>=3.8.0',  # For async HTTP requests
    ],
    entry_points={
        'console_scripts': [
            'jarvis=jarvis.cli:app',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
