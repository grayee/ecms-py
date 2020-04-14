# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 11:00:35 2020

@author: Administrator
"""

from fabric import Connection


def main():
    file_local_path = 'D:/maimai/deploy'
    host_config = [{'host': 'root@172.16.14.251:2016', 'password': 'maitian123?',
                    'uplodList': [
                        {'android1': '{}/12环境.apk'.format(file_local_path), 'ios': '{}/12.ipa'.format(file_local_path),
                         'env_no': '12'}]
                    },
                   {'host': 'root@172.16.14.211:22', 'password': 'maitian123?',
                    'uplodList': [
                        {'android1': '{}/17环境.apk'.format(file_local_path), 'ios': '{}/17.ipa'.format(file_local_path),
                         'env_no': '17'}]
                    }]
    for host_config in host_config:
        conn = Connection(host_config['host'], connect_kwargs={"password": host_config['password']})
        for upload_dict in host_config['uplodList']:
            base_server_path = "/home/Application/fileStore/maimai/{}/default".format(upload_dict['env_no'])
            # 上传移动端app
            if ('android' in upload_dict.keys()):
                uploadApp(conn, upload_dict['android'], "{}/maimai.apk".format(base_server_path))
            if ('ios' in upload_dict.keys()):
                uploadApp(conn, upload_dict['ios'], "{}/maimai.ipa".format(base_server_path))
    print('finish>>>>')


def uploadApp(conn, local_file, server_file):
    conn.run("rm -rf {}".format(server_file))
    result = conn.put(local_file, remote=server_file)
    print("Uploaded app from 【{0.local}】 to 【{0.remote}】".format(result))


def taillog():
    con = Connection("root@172.16.14.62:2016", connect_kwargs={"password": "maitian123?"})
    with con.cd('/home/Application/tomcat-8081/logs'):
        con.run('tail -f catelina.out')


if __name__ == '__main__':
    main()
