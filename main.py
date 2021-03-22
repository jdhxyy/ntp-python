"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
网络校时服务
Authors: jdh99 <jdh821@163.com>
"""

import config

import tziot
import dcompy as dcom
import lagan
import time

from datetime import datetime, timezone, timedelta

TAG = 'ntp'

# 应用错误码
# 接收格式错误
ERROR_CODE_RX_FORMAT = 0x40

# rid号
RID_GET_TIME = 1


def main():
    config.init()

    lagan.load(0)
    lagan.set_filter_level(lagan.LEVEL_INFO)
    lagan.enable_color(True)

    tziot.bind_pipe_net(config.LOCAL_IA, config.local_pwd, config.LOCAL_IP, config.LOCAL_PORT)
    tziot.register(RID_GET_TIME, ntp_service)


def ntp_service(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
    """校时服务.返回值是应答和错误码.错误码为0表示回调成功,否则是错误码"""
    ip, port = dcom.pipe_to_addr(pipe)

    if len(req) == 0:
        time_zone = 8
    elif len(req) == 1:
        time_zone = req[0]
        if time_zone >= 0x80:
            time_zone = -(0x100 - time_zone)
    else:
        lagan.warn(TAG, "ip:%s port:%d ia:0x%x ntp failed.len is wrong:%d", ip, port, src_ia, len(req))
        return None, ERROR_CODE_RX_FORMAT

    now = datetime.utcnow() + timedelta(hours=time_zone)
    if time_zone >= 0:
        s = b'%04d-%02d-%02d %02d:%02d:%02d +%02d00 MST' % (now.year, now.month, now.day, now.hour, now.minute,
                                                            now.second, time_zone)
    else:
        s = b'%04d-%02d-%02d %02d:%02d:%02d -%02d00 MST' % (now.year, now.month, now.day, now.hour, now.minute,
                                                            now.second, -time_zone)
    lagan.info(TAG, 'ip:%s port:%d ntp time:%s', ip, port, s)
    return bytearray(s), 0


if __name__ == '__main__':
    main()
