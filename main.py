"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
网络校时服务
Authors: jdh99 <jdh821@163.com>
"""

import config

import tziot
import dcompy as dcom
import lagan
import sbc

from datetime import datetime, timedelta

TAG = 'ntp'

# 应用错误码
# 内部错误
ERROR_CODE_INTERNAL_ERROR = 0x40
# 接收格式错误
ERROR_CODE_RX_FORMAT = 0x41

# rid号
# 读取时间.返回的是字符串
RID_GET_TIME1 = 1
# 读取时间.返回的是结构体
RID_GET_TIME2 = 2


class AckRidGetTime2(sbc.LEFormat):
    _fields_ = [
        # (字段名, c类型)
        # 时区
        ('time_zone', sbc.c_uint8),
        ('year', sbc.c_int16),
        ('month', sbc.c_uint8),
        ('day', sbc.c_uint8),
        ('hour', sbc.c_uint8),
        ('minute', sbc.c_uint8),
        ('second', sbc.c_uint8),
        # 星期
        ('weekday', sbc.c_uint8),
    ]


def main():
    config.init()

    lagan.load(0)
    lagan.set_filter_level(lagan.LEVEL_INFO)
    lagan.enable_color(True)
    dcom.set_filter_level(lagan.LEVEL_WARN)

    tziot.bind_pipe_net(config.LOCAL_IA, config.local_pwd, config.LOCAL_IP, config.LOCAL_PORT)
    tziot.register(RID_GET_TIME1, ntp_service1)
    tziot.register(RID_GET_TIME2, ntp_service2)


def ntp_service1(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
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
        s = '%04d-%02d-%02d %02d:%02d:%02d +%02d00 MST' % (now.year, now.month, now.day, now.hour, now.minute,
                                                            now.second, time_zone)
    else:
        s = '%04d-%02d-%02d %02d:%02d:%02d -%02d00 MST' % (now.year, now.month, now.day, now.hour, now.minute,
                                                            now.second, -time_zone)
    lagan.info(TAG, 'ip:%s port:%d ntp time:%s', ip, port, s)
    return tziot.str_to_bytearray(s), 0


def ntp_service2(pipe: int, src_ia: int, req: bytearray) -> (bytearray, int):
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
    t = AckRidGetTime2()
    t.time_zone = time_zone
    t.year = now.year
    t.month = now.month
    t.day = now.day
    t.hour = now.hour
    t.minute = now.minute
    t.second = now.second
    t.weekday = now.isoweekday()
    lagan.info(TAG, 'ip:%s port:%d ntp time:%04d-%02d-%02d %02d:%02d:%02d +%02d00 MST', ip, port, t.year, t.month,
               t.day, t.hour, t.minute, t.second, t.time_zone)
    return t.struct_to_bytearray(), 0


if __name__ == '__main__':
    main()
