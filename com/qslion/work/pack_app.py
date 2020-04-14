# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:25:02 2020

@author: Administrator
"""
import com.qslion.work.ssh_connection as ssh_connection
import os, tarfile



# 逐个添加文件打包，未打包空子目录。可过滤文件。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz_one_by_one(output_filename, source_dir, tmp_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for root, dir, files in os.walk(source_dir):
        root_ = os.path.relpath(root, start=tmp_dir)
        # tar.add(root,arcname=root_)
        for file in files:
            full_path = os.path.join(root, file)
            # print(full_path)
            tar.add(full_path, arcname=os.path.join(root_, file))
    tar.close()


# 打包本地代码
tar_local_path = 'D:/workspace/maitian/maimai/classes/artifacts/'
tar_file_name = os.path.join(tar_local_path, 'maimai.tar.gz')
make_targz_one_by_one(tar_file_name, tar_local_path + 'maimai', tar_local_path)

# 连接服务器
host_dict = {'host': '172.16.14.72', 'port': 2016, 'username': 'root', 'password': 'maitian123?'}
ssh = ssh_connection.SSHConnection(host_dict)
ssh.connect()

# 停服务器，删除日志
server_base_path = '/home/Application/tomcat-8081'
'''
ssh.run_cmd("kill -9 `ps aux | grep 'java.*tomcat-8081' | grep -v grep`")
ssh.run_cmd("rm -rf {}/webapps/*".format(server_base_path))
ssh.run_cmd("rm -rf {}/work/*".format(server_base_path))
ssh.run_cmd("rm -rf {}/temp/*".format(server_base_path))
ssh.run_cmd("rm -rf {}/bslogs/*".format(server_base_path))
ssh.run_cmd("rm -rf {}/logs/*".format(server_base_path))
'''

# 上传Tar包
server_file_name = '/home/Application/maimai.tar.gz'
print(ssh.upload(tar_file_name, server_file_name))
# 解压Tar包
ssh.run_cmd('tar zxvf {} -C {}'.format(server_file_name, '/home/Application'))
'''
#替换配置文件
ssh.run_cmd('cp -f /home/Application/bak/web.xml {}/webapps/maimai/WEB-INF/'.format(server_base_path))

#启动服务器
ssh.run_cmd('sh {}/bin/startup.sh'.format(server_base_path))
'''
