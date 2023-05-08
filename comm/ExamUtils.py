
# 校验习题数目
import random

from django.db.models import Q

from app import models


class CheckPractiseTotal():

    # 查询数据
    def qryPractises(type, projectId):
        qruery = Q();
        qruery = qruery & Q(type=type)
        qruery = qruery & Q(project__id=projectId)
        return models.Practises.objects.filter(qruery)

    # 校验指定科目的选择题数目是否足够
    def check_0(data):

        total = 0
        for item in data:
            temp = models.Options.objects.filter(practise__id=item.id).count()
            if temp==4:
                total=total+1

        if total >=10:
            return True
        else:
            return False

    # 校验指定科目的填空题数目是否足够
    def check_1(data):

        if data.count() >=10:
            return True
        else:
            return False

    # 校验指定科目的判断题数目是否足够
    def check_2(data):

        if data.count() >=10:
            return True
        else:
            return False

    # 校验指定科目的编程题数目是否足够
    def check_3(data):

        if data.count() >=2:
            return True
        else:
            return False

        # 组合试卷

    # 检查所有科目题目数量是否足够
    def check(projectId):

        # 获取指定科目的选择题列表
        data_0 = CheckPractiseTotal.qryPractises(0, projectId)

        # 获取指定科目的填空题列表
        data_1 = CheckPractiseTotal.qryPractises(1, projectId)

        # 获取指定科目的判断题列表
        data_2 = CheckPractiseTotal.qryPractises(2, projectId)

        # 获取指定科目的编程题列表
        data_3 = CheckPractiseTotal.qryPractises(3, projectId)

        if (CheckPractiseTotal.check_0(data_0) & CheckPractiseTotal.check_1(data_1) &
            CheckPractiseTotal.check_2(data_2) & CheckPractiseTotal.check_3(data_3)):

            return True
        else:
            return False

# 组织试卷
class MakeExam():

    # 查询数据
    def qryPractises(type, projectId):
        qruery = Q();
        qruery = qruery & Q(type=type)
        qruery = qruery & Q(project__id=projectId)
        return models.Practises.objects.filter(qruery)

    # 生成题号索引列表
    def createNums(rang, total):

        resl = []
        while 1 == 1:
            if len(resl)==total:
                break
            else:
                temp = random.randint(0, rang-1)
                if resl.count(temp)>0:
                    pass
                else:
                    resl.append(temp)
        return resl


    # 组合选择题
    def make_0(data):

        resl = []

        # 提取指定科目的选择题号
        pIds = []
        for item in data:
            pIds.append(item.id)

        # 生成10个随机数
        nums = MakeExam.createNums(data.count(), 10)

        # 根据生成的随机数提取对应的题号
        for item in nums:
            resl.append(pIds[item])

        return resl

    # 组合填空题
    def make_1(data):

        resl = []

        # 提取指定科目的选择题号
        pIds = []
        for item in data:
            pIds.append(item.id)

        # 生成10个随机数
        nums = MakeExam.createNums(data.count(), 10)

        # 根据生成的随机数提取对应的题号
        for item in nums:
            resl.append(pIds[item])

        return resl

    # 组合判断题
    def make_2(data):

        resl = []

        # 提取指定科目的判断题题号
        pIds = []
        for item in data:
            pIds.append(item.id)

        # 生成10个随机数
        nums = MakeExam.createNums(data.count(), 10)

        # 根据生成的随机数提取对应的题号
        for item in nums:
            resl.append(pIds[item])

        return resl

    # 组合编程题
    def make_3(data):

        resl = []

        # 提取指定科目的编程题号
        pIds = []
        for item in data:
            pIds.append(item.id)

        # 生成10个随机数
        nums = MakeExam.createNums(data.count(), 2)

        # 根据生成的随机数提取对应的题号
        for item in nums:
            resl.append(pIds[item])

        return resl

    # 组合试卷
    def make(projectId):

        # 获取指定科目的选择题列表
        data_0 = MakeExam.qryPractises(0, projectId)

        # 获取指定科目的填空题列表
        data_1 = MakeExam.qryPractises(1, projectId)

        # 获取指定科目的判断题列表
        data_2 = MakeExam.qryPractises(2, projectId)

        # 获取指定科目的编程题列表
        data_3 = MakeExam.qryPractises(3, projectId)

        nums_0 = MakeExam.make_0(data_0)
        nums_1 = MakeExam.make_1(data_1)
        nums_2 = MakeExam.make_2(data_2)
        nums_3 = MakeExam.make_3(data_3)

        return {'item_0': nums_0, 'item_1': nums_1, 'item_2': nums_2, 'item_3': nums_3}

