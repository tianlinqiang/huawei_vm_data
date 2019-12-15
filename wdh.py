#coding=utf-8
import os
import sys
import time
import sql
import commands


name = "xxxxxxxxxxxxxx"
user = "xxxxxxxxxxxxxx"
password = "xxxxxxxxxxx"
project_id = "xxxxxxxxxxxxxx"


url_iam = "https://iam.ap-southeast-1.myhuaweicloud.com/v3/auth/tokens"
url_vm_start = "https://ecs.ap-southeast-1.myhuaweicloud.com/v1/"+project_id+"/cloudservers/action"
url_vm_creat = 'https://ecs.ap-southeast-1.myhuaweicloud.com/v1/'+project_id+'/cloudservers'
url_get_vm_id = 'https://ecs.ap-southeast-1.myhuaweicloud.com/v1/'+project_id+'/jobs/'
url_get_vm_eip = 'https://ecs.ap-southeast-1.myhuaweicloud.com/v1/'+project_id+'/cloudservers/'
url_vm_del = 'https://ecs.ap-southeast-1.myhuaweicloud.com/v1/'+project_id+'/cloudservers/delete'

def get_user_token():
    cmd_user_token = 'curl -i -k -s -X POST '+url_iam+ \
                     ' -H "Content-Type:application/json;charset=UTF-8"'\
                     ' -d \'{"auth":{"identity":{ '\
                     '"methods":["password"],'\
                     '"password":{"user":{"name":"'+user+'",'\
                     '"password":"'+password+'",'\
                     '"domain":{"name":"'+name+'"}}}},'\
                     '"scope":{"project":{"name":"ap-southeast-1"}}}}\''\
                     '|grep X-Subject-Token|awk {\'print $2\'}'
    user_token = commands.getoutput(cmd_user_token)
    if len(user_token) == 0:
        print ("get token fail")
    else:
        return user_token

def vm_creat(user_token,vm_name):
    cmd_vm_creat = 'curl -i -k -s -X POST '+url_vm_creat+\
                    ' -H "Content-Type:application/json;charset=UTF-8"' \
                    ' -H "X-Auth-Token:'+user_token+'"'\
                    ' -d \'{"server": {"availability_zone":"ap-southeast-1a", '\
                    '"name": "'+vm_name+'", "imageRef": "b61f5ce5-1de4-4533-bcf4-184b416a6a43",'\
                    '"root_volume": {"volumetype": "SATA"}, "flavorRef": "s2.medium.2",'\
                    '"vpcid": "d0a98695-a46c-4406-b4a5-938c4cc5b280",'\
                    '"security_groups":[{"id": "b2555fe2-652b-45e3-8e05-ffcc857d2229"}],'\
                    '"nics": [{"subnet_id": "939b9cdd-eeb9-4036-b480-65b4bf9d0ebb"}],'\
                    '"publicip": {"eip": {"iptype": "5_bgp",'\
                    '"bandwidth": {"size": 5, "sharetype": "PER"}}}}}\'|grep job_id|cut -c 12-43'


    vm_creat_jobs = commands.getoutput(cmd_vm_creat)
    if len(vm_creat_jobs) == 0:
        print "虚拟机创建失败"
    else:
        print vm_creat_jobs
        return vm_creat_jobs


def get_vm_id(vm_creat_jobs,user_token):

    cmd_get_vm_id = 'curl -i -k -s -X GET '+url_get_vm_id+vm_creat_jobs+\
                    ' -H "Content-Type:application/json;charset=UTF-8"' \
                    ' -H "X-Auth-Token:'+user_token+'"|grep server_id '\
                    '|awk -F \',\' \'{print $NF}\''\
                    '|awk -F \':\' \'{print $3}\''\
                    '|awk -F \'"\' \'{print $2}\''
    vm_id = commands.getoutput(cmd_get_vm_id)
    if len(vm_id) == 0:
        print "获取虚拟机id失败"
    else:
        return vm_id


