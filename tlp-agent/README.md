# 标注代理器

> 作为服务独立存在于系统内的程序，负责和标注器交互。

## 项目结构说明

```
TLPLibrary/

​    core/：核心内容模块，如配置文件，基本父类，配置文件，数据库处理类等

​    entity/：客户用的实体类

​    error/：所有包用的封装错误

​    service/：对外提供服务的类

​    tools/：工具类
```

## 说明和备注

**当前Agent只支持python3!**

**Agent依赖：**

tornado>=6.0.2

mysqlclient>=1.4.5

DBUtils>=1.3

## 安装方法

安装Python3，[下载地址](https://www.python.org/ftp/python/3.7.7/python-3.7.7-amd64.exe)，next 2 over；

开启一个cmd命令行窗口，尝试输入`pip list`，如果有结果返回，则说明pip安装正常，如果没有成功安装pip，则先下载安装[pip的脚本](https://bootstrap.pypa.io/get-pip.py)，下载到本地后开启cmd，切换到get-pip.py(刚才下载的脚本)所在的目录，执行`python get-pip.py`，安装pip，然后再执行`pip list`检查是否能正确返回结果；

切换到tlp-agent目录下，执行命令`pip install -r requirements.txt`

## 运行方法

运行项目目录下的`run-linux.sh`或`run-windows.sh`即可在后台启动服务。

## 测试方法

**测试请通过chrome的插件进行ws连接测试，无单独测试方法**

