#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time
from os import path
import paramiko

from config import logging_config, vmiss_us_remote_host, vmiss_us_remote_user, remote_user, remote_host


class ImagesUtil(object):
    def __init__(self):
        self._key_path = path.join(os.getcwd(), 'key\\wmiss_hk.pem')
        self._vmiss_us_key_path = path.join(os.getcwd(), 'key\\VMISSLosAngeles.pem')

    def upload_images_to_server(self, host, username, private_key_file_path, local_file_name, remote_file_path,
                                port=22):
        """
       将单个文件上传到远程服务器
       :param host: 服务器地址
       :param port: 服务器端口，空为默认 22
       :param username: 用户名
       :param local_file_name: 本地图片名称
       :param remote_file_path: 图片远程保存地址
       :param private_key_file_path: 登录服务器密钥文件路径
       :return:
       """
        port = int(port) if port else 22
        ssh = paramiko.SSHClient()
        private_key = paramiko.RSAKey.from_private_key_file(private_key_file_path)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pkey=private_key, hostname=host, port=port, username=username)
        sftp = ssh.open_sftp()
        # 本地文件路径
        local_file_path = path.join(os.getcwd(), 'files', local_file_name)
        # 检查远程目录是否存在
        stdin, stdout, stderr = ssh.exec_command(f'test -d {remote_file_path} && echo "Exists"')
        result = stdout.read().decode().strip()
        if result == 'Exists':
            # 目录存在，保存文件到远程目录
            sftp.put(local_file_path, f'{remote_file_path}/{local_file_name}')
        else:
            # 目录不存在，创建远程目录
            ssh.exec_command(f'mkdir -p {remote_file_path}')
            sftp.put(local_file_path, f'{remote_file_path}/{local_file_name}')
        sftp.close()
        ssh.close()

    def update_vmiss_us_server(self, local_file_name, remote_file_path):
        host = vmiss_us_remote_host
        username = vmiss_us_remote_user
        private_key_file_path = self._vmiss_us_key_path
        self.upload_images_to_server(host=host, username=username, private_key_file_path=private_key_file_path,
                                     local_file_name=local_file_name, remote_file_path=remote_file_path)

    def update_vmiss_hk_server(self, local_file_name, remote_file_path):
        host = remote_host
        username = remote_user
        private_key_file_path = self._key_path
        self.upload_images_to_server(host=host, username=username, private_key_file_path=private_key_file_path,
                                     local_file_name=local_file_name, remote_file_path=remote_file_path)

    def update_image_main(self, local_file_name, remote_file_path):
        self.update_vmiss_us_server(local_file_name=local_file_name, remote_file_path=remote_file_path)
        self.update_vmiss_hk_server(local_file_name=local_file_name, remote_file_path=remote_file_path)


class DeleteFileUtil(object):
    def __init__(self):
        logger_name = 'images_util'
        init_logging = logging_config.LoggingConfig()
        self._logging = init_logging.init_logging(logger_name)

    def delete_file(self, file_name):
        # 文件路径
        local_file_path = path.join(os.getcwd(), 'files', file_name)
        try:
            # 如果文件存在
            if os.path.exists(local_file_path):
                # 删除文件
                os.remove(local_file_path)
            else:
                # 则返回文件不存在
                self._logging.error('no such file:%s' % file_name)
        except PermissionError:
            # 处理权限错误
            self._logging.error('PermissionError: 另一个程序正在使用此文件。等待1秒后重试...')



