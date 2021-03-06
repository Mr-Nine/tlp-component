# TLP Agent Celery Model

## 目标

解除WS的框架和MYSQL的紧耦合，将异步消息中的同步数据操作剥离，让程序在遇到数据库操作时可以先挂起去处理其他请求，等数据库操作完成后再切回来继续执行，以此来解决消息阻塞的问题。

## 结构

```
  标注器
    |
--tornado
|   |
| celery ---
|   |      |
|-redis  mysql
```

## 流程

操作者通过标注器发送操作消息，TLP-Agent(tornado)的WS模块接收到消息，分发给不同的handler去处理，handler接收到消息后处理前置逻辑（获取缓存，检查数据，组织逻辑），当遇到需要进行数据库的操作时(前期以select)为主，将select的操作数据以task的形式发送给celery(增加异步的操作标签)，celery接收到数据后，进行任务的处理，并将结果写入Redis，然后以回调的形式通知agent处理完成，agent以回调的形式接收返回消息key,对数据进行获取，然后继续自己的业务逻辑处理，将结果返回给标注器。

## 进度

环境准备完成

本地库准备完成

运行Redis服务器

构建celery服务端

拆解agent，将查询任务下发

拆解agent，将查询使用异步

拆解agent，将查询结构作为回调进行处理



