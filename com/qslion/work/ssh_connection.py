# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:25:02 2020

@author: Administrator
"""

import paramiko

class SSHConnection(object):
    #构造函数
    def __init__(self, host_dict):
        self.host = host_dict['host']
        self.port = host_dict['port']
        self.username = host_dict['username']
        self.pwd = host_dict['password']
        self.__k = None
 
    def connect(self):
        try:
            #获取Transport实例
            transport = paramiko.Transport((self.host,self.port))
            #连接SSH服务端，使用password
            transport.connect(username=self.username,password=self.pwd)
            self.__transport = transport
        except Exception as e:
            print('ssh %s@%s:passwd %s, error message is %s' % (self.username, self.host,self.pwd, e))
 
    
    def close(self):
        self.__transport.close()
 
    def run_cmd(self, command):
        """
         执行shell命令,返回字典
         return {'color': 'red','result':error}或
         return {'color': 'green', 'result':result}
        :param command:
        :return:
        """
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = self.__transport
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)
        # 获取命令结果
        result = stdout.read()
        # 获取错误信息
        error = stderr.read()
        # 如果有错误信息，返回error
        # 否则返回result
        if error.strip():
            print(error)
            return {'color':'red','result':error}
        else:
            print(result)
            return {'color': 'green', 'result':result}
 
    def upload(self,local_path, target_path):
        # 创建一个已连通的SFTP客户端通道
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # 将本地文件上传到服务器（confirm：是否调用stat()方法检查文件状态，返回ls -l的结果
        uploadLs = sftp.put(local_path, target_path, confirm=True)
        # print(os.stat(local_path).st_mode)
        # 增加权限
        # sftp.chmod(target_path, os.stat(local_path).st_mode)
        #sftp.chmod(target_path, 0o755)  # 注意这里的权限是八进制的，八进制需要使用0o作为前缀
        return self.to_str(uploadLs)
 
    def download(self,target_path, local_path):
        # 连接，下载
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # 从服务器下载文件到本地
        sftp.get(target_path, local_path)
 
    def run(self):
        self.connect()
        pass
        self.close()
        
    def rename(self, old_path, new_path):
        ssh = paramiko.SSHClient()
        ssh._transport = self.__transport
        # 执行命令
        cmd = "mv %s %s".format(old_path, new_path,)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # 获取命令结果
        result = stdout.read()   
        return result;
    
    # 销毁
    def __del__(self):
        self.close()
 
    def to_str(self,bytes_or_str):
        """
        把byte类型转换为str
        :param bytes_or_str:
        :return:
        """
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')
        else:
            value = bytes_or_str
        print(value)
        return value

if __name__=='__main__':
    hostdict_62 = {'host':'172.16.14.62','port':2016,'username':'root','password':'maitian123?'}
    ssh = SSHConnection(hostdict_62)
    ssh.connect()
    ssh.run_cmd('ls -l')
    
    
    