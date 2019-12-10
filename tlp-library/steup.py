# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-10 18:25:40
@LastEditTime: 2019-12-10 20:23:53
@Description:
'''
import setuptools
from setuptools import setup, find_packages, Command

class InstallCommand(Command):
    description = "install tlp library 2 you computer."
    user_options = [
        ('mysql_host=', 'localhost', 'Specify the foo to bar.'),
        ('mysql_port=', 3306, 'Specify the foo to bar.'),
        ('mysql_user=', 'root', 'Specify the foo to bar.'),
        ('mysql_pwd=', '000000', 'Specify the foo to bar.'),
    ]

    def initialize_options(self):
        self.mysql_host = 'localhost'
        self.mysql_port = 3306
        self.mysql_user = 'root'
        self.mysql_pwd = '000000'

    def finalize_options(self):
        assert self.foo in (None, 'myFoo', 'myFoo2'), 'Invalid foo!'

    def run(self):
        if not self.skip_build:
            setuptools.command.install.install.run(self)

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
        "TLPLibrary.service"
    ],
    package_data={
        'TLPLibrary.core': ['library.conf'],
    },
    install_requires=[
        'mysqlclient>=1.4.5',
        'DBUtils>=1.3'
    ],
    cmdClass={
        'install':InstallCommand,
    }
)