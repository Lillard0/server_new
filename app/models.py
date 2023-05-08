from django.db import models

# 学院信息
class Colleges(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('学院名称',  max_length=32, null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_colleges'

# 班级信息
class Grades(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('班级名称',  max_length=32, null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_grades'

# 科目信息
class Projects(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('科目名称',  max_length=32, null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_projects'

# 用户信息
class Users(models.Model):
    id = models.CharField('用户编号', max_length=20, null=False, primary_key=True)
    userName = models.CharField('用户账号', db_column='user_name', max_length=32, null=False)
    passWord = models.CharField('用户密码', db_column='pass_word', max_length=32, null=False)
    name = models.CharField('用户姓名', max_length=20, null=False)
    gender = models.CharField('用户性别', max_length=4, null=False)
    age = models.IntegerField('用户年龄', null=False)
    type = models.IntegerField('用户身份 0-管理员 1-教师 2-学生', null=False)
    class Meta:
        db_table = 'fater_users'

# 学生信息
class Students(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column="user_id")
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE, db_column="grade_id")
    college = models.ForeignKey(Colleges, on_delete=models.CASCADE, db_column="college_id")
    class Meta:
        db_table = 'fater_students'

# 教师信息
class Teachers(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column="user_id")
    phone = models.CharField('联系电话', max_length=11, null=False)
    record = models.CharField('教师学历 ', max_length=10, null=False)
    job = models.CharField('教师职称', max_length=20, null=False)
    class Meta:
        db_table = 'fater_teachers'

# 习题信息
class Practises(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('题目名称',  max_length=64, null=False)
    answer = models.TextField('参考答案')
    analyse = models.TextField('题目分析')
    type = models.IntegerField('题目类型 0-选择 1-填空 2-判断 3-编程', null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column="project_id")
    class Meta:
        db_table = 'fater_practises'

# 选项记录
class Options(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('题目名称',  max_length=64, null=False)
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    class Meta:
        db_table = 'fater_options'

# 考试信息
class Exams(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('考试名称',  max_length=64, null=False)
    teacher = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="teacher_id")
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column="project_id")
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE, db_column="grade_id")
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    examTime = models.CharField('考试时间', db_column='exam_time', max_length=19)
    class Meta:
        db_table = 'fater_exams'

# 参考记录
class ExamLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id")
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, db_column="exam_id")
    status = models.IntegerField('考试状态 0-参考 1-待审 2-结束', null=False)
    score = models.FloatField('考试得分', default=0.0)
    createTime = models.CharField('参考时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_exam_logs'

# 答题记录
class AnswerLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id")
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, db_column="exam_id")
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practises_id")
    score = models.FloatField('审核分数', default=0.0)
    status = models.IntegerField('审核结果 0-待审 1-结束', null=False)
    answer = models.TextField('答案内容')
    no = models.IntegerField('题号索引', null=False)
    class Meta:
        db_table = 'fater_answer_logs'