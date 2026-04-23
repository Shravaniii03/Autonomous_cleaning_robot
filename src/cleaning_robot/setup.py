from setuptools import setup
import os
from glob import glob

package_name = 'cleaning_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MAR Team',
    maintainer_email='team@example.com',
    description='Autonomous Cleaning Robot',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'coverage_cleaner = cleaning_robot.coverage_cleaner:main',
        ],
    },
)


