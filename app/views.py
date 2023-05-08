import uuid
from datetime import time

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q

from app import models
from comm import ExamUtils
from comm.BaseView import BaseView
from comm.CommUtils import SysUtil
from comm.CommUtils import DateUtil

'''
系统处理
'''


class SysView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return SysView.getUserInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'login':
            return SysView.login(request)
        elif module == 'exit':
            return SysView.exit(request)
        elif module == 'info':
            return SysView.updUserInfo(request)
        elif module == 'pwd':
            return SysView.updUserPwd(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定用户信息
    def getUserInfo(request):

        user = models.Users.objects.filter(id=cache.get(request.GET.get('token'))).first()

        if user.type == 0:

            return BaseView.successData({
                'id': user.id,
                'userName': user.userName,
                'name': user.name,
                'gender': user.gender,
                'age': user.age,
                'type': user.type,
            })
        elif user.type == 1:

            teacher = models.Teachers.objects.filter(user__id=user.id).first()
            return BaseView.successData({
                'id': user.id,
                'userName': user.userName,
                'name': user.name,
                'gender': user.gender,
                'age': user.age,
                'type': user.type,
                'phone': teacher.phone,
                'record': teacher.record,
                'job': teacher.job,
            })
        elif user.type == 2:

            student = models.Students.objects.filter(user__id=user.id).first()
            return BaseView.successData({
                'id': user.id,
                'userName': user.userName,
                'name': user.name,
                'gender': user.gender,
                'age': user.age,
                'type': user.type,
                'gradeId': student.grade.id,
                'gradeName': student.grade.name,
                'collegeId': student.college.id,
                'collegeName': student.college.name,
            })

    # 登陆处理
    def login(request):
        userName = request.POST.get('userName')
        passWord = request.POST.get('passWord')

        user = models.Users.objects.filter(userName=userName)
        if user.exists():
            user = user.first()
            if user.passWord == passWord:
                token = uuid.uuid4()
                resl = {
                    'token': str(token)
                }
                cache.set(token, user.id, 60 * 60 * 60 * 3)
                return SysView.successData(resl)
            else:
                return SysView.warn('用户密码输入错误')
        else:
            return SysView.warn('用户名输入错误')

    # 退出系统
    def exit(request):
        cache.delete(request.POST.get('token'))
        return BaseView.success()

    # 修改用户信息
    def updUserInfo(request):

        user = models.Users.objects.filter(id=cache.get(request.POST.get('token')))
        if (request.POST.get('userName') != user.first().userName) & \
                (models.Users.objects.filter(userName=request.POST.get('userName')).exists()):
            return BaseView.warn('用户账号已存在')
        else:
            user.update(
                userName=request.POST.get('userName'),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                age=request.POST.get('age'),
            )
            return BaseView.success()

    # 修改用户密码
    def updUserPwd(request):

        user = models.Users.objects.filter(id=cache.get(request.POST.get('token')))

        if (request.POST.get('newPwd') != request.POST.get('rePwd')):

            return BaseView.warn('两次输入的密码不一致')
        elif (request.POST.get('oldPwd') != user.first().passWord):

            return BaseView.warn('原始密码输入错误')
        else:
            user.update(
                passWord=request.POST.get('newPwd')
            )
            return BaseView.success()


'''
学院信息处理
'''


class CollegesView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return CollegesView.getAll(request)
        elif module == 'page':
            return CollegesView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return CollegesView.addInfo(request)
        elif module == 'upd':
            return CollegesView.updInfo(request)
        elif module == 'del':
            return CollegesView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取全部的学院信息
    def getAll(request):

        colleges = models.Colleges.objects.all();

        return BaseView.successData(list(colleges.values()))

    # 分页获取学院信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q();

        if SysUtil.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Colleges.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加学院信息
    def addInfo(request):

        models.Colleges.objects.create(
            name=request.POST.get('name'),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改学院信息
    def updInfo(request):

        models.Colleges.objects. \
            filter(id=request.POST.get('id')).update(
            name=request.POST.get('name')
        )
        return BaseView.success()

    # 删除学院信息
    def delInfo(request):

        if models.Students.objects.filter(college__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联记录无法移除')
        else:
            models.Colleges.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
班级信息处理
'''


class GradesView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return GradesView.getAll(request)
        elif module == 'page':
            return GradesView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return GradesView.addInfo(request)
        elif module == 'upd':
            return GradesView.updInfo(request)
        elif module == 'del':
            return GradesView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取全部的班级信息
    def getAll(request):

        grades = models.Grades.objects.all();

        return BaseView.successData(list(grades.values()))

    # 分页获取班级信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q();

        if SysUtil.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Grades.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加班级信息
    def addInfo(request):

        models.Grades.objects.create(
            name=request.POST.get('name'),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改班级信息
    def updInfo(request):

        models.Grades.objects. \
            filter(id=request.POST.get('id')).update(
            name=request.POST.get('name')
        )
        return BaseView.success()

    # 删除班级信息
    def delInfo(request):

        if models.Students.objects.filter(grade__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联学生无法移除')
        elif models.Exams.objects.filter(grade__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联考试无法移除')
        else:
            models.Grades.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
科目信息处理
'''


class ProjectsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return ProjectsView.getAll(request)
        elif module == 'page':
            return ProjectsView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return ProjectsView.addInfo(request)
        elif module == 'upd':
            return ProjectsView.updInfo(request)
        elif module == 'del':
            return ProjectsView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取全部的科目信息
    def getAll(request):

        projects = models.Projects.objects.all();

        return BaseView.successData(list(projects.values()))

    # 分页获取科目信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q();

        if SysUtil.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Projects.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加科目信息
    def addInfo(request):

        models.Projects.objects.create(
            name=request.POST.get('name'),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改科目信息
    def updInfo(request):

        models.Projects.objects. \
            filter(id=request.POST.get('id')).update(
            name=request.POST.get('name')
        )
        return BaseView.success()

    # 删除科目信息
    def delInfo(request):

        if (models.Exams.objects.filter(project__id=request.POST.get('id')).exists() |
                models.Practises.objects.filter(project__id=request.POST.get('id')).exists()):
            return BaseView.warn('存在关联记录无法移除')
        else:
            models.Projects.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
教师信息处理
'''


class TeachersView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return TeachersView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return TeachersView.addInfo(request)
        elif module == 'upd':
            return TeachersView.updInfo(request)
        elif module == 'del':
            return TeachersView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 分页查询教师信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        record = request.GET.get('record')
        job = request.GET.get('job')

        qruery = Q();
        if SysUtil.isExit(name):
            qruery = qruery & Q(user__name__contains=name)
        if SysUtil.isExit(record):
            qruery = qruery & Q(record=record)
        if SysUtil.isExit(job):
            qruery = qruery & Q(job=job)

        data = models.Teachers.objects.filter(qruery)

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.user.id,
                'userName': item.user.userName,
                'name': item.user.name,
                'gender': item.user.gender,
                'age': item.user.age,
                'type': item.user.type,
                'phone': item.phone,
                'record': item.record,
                'job': item.job
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加教师信息
    @transaction.atomic
    def addInfo(request):

        if models.Users.objects.filter(userName=request.POST.get('userName')).exists():
            return BaseView.warn('账号已存在，请重新输入')
        elif models.Users.objects.filter(id=request.POST.get('id')).exists():
            return BaseView.warn('工号已存在，请重新输入')
        else:
            user = models.Users.objects.create(
                id=request.POST.get('id'),
                userName=request.POST.get('userName'),
                passWord=request.POST.get('userName'),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                age=request.POST.get('age'),
                type=1,
            )
            models.Teachers.objects.create(
                user=user,
                phone=request.POST.get('phone'),
                record=request.POST.get('record'),
                job=request.POST.get('job')
            )
            return BaseView.success()

    # 修改教师信息
    def updInfo(request):

        models.Teachers.objects. \
            filter(user__id=request.POST.get('id')).update(
            phone=request.POST.get('phone'),
            record=request.POST.get('record'),
            job=request.POST.get('job')
        )
        return BaseView.success()

    # 删除教师信息
    @transaction.atomic
    def delInfo(request):

        if models.Exams.objects.filter(teacher__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联记录无法移除')
        else:
            models.Users.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
学生信息处理
'''


class StudentsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return StudentsView.getPageInfos(request)
        elif module == 'info':
            return StudentsView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return StudentsView.addInfo(request)
        elif module == 'upd':
            return StudentsView.updInfo(request)
        elif module == 'del':
            return StudentsView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定学生信息
    def getInfo(request):

        student = models.Students.objects.filter(user__id=request.GET.get('id')).first()

        return BaseView.successData({
            'id': student.user.id,
            'userName': student.user.userName,
            'passWord': student.user.passWord,
            'name': student.user.name,
            'gender': student.user.gender,
            'gradeId': student.grade.id,
            'gradeName': student.grade.name,
            'collegeId': student.college.id,
            'collegeName': student.college.name,
        })

    # 分页查询学生信息
    def getPageInfos(request):
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        collegeId = request.GET.get('collegeId')
        gradeId = request.GET.get('gradeId')

        qruery = Q();
        if SysUtil.isExit(name):
            qruery = qruery & Q(user__name__contains=name)
        if SysUtil.isExit(collegeId):
            qruery = qruery & Q(college__id=int(collegeId))
        if SysUtil.isExit(gradeId):
            qruery = qruery & Q(grade__id=int(gradeId))

        data = models.Students.objects.filter(qruery)

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.user.id,
                'userName': item.user.userName,
                'name': item.user.name,
                'gender': item.user.gender,
                'age': item.user.age,
                'type': item.user.type,
                'gradeId': item.grade.id,
                'gradeName': item.grade.name,
                'collegeId': item.college.id,
                'collegeName': item.college.name
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加学生信息
    @transaction.atomic
    def addInfo(request):

        if models.Users.objects.filter(userName=request.POST.get('userName')).exists():
            return BaseView.warn('账号已存在，请重新输入')
        elif models.Users.objects.filter(id=request.POST.get('id')).exists():
            return BaseView.warn('学号已存在，请重新输入')
        else:
            user = models.Users.objects.create(
                id=request.POST.get('id'),
                userName=request.POST.get('userName'),
                passWord=request.POST.get('userName'),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                age=request.POST.get('age'),
                type=2,
            )
            models.Students.objects.create(
                user=user,
                grade=models.Grades.objects.get(id=request.POST.get('gradeId')),
                college=models.Colleges.objects.get(id=request.POST.get('collegeId'))
            )
            return BaseView.success()

    # 修改学生信息
    def updInfo(request):

        models.Students.objects. \
            filter(user__id=request.POST.get('id')).update(
            grade=models.Grades.objects.get(id=request.POST.get('gradeId')),
            college=models.Colleges.objects.get(id=request.POST.get('collegeId'))
        )
        return BaseView.success()

    # 删除学生信息
    @transaction.atomic
    def delInfo(request):

        if (models.ExamLogs.objects.filter(student__id=request.POST.get('id')).exists() |
                models.AnswerLogs.objects.filter(student__id=request.POST.get('id')).exists()):
            return BaseView.warn('存在关联记录无法移除')
        else:
            models.Users.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
习题信息处理
'''


class PractisesView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return PractisesView.getPageInfos(request)
        elif module == 'info':
            return PractisesView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return PractisesView.addInfo(request)
        elif module == 'setanswer':
            return PractisesView.setAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定 ID 的习题信息
    def getInfo(request):

        practise = models.Practises.objects.filter(id=request.GET.get('id')).first()

        if practise.type == 0:
            return BaseView.successData({
                'id': practise.id,
                'name': practise.name,
                'answer': practise.answer,
                'analyse': practise.analyse,
                'type': practise.type,
                'createTime': practise.createTime,
                'projectId': practise.project.id,
                'projectName': practise.project.name,
                'options': list(models.Options.objects.filter(practise__id=practise.id).values())
            })
        else:
            return BaseView.successData({
                'id': practise.id,
                'name': practise.name,
                'answer': practise.answer,
                'analyse': practise.analyse,
                'type': practise.type,
                'createTime': practise.createTime,
                'projectId': practise.project.id,
                'projectName': practise.project.name,
            })

    # 分页查询习题信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        type = request.GET.get('type')
        projectId = request.GET.get('projectId')

        qruery = Q();
        if SysUtil.isExit(name):
            qruery = qruery & Q(name__contains=name)
        if SysUtil.isExit(type):
            qruery = qruery & Q(type=int(type))
        if SysUtil.isExit(projectId):
            qruery = qruery & Q(project__id=int(projectId))

        data = models.Practises.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):

            if item.type == 0:
                resl.append({
                    'id': item.id,
                    'name': item.name,
                    'answer': int(item.answer) if SysUtil.isExit(item.answer) else '',
                    'analyse': item.analyse,
                    'type': item.type,
                    'projectId': item.project.id,
                    'projectName': item.project.name,
                    'createTime': item.createTime,
                    'optionTotal': models.Options.objects.filter(practise__id=item.id).count()
                })
            else:
                resl.append({
                    'id': item.id,
                    'name': item.name,
                    'answer': item.answer,
                    'analyse': item.analyse,
                    'type': item.type,
                    'projectId': item.project.id,
                    'projectName': item.project.name,
                    'createTime': item.createTime,
                    'optionTotal': 0
                })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加习题信息
    def addInfo(request):
        models.Practises.objects.create(
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            project=models.Projects.objects.get(id=request.POST.get('projectId')),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改习题信息
    def setAnswer(request):
        models.Practises.objects. \
            filter(id=request.POST.get('id')).update(
            answer=request.POST.get('answer'),
            analyse=request.POST.get('analyse')
        )
        return BaseView.success()


'''
选项信息处理
'''


class OptionsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'list':
            return OptionsView.getListByPractiseId(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return OptionsView.addInfo(request)
        elif module == 'upd':
            return OptionsView.updInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 依据习题编号获取选项信息
    def getListByPractiseId(request):

        options = models.Options.objects.filter(practise__id=request.GET.get('practiseId'))

        return BaseView.successData(list(options.values()))

    # 添加选项信息
    def addInfo(request):
        models.Options.objects.create(
            name=request.POST.get('name'),
            practise=models.Practises.objects.get(id=request.POST.get('practiseId'))
        )
        return BaseView.success()

    # 修改选项信息
    def updInfo(request):
        models.Options.objects. \
            filter(id=request.POST.get('id')).update(
            name=request.POST.get('name')
        )
        return BaseView.success()


'''
考试信息处理
'''


class ExamsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return ExamsView.getPageInfos(request)
        elif module == 'info':
            return ExamsView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return ExamsView.addInfo(request)
        elif module == 'make':
            return ExamsView.createExamPaper(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取考试信息
    def getInfo(request):

        exam = models.Exams.objects.filter(id=request.GET.get('id')).first()

        return BaseView.successData({
            'id': exam.id,
            'name': exam.name,
            'createTime': exam.createTime,
            'examTime': exam.examTime,
            'teacherId': exam.teacher.id,
            'teacherName': exam.teacher.name,
            'projectId': exam.project.id,
            'projectName': exam.project.name,
            'gradeId': exam.grade.id,
            'gradeName': exam.grade.name,
        })

    # 分页查询考试信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        gradeId = request.GET.get('gradeId')
        projectId = request.GET.get('projectId')
        teacherId = request.GET.get('teacherId')

        qruery = Q();
        if SysUtil.isExit(teacherId):
            qruery = qruery & Q(teacher__id=teacherId)
        if SysUtil.isExit(name):
            qruery = qruery & Q(name__contains=name)
        if SysUtil.isExit(gradeId):
            qruery = qruery & Q(grade__id=gradeId)
        if SysUtil.isExit(projectId):
            qruery = qruery & Q(project__id=projectId)

        data = models.Exams.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'examTime': item.examTime,
                'createTime': item.createTime,
                'projectId': item.project.id,
                'projectName': item.project.name,
                'teacherId': item.teacher.id,
                'teacherName': item.teacher.name,
                'gradeId': item.grade.id,
                'gradeName': item.grade.name,
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加考试信息
    def addInfo(request):

        if ExamUtils.CheckPractiseTotal.check(request.POST.get('projectId')):

            if models.Teachers.objects.filter(user__id=request.POST.get('teacherId')).exists():
                models.Exams.objects.create(
                    name=request.POST.get('name'),
                    examTime=request.POST.get('examTime'),
                    project=models.Projects.objects.get(id=request.POST.get('projectId')),
                    teacher=models.Users.objects.get(id=request.POST.get('teacherId')),
                    grade=models.Grades.objects.get(id=request.POST.get('gradeId')),
                    createTime=DateUtil.getNowDateTime()
                )
                return BaseView.success()
            else:
                return BaseView.warn('指定工号的教师不存在')
        else:
            return BaseView.warn('相关题目数量不足，无法准备考试')

    # 生成考试试卷
    def createExamPaper(request):
        projectId = request.POST.get('projectId')
        paper = ExamUtils.MakeExam.make(projectId)
        return BaseView.successData(paper)


'''
考试记录处理
'''


class ExamLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'pagestu':
            return ExamLogsView.getPageStudentLogs(request)
        elif module == 'pagetea':
            return ExamLogsView.getPageTeacherLogs(request)
        elif module == 'info':
            return ExamLogsView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return ExamLogsView.addInfo(request)
        elif module == 'upd':
            return ExamLogsView.updInfo(request)
        elif module == 'put':
            return ExamLogsView.putExamLog(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定考试记录
    def getInfo(request):

        examLogs = models.ExamLogs.objects.filter(id=request.GET.get('id')).first()

        answers = []
        qruery = Q();
        qruery = qruery & Q(student__id=request.GET.get('studentId'))
        qruery = qruery & Q(exam__id=examLogs.exam.id)
        temps = models.AnswerLogs.objects.filter(qruery).order_by('no')
        for item in temps:
            answers.append({
                'id': item.id,
                'score': item.score,
                'status': item.status,
                'answer': item.answer,
                'no': item.no,
                'practiseId': item.practise.id,
                'practiseName': item.practise.name,
                'practiseAnswer': item.practise.answer,
                'practiseAnalyse': item.practise.analyse,
                'options': list(models.Options.objects.filter(id=item.practise.id).values()),
            })

        return BaseView.successData({
            'id': examLogs.id,
            'status': examLogs.status,
            'score': examLogs.score,
            'createTime': examLogs.createTime,
            'examId': examLogs.exam.id,
            'examName': examLogs.exam.name,
            'projectId': examLogs.exam.project.id,
            'projectName': examLogs.exam.project.name,
            'teacherId': examLogs.exam.teacher.id,
            'teacherName': examLogs.exam.teacher.name,
            'gradeId': examLogs.exam.grade.id,
            'gradeName': examLogs.exam.grade.name,
            'answers': answers
        })

    # 分页获取学生考试记录
    def getPageStudentLogs(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        examName = request.GET.get('examName')
        studentId = request.GET.get('studentId')
        projectId = request.GET.get('projectId')

        qruery = Q(student__id=studentId);
        if SysUtil.isExit(examName):
            qruery = qruery & Q(exam__name__contains=examName);
        if SysUtil.isExit(projectId):
            qruery = qruery & Q(exam__project__id=projectId)

        data = models.ExamLogs.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'status': item.status,
                'createTime': item.createTime,
                'score': item.score,
                'examId': item.exam.id,
                'examName': item.exam.name,
                'teacherId': item.exam.teacher.id,
                'teacherName': item.exam.teacher.name,
                'projectId': item.exam.project.id,
                'projectName': item.exam.project.name,
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 分页获取教师审核记录
    def getPageTeacherLogs(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        examName = request.GET.get('examName')
        token = request.GET.get('token')
        gradeId = request.GET.get('gradeId')
        projectId = request.GET.get('projectId')

        qruery = Q(exam__teacher__id=cache.get(token));
        if SysUtil.isExit(examName):
            qruery = qruery & Q(exam__name__contains=examName)
        if SysUtil.isExit(gradeId):
            qruery = qruery & Q(exam__grade__id=gradeId)
        if SysUtil.isExit(projectId):
            qruery = qruery & Q(exam__project__id=projectId)

        data = models.ExamLogs.objects.filter(qruery).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'status': item.status,
                'createTime': item.createTime,
                'score': item.score,
                'examId': item.exam.id,
                'examName': item.exam.name,
                'studentId': item.student.id,
                'studentName': item.student.name,
                'projectId': item.exam.project.id,
                'projectName': item.exam.project.name,
                'gradeId': item.exam.grade.id,
                'gradeName': item.exam.grade.name,
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加考试记录
    def addInfo(request):

        models.ExamLogs.objects.create(
            student=models.Users.objects.get(id=cache.get(request.POST.get('token'))),
            exam=models.Exams.objects.get(id=request.POST.get('examId')),
            status=0,
            score=0,
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改考试记录
    def updInfo(request):

        models.ExamLogs.objects. \
            filter(id=request.POST.get('id')).update(
            status=request.POST.get('status')
        )
        return BaseView.success()

    # 公布学生考核成绩
    def putExamLog(request):
        studentId = request.POST.get('studentId')
        examId = request.POST.get('examId')

        qruery = Q(student__id=studentId)
        qruery = qruery & Q(exam__id=examId)

        total = 0.0
        answers = models.AnswerLogs.objects.filter(qruery)
        for item in answers:

            if item.practise.type == 0:
                temp = 2 if item.practise.answer == item.answer else 0
                total = total + temp
                models.AnswerLogs.objects. \
                    filter(id=item.id).update(
                    status=1,
                    score=temp
                )
            elif item.practise.type == 1:
                total = total + item.score
            elif item.practise.type == 2:
                temp = 2 if item.practise.answer == item.answer else 0
                total = total + temp
                models.AnswerLogs.objects. \
                    filter(id=item.id).update(
                    status=1,
                    score=temp
                )
            elif item.practise.type == 3:
                total = total + item.score

        models.ExamLogs.objects. \
            filter(qruery).update(
            status=2,
            score=total
        )
        return BaseView.success()


'''
答题记录处理
'''


class AnswerLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return AnswerLogsView.getInfo(request)
        elif module == 'answers':
            return AnswerLogsView.getAnswers(request)
        elif module == 'check':
            return AnswerLogsView.checkAnswers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return AnswerLogsView.addInfo(request)
        elif module == 'audit':
            return AnswerLogsView.aduitAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定答题记录
    def getInfo(request):
        pass

    # 获取指定的答案列表
    def getAnswers(request):

        studentId = request.GET.get('studentId')
        type = request.GET.get('type')
        examId = request.GET.get('examId')

        qruery = Q(student__id=studentId);
        qruery = qruery & Q(exam__id=examId)

        resl = []
        data = models.AnswerLogs.objects.filter(qruery).order_by('no')
        for item in data:

            if item.practise.type == int(type):
                resl.append({
                    'id': item.id,
                    'practiseId': item.practise.id,
                    'practiseName': item.practise.name,
                    'practiseAnswer': item.practise.answer,
                    'answer': item.answer,
                    'score': item.score,
                    'status': item.status,
                    'no': item.no
                })
            elif item.practise.type == int(type):
                resl.append({
                    'id': item.id,
                    'practiseId': item.practise.id,
                    'practiseName': item.practise.name,
                    'practiseAnswer': item.practise.answer,
                    'answer': item.answer,
                    'score': item.score,
                    'status': item.status,
                    'no': item.no
                })

        return BaseView.successData(resl)

    # 按照类型检查答题
    def checkAnswerType(studentId, examId, type):

        qruery = Q(student__id=studentId)
        qruery = qruery & Q(exam__id=examId)
        qruery = qruery & Q(status=0)
        qruery = qruery & Q(practise__type=type)

        return models.AnswerLogs.objects.filter(qruery).exists()

    # 检查手动审核题目
    def checkAnswers(request):

        studentId = request.GET.get('studentId')
        examId = request.GET.get('examId')

        qruery = Q(student__id=studentId)
        qruery = qruery & Q(exam__id=examId)
        qruery = qruery & Q(status=0)
        qruery = qruery & Q(practise__type=1)
        qruery = qruery | Q(practise__type=3)

        if AnswerLogsView.checkAnswerType(studentId, examId, 1):

            return BaseView.successData({'flag': True, 'msg': '填空题还有未审核的内容'})
        elif AnswerLogsView.checkAnswerType(studentId, examId, 3):

            return BaseView.successData({'flag': True, 'msg': '编程题还有未审核的内容'})
        else:

            return BaseView.successData({'flag': False, 'msg': '手动审核部分已完成'})

    # 添加答题记录
    @transaction.atomic
    def addInfo(request):

        answers = request.POST.getlist('answers')
        nos = request.POST.getlist('nos')
        practiseIds = request.POST.getlist('practiseIds')
        examId = request.POST.get('examId')
        token = request.POST.get('token')

        for no in nos:
            models.AnswerLogs.objects.create(
                student=models.Users.objects.get(id=cache.get(token)),
                exam=models.Exams.objects.get(id=examId),
                practise=models.Practises.objects.get(id=practiseIds[int(no) - 1]),
                status=0,
                answer=answers[int(no) - 1],
                no=no
            )
        qruery = Q(exam__id=examId);
        qruery = qruery & Q(student__id=cache.get(token))
        models.ExamLogs.objects. \
            filter(qruery).update(
            status=1
        )
        return BaseView.success()

    # 审核答题
    def aduitAnswer(request):

        if int(request.POST.get('type')) == 1:

            models.AnswerLogs.objects. \
                filter(id=request.POST.get('id')).update(
                status=1,
                score=2 if int(request.POST.get('flag')) == 0 else 0,
            )
        else:
            models.AnswerLogs.objects. \
                filter(id=request.POST.get('id')).update(
                status=1,
                score=20 if int(request.POST.get('flag')) == 0 else 0,
            )

        return BaseView.success()
