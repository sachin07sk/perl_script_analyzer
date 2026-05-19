"""
Setup script for MPC Protocol - VLSI/EDA Perl Script Analyzer.

Installation:
    pip install -e .

Or for development:
    pip install -e ".[dev]"
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mpc-perl-analyzer',
    version='1.0.0',
    description='MPC Protocol - Multi-Purpose Checker for VLSI/EDA Perl Script Analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='MPC Protocol Team',
    author_email='mpc@example.com',
    url='https://github.com/example/mpc-perl-analyzer',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        # Core functionality uses Python standard library
        # Optional: reportlab>=4.0 for rich PDF output
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
        ],
        'pdf': [
            'reportlab>=4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'mpc-analyze=src.analyzer:main',
            'mpc-server=mcp_servers.server_manager:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
    keywords='perl analyzer vlsi eda syntax checker modernization pdf report',
    project_urls={
        'Source': 'https://github.com/example/mpc-perl-analyzer',
        'Documentation': 'https://github.com/example/mpc-perl-analyzer#readme',
        'Bug Reports': 'https://github.com/example/mpc-perl-analyzer/issues',
    },
)