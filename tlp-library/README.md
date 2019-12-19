# TLP-Library

> 用于部署在客户环境中为导入和推理脚本提供统一入口的库项目

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

**当前库只支持python3!**

**Library依赖：**

mysqlclient>=1.4.5

DBUtils>=1.3

## 安装方法

执行项目文件夹下的`package.sh`或`package.bat`将项目打包成whl文件，然后执行`install.sh`或`install.bat`来安装库到本地环境中的python中。

## 测试方法

### 生成基础脚本

```shell
# 命令行执行如下命令来生成导入脚本的模板
tlp_script_generator -t inferencer -o /tmp -n inferencer.py

# 可以通过帮助来查看命令的具体参数
tlp_script_generator -h 
```

### 编写业务逻辑

```python
from TLPLibrary.entity import *
from TLPLibrary.core import *
from TLPLibrary.error import *
from TLPLibrary.service import InferencerLabelService


def input_data(runParameter):
    # 根据具体的业务场景，实现组织要自动推理或批量导入的标签，形状的信息
    # .
    # .
    # .
    # 取消下面的注释，将内容交给导入程序处理
    # inferencerLabelService = InferencerLabelService
    # result = inferencerLabelService.inferencerOneImageLabel(runParameter, image)
    # if result:
    #     print(result)
    # else:
    #     print(False)


def main():
    runParameter = RunParameter.get_run_parameter()
    input_data(runParameter)

if __name__ == "__main__":
    main()
```

### 测试导入脚本

也可以手动执行来测试导入脚本

```shell
python .\inferencer_script_template.py -pid 80882967-e342-4417-b002-8aeaf41cd6ea -uid 31602ab7-8527-4952-a252-639a9be22d64 -p 192.168.30.198:/export/dujiujun/tlp/gdal2tiles/source/ -t import
```

或

```shell
python .\import_script_template.py -pid 80882967-e342-4417-b002-8aeaf41cd6ea -uid 31602ab7-8527-4952-a252-639a9be22d64 -p 192.168.30.198:/export/dujiujun/tlp/gdal2tiles/source/8.jpg -t inferencer -iid 66655555-e342-4417-b002-111111111111
```

具体参数的意义可以执行如下命令查看`python 导入模板编写的脚本名称.py -h`

