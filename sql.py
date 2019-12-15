# -*- coding:UTF-8 -*-

import MySQLdb


def open_database():
    db = MySQLdb.connect("localhost","root","xxxxxxxxxx","huawei_vm_datas",charset='utf8')
    cursor = db.cursor()
    def write_job_name(sql):
        #sql = "INSERT INTO vm_table(vm_creat_job,vm_name)values ('%s','%s')" %(vm_creat_job,vm_name)
        sqls = sql
        try:
            cursor.execute(sqls)
            db.commit()
            print "写入数据库成功"
        except:
            db.rollback()
    def query_vm_jobs(sql):
        sqls = sql
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            job = results[0][0]
            return job
        except:
            print "Error: unable to fecth data"

    return write_job_name,query_vm_jobs
    db.close()