def get_vm_eip(vm_id,user_token):

    cmd_get_vm_eip = 'curl -i -k -s -X GET '+url_get_vm_eip+vm_id+\
                     ' -H "Content-Type:application/json;charset=UTF-8"' \
                     ' -H "X-Auth-Token:'+user_token+'"|grep addr'\
                     '|awk -F \',\' \'{if ($FN > 2) print $10}\''\
                     '|awk -F \':\' \'{print $2}\'|tr -d \'"\''
    vm_eip = commands.getoutput(cmd_get_vm_eip)
    cmd_back_bashrc = 'cp ~/.bashrc ~/bashrc.back'
    cmd_del_huaweiip = 'sed -i \'/^[[:space:]]*huaweiip/d\' ~/.bashrc'
    cmd_add_huaweiip = 'sed -i \'/#sedhuaweiip/a\    huaweiip="'+vm_eip+'"\' ~/.bashrc'
    back_bashrc = commands.getoutput(cmd_back_bashrc)
    time.sleep(0.5)
    if len(vm_eip) == 0:
        print "获取EIP失败"
    else:
        del_huaweiip = commands.getoutput(cmd_del_huaweiip)
        add_huaweiip = commands.getoutput(cmd_add_huaweiip)
        return vm_eip

def vm_uuid(vm_name):
   
    sqls = "select vm_uuid from vm_table where vm_name='%s'" %(vm_name)
    
    write_job_name,query_vm_jobs = sql.open_database()
    vm_uuid = query_vm_jobs(sqls)
    if vm_uuid:
        return vm_uuid
    else:
        print "获取虚拟机ID失败,请检查输入的 vm_name 是否正确"
        exit()

def vm_start(user_token,vm_name):
    vm_id = vm_uuid(vm_name)
    cmd_vm_start = 'curl -i -k -s -X POST '+url_vm_start+ \
            ' -H "Content-Type:application/json;charset=UTF-8"'\
            ' -H "X-Auth-Token:'+user_token+\
            '" -d \'{"os-start":{"servers": [{"id":"'+vm_id+'"}]}}\'|grep job_id'
    vm_start_job = commands.getoutput(cmd_vm_start)
    if len(vm_start_job) == 0:
        print ("get start job fail")
    else:
        return vm_start_job

def vm_restartOS(vm_name):
    
    user_token = get_user_token()
    vm_id = vm_uuid(vm_name)
    url_vm_os = 'https://ecs.ap-southeast-1.myhuaweicloud.com/v2/'+project_id+'/cloudservers/'+vm_id+'/reinstallos'
    cmd_vm_restartos = 'curl -i -k -s -X POST '+url_vm_os+ \
                       ' -H "Content-Type:application/json;charset=UTF-8"'\
                       ' -H "X-Auth-Token:'+user_token+ \
                       '" -d \'{"os-reinstall":{"adminpass":"tlq123@321"}}\'|grep HTTP/1.1|awk -F \' \' \'{print $2}\''
    vm_os_job = commands.getoutput(cmd_vm_restartos)
    if vm_os_job == "200":
        print "OS reinstall success"
    else:
        print "OS reinstall fail"


def vm_stop(user_token,vm_name):
    vm_id = vm_uuid(vm_name)
    cmd_vm_stop = 'curl -i -k -s -X POST '+url_vm_start+ \
                    ' -H "Content-Type:application/json;charset=UTF-8"'\
                    ' -H "X-Auth-Token:'+user_token+\
                    '" -d \'{"os-stop":{"type":"HARD","servers":[{"id":"'+vm_id+'"}]}}\'|grep job_id'
    vm_stop_job = commands.getoutput(cmd_vm_stop)
    if len(vm_stop_job) == 0:
        print ("get stop job fail")
    else:
        return vm_stop_job

