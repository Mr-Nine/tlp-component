# -- coding: utf-8 --
__author__ = 'dcp team dujiujun - tlp-agent'
'''
@Project:TLP-Agent
@Team:DCP
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-10-31 09:59:24
@LastEditTime: 2019-11-20 17:57:08
@Description:
'''
import platform
import ipaddress
import datetime

# -------------------------------------------------------------------------
def get_os_type():
    """Get current os type.
    """
    os_info = platform.platform()
    if 'Ubuntu' in os_info:
        return 'ubuntu'
    if 'centos' in os_info:
        return 'centos'
    if 'windows' in os_info:
        return 'windows'

# -------------------------------------------------------------------------
def to_str(bstr, encoding='utf-8'):
    '''将二进制得数据转换为一个字符串
    '''
    if isinstance(bstr, bytes):
        return bstr.decode(encoding)
    return bstr

# -------------------------------------------------------------------------
def to_ip_address(ipstr):
    '''将一个地址字符串转换为一个python得地址对象
    '''
    return ipaddress.ip_address(to_str(ipstr))

# -------------------------------------------------------------------------
def to_int(string):
    '''将字符串转换为一个int值
    '''
    try:
        return int(string)
    except (TypeError, ValueError):
        return None

# -------------------------------------------------------------------------
def get_current_datetime_string():
    '''获取当前可读得系统时间字符串
    '''
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# -------------------------------------------------------------------------
def is_valid_port(port):
    '''验证端口号是否合法
    '''
    return 0 < port < 65536

# -------------------------------------------------------------------------
def mysql_dict_2_dict(data_dict):
    return_dict = {}
    for key in data_dict.keys():
        value = data_dict[key]

        if isinstance(value, bytes):
            return_dict[key] = str(value, encoding="utf-8")
        elif isinstance(value, datetime.datetime):
            return_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return_dict[key] = value

    return return_dict