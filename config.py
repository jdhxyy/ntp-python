"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
配置文件
Authors: jdh99 <jdh821@163.com>
"""

# 系统参数
LOCAL_IA = 0x2141000000000005
LOCAL_IP = '0.0.0.0'
LOCAL_PORT = 12931

local_pwd = ''


def init():
    global local_pwd
    print('please input password:')
    local_pwd = input()
