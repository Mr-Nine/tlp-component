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

无需安装，运行项目目录下的`run-linux.sh`或`run-windows.sh`即可在后台启动服务。

## 测试方法

**测试请通过chrome的插件进行ws连接测试，无单独测试方法**

