import sys
import pip
from setuptools import setup, find_packages


if sys.version_info[:2] < (2, 6) or (3, 0) <= sys.version_info[0:2]:
    raise RuntimeError("Python version 2.6, 2.7  required.")


with open('README.rst') as readme_file:
    readme = readme_file.read()


# Dependencies for building C Extensions
dependencies = ['numpy',
                'scipy==0.18',
                'matplotlib',
                'scikits.samplerate==0.3.3',
                'librosa==0.4.2',
                'future',
                'Pillow',
                'PyYAML']

# Installing the required packages
for package in dependencies:
    pip.main(['install', package])

setup(
    name='VMO-Score',
    version='0.1.0',
    description='Generation of an i-score scenario from an audio recording',
    long_description=readme,
    license='GPLv2',
    keywords='improvisation music i-score vmo',
    author='Jaime Arias, Shlomo Dubnov, and Myriam Desainte-Catherine',
    maintainer='Jaime Arias',
    maintainer_email='jaime.arias@inria.fr',
    url='https://github.com/vmo-score/vmo-score',
    packages=find_packages(exclude=('tests*', 'docs', 'examples', 'resources')),
    entry_points={'console_scripts':
                  ['vmo-score=VMO_Score.main:main']},
    include_package_data=True,
    build_requires=dependencies,
    install_requires=dependencies,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved',
        'Intended Audience :: Science/Research',
        'Topic :: Artistic Software',
        'Topic :: Multimedia',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: MacOS'
    ],
    extras_require={
        'test': ['pytest', 'pytest-cov'],
        'docs': ['sphinx', 'sphinx-rtd-theme', 'mock']
    }
)
