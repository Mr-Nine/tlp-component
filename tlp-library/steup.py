# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-10 18:25:40
@LastEditTime: 2019-12-17 11:49:17
@Description:
'''
import setuptools
from setuptools import setup, find_packages, Command

setup(
    name='TLPLibrary',
    version='1.0',
    description='TLP label project library',
    author='jerome.du',
    author_email='dujiujun@outlook.com',
    python_requires='>=3',
    packages=[
        "TLPLibrary",
        "TLPLibrary.core",
        "TLPLibrary.error",
        "TLPLibrary.entity",
        "TLPLibrary.service",
        "TLPLibrary.tools"
    ],
    package_data={
        'TLPLibrary.core': ['library.conf'],
        'TLPLibrary.tools': ['import_script_template', 'inferencer_script_template']
    },
    install_requires=[
        'mysqlclient>=1.4.5',
        'DBUtils>=1.3'
    ],
    entry_points={
        'console_scripts': [
            'tlp_script_generator=TLPLibrary.tools.script_generator:main' # script-generator
        ],
    }
)