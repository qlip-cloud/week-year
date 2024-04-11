from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in ball_customization/__init__.py
from ball_customization import __version__ as version

setup(
	name='ball_customization',
	version=version,
	description='Ball Customization',
	author='Mentum Group',
	author_email='aryrosa.fuentes@MENTUM.group',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
