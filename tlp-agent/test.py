
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-14 18:37:16
@LastEditTime: 2019-11-27 11:32:08
@Description:
'''
import sys
import uuid
import random
import datetime
import traceback

from core import MysqlManager

from tlp.entity import AnnotationProjectImageRegion
from tlp.error import DataBaseException

def main():


    projectId = '80882967-e342-4417-b002-8aeaf41cd6ea'
    labelGroupId = None
    type = 'MATE'
    source = 'MANUAL'
    heat = 0
    reasoningMachineId = None
    icon = None
    shortcutKey = None
    enabled = 1
    attribute = ''
    creatorId = '828af57e-3be7-5cbd-b703-5198d6e02810'
    createTime = datetime.datetime.today()
    updateTime = datetime.datetime.today()

    sql = '''INSERT INTO `AnnotationlProjectLabelTemplate` (
        `id`, `projectId`, `name`, `labelGroupId`, `type`, `source`, `heat`, `reasoningMachineId`, `icon`, `backgroundColor`, `shortcutKey`, `enabled`, `required`, `defaulted`, `reviewed`, `attribute`, `creatorId`, `createTime`, `updateTime`
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )'''

    """
    manager = MysqlManager()

    # result = manager.selectAll("select * from User")

    # 插入MATE标签


    values = []
    for i in range(20):
        id = str(uuid.uuid4())
        name = ('mate-label-' + str(i))
        backgroundColor = '#' + ("".join([random.choice("0123456789ABCDEF") for i in range(6)]))
        required = random.randint(0, 1)
        defaulted = random.randint(0, 1)
        reviewed = random.randint(0, 1)

        values.append((id, projectId, name, labelGroupId, type, source, heat, reasoningMachineId, icon, backgroundColor, shortcutKey, enabled, required, defaulted, reviewed, attribute, creatorId, createTime, updateTime))

    # manager.insertMany(sql, values)

    # 插入REGION标签

    values = []
    type = 'REGION'
    for i in range(1, 50):
        id = str(uuid.uuid4())
        name = ('region-label-' + str(i))
        backgroundColor = '#' + ("".join([random.choice("0123456789ABCDEF") for i in range(6)]))
        required = random.randint(0, 1)
        defaulted = random.randint(0, 1)
        reviewed = random.randint(0, 1)

        values.append((id, projectId, name, labelGroupId, type, source, heat, reasoningMachineId, icon, backgroundColor, shortcutKey, enabled, required, defaulted, reviewed, attribute, creatorId, createTime, updateTime))

    try:
        manager.insertMany(sql, values)
        # pass
    except DataBaseException as e:
        print("==========================================================")
        # traceback.print_exc(file=sys.stdout)
        e.print_exception_message()
        print("==========================================================")

    manager.destory()
    """


        # region = AnnotationProjectImageRegion(id="A", imageId="B", index=0, shape="C", shapeData="{json:json}", userId="D", createTime=datetime.datetime.today(), updateTime=datetime.datetime.today())

        # print(region.id)
        # print(region.imageId)
        # print(region.index)
        # print(region.shape)
        # print(region.shapeData)
        # print(region.userId)
        # print(region.createTime)
        # print(region.updateTime)

        # region.to_dict()["id"] = "A1"
        # print(region.id)
    arr = []
    if arr:
        print("A")
    arr.append("A")
    if arr:
        print("A")

if __name__ == "__main__":
    main()
