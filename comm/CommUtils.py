import time

'''
系统处理工具类
'''
class SysUtil():

    '''
    检查指定的参数是否存在
    存在返回 True
    不存在返回 False
    '''
    def isExit(param):

        if (param == None) or (param == ''):
            return False
        else:
            return True

'''
时间处理工具类
'''
class DateUtil():

    def getNowDateTime(format='%Y-%m-%d %H:%M:%S'):

        return time.strftime(format, time.localtime())