def vm_del(vm_name,user_token):
    vm_id = vm_uuid(vm_name)
    cmd_vm_del = 'curl -i -k -s -X POST '+url_vm_del+\
                   ' -H "Content-Type:application/json;charset=UTF-8"'\
                   ' -H "X-Auth-Token:'+user_token+\
                   '" -d \'{"servers": [{"id": "'+vm_id+'"}], "delete_publicip": true,'\
                   '"delete_volume": false}\'|grep job_id'
    vm_del_job = commands.getoutput(cmd_vm_del)
    
    if len(vm_del_job) ==0:
        print "get vm_del job fail"
    else:
        return vm_del_job

def creat_vm_ing(vm_name):
    user_token = get_user_token()    
    vm_creat_jobs = vm_creat(user_token,vm_name)
    time.sleep(1)
    write_job_name,query_vm_jobs  = sql.open_database()
    sqls = "INSERT INTO vm_table(vm_creat_job,vm_name)values ('%s','%s')" %(vm_creat_jobs,vm_name)
    write_job_name(sqls)

    

def get_vm_id_ing(vm_name):

    user_token = get_user_token()
    write_job_name,query_vm_jobs = sql.open_database()

    sqls = "select vm_creat_job from vm_table where vm_name='%s'" %(vm_name) 
    vm_creat_jobs = query_vm_jobs(sqls)
    if vm_creat_jobs:
        vm_id = get_vm_id(vm_creat_jobs,user_token)
        vm_eip = get_vm_eip(vm_id,user_token)
        sqls_write_vm_uuid = "update vm_table set vm_uuid = '%s', vm_eip = '%s' where vm_name = '%s'" %(vm_id,vm_eip,vm_name)
        print vm_eip
        write_job_name(sqls_write_vm_uuid)
    else:
        print "请检查虚拟机名字是否正确"
        exit(1)




def vm_start_ing(vm_name):
    user_token = get_user_token()
    vm_start_job = vm_start(user_token,vm_name)
    print (vm_start_job)

def vm_stop_ing(vm_name):
    user_token = get_user_token()
    vm_stop_job = vm_stop(user_token,vm_name)
    print (vm_stop_job)

def vm_del_ing(vm_name):
    user_token = get_user_token()

    vm_del_job = vm_del(vm_name,user_token)
    if len(vm_del_job) > 0:
        
        write_job_name,query_vm_jobs = sql.open_database()
        sqls = "DELETE FROM vm_table  WHERE vm_name = '%s'" %(vm_name)
        write_job_name(sqls)
        print vm_del_job
    else:
        print "删除vm_name:%s 数据库信息失败" %(vm_name)


def query_vm_name(vm_name):
    
    write_job_name,query_vm_jobs = sql.open_database()
    sqls = "select vm_name from vm_table where vm_name = '%s'" %(vm_name)
    vm_name_datas = query_vm_jobs(sqls)
    if vm_name_datas:
        print "输入的vm_name已被使用，请重新输入"
        exit()
    else:
        return True
#    except 

def main():
    print ("""
        功能菜单
        1.虚拟机开机
        2.虚拟机关机
        3.创建虚拟机
        4.获取虚拟机ip
        5.restart os
        6.删除虚拟机
        0.退出
        """
        )
    youinput = int(raw_input("Input num is:"))
    if youinput == 1:
        vm_name = raw_input("pl input vm_name:")
        vm_start_ing(vm_name)
    elif youinput == 2:
        vm_name = raw_input("pl input vm_name:")
        vm_stop_ing(vm_name)
    elif youinput == 3:
        vm_name = raw_input("pl input vm_name:")
        vm_names = query_vm_name(vm_name)
        if vm_names:
            creat_vm_ing(vm_name)
        else:
            exit()
    elif youinput == 4:
        vm_name = raw_input("pl input vm_name:")
        get_vm_id_ing(vm_name)
    elif youinput == 5:
        vm_name = raw_input("pl input vm_name:")
        vm_restartOS(vm_name)
    elif youinput == 6:
        vm_name = raw_input("pl input vn_name:")
        vm_del_ing(vm_name) 
    elif youinput == 0:
        exit()
if __name__ == '__main__':
    main()
