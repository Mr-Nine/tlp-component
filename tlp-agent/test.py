
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-14 18:37:16
@LastEditTime: 2020-03-16 14:56:37
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
    type = 'META'
    source = 'MANUAL'
    heat = 0
    inferencerId = None
    icon = None
    shortcutKey = None
    enabled = 1
    attribute = ''
    creatorId = '828af57e-3be7-5cbd-b703-5198d6e02810'
    createTime = datetime.datetime.today()
    updateTime = datetime.datetime.today()

    sql = '''INSERT INTO `AnnotationProjectLabelTemplate` (
        `id`, `projectId`, `name`, `labelGroupId`, `type`, `source`, `heat`, `inferencerId`, `icon`, `backgroundColor`, `shortcutKey`, `enabled`, `required`, `defaulted`, `reviewed`, `attribute`, `creatorId`, `createTime`, `updateTime`
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )'''

    manager = MysqlManager()

    # result = manager.selectAll("select * from User")

    # 插入META标签


    values = []
    for i in range(20):
        id = str(uuid.uuid4())
        name = ('meta-label-' + str(i))
        backgroundColor = '#' + ("".join([random.choice("0123456789ABCDEF") for i in range(6)]))
        required = random.randint(0, 1)
        defaulted = random.randint(0, 1)
        reviewed = random.randint(0, 1)

        values.append((id, projectId, name, labelGroupId, type, source, heat, inferencerId, icon, backgroundColor, shortcutKey, enabled, required, defaulted, reviewed, attribute, creatorId, createTime, updateTime))

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

        values.append((id, projectId, name, labelGroupId, type, source, heat, inferencerId, icon, backgroundColor, shortcutKey, enabled, required, defaulted, reviewed, attribute, creatorId, createTime, updateTime))

    try:
        manager.insertMany(sql, values)
        # pass
    except DataBaseException as e:
        print("==========================================================")
        # traceback.print_exc(file=sys.stdout)
        e.print_exception_message()
        print("==========================================================")

    manager.destory()

if __name__ == "__main__":
    main()
