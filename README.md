# ntp

## 介绍
基于Python编写，在海萤物联网提供校时服务。

本机地址是：
```text
0x2141000000000405
```

## 服务
服务号|服务
---|---
1|读取时间1
2|读取时间2.返回的是结构体

### 读取时间服务1
- CON请求：空或者带符号的1个字节。

当CON请求为空时，则默认为读取的是北京时间（时区8）。

也可以带1个字节表示时区号。这个字节是有符号的int8。

小技巧，可以使用0x100减去正值即负值。比如8对应的无符号数是0x100-8=248。

- ACK应答：当前时间的字符串

当前时间字符串的格式：2006-01-02 15:04:05 -0700 MST

### 读取时间服务2.返回的是结构体
- CON请求：格式与读取时间服务1一致

- ACK应答：
```c
struct {
    // 时区
    uint8 TimeZone
    uint16 Year
    uint8 Month
    uint8 Day
    uint8 Hour
    uint8 Minute
    uint8 Second
    // 星期
    uint8 Weekday
}
```

### 自定义错误码
错误码|含义
---|---
0x40|内部错误
0x41|接收格式错误

## 示例
### 读取时间
```python
resp, err = tziot.call(pipe, 0x2141000000000005, 1, 1000, bytearray())
print("err:", err, "time:", resp)
```

输出：
```text
err: 0 time: b'2021-03-22 10:06:09 +0800 MST'
```

### 读取时区为2的时间
```python
resp, err = tziot.call(pipe, 0x2141000000000005, 1, 1000, bytearray([2]))
print("err:", err, "time:", resp)
```

输出：
```text
err: 0 time: b'2021-03-22 04:07:20 +0200 MST'
```

### 读取时区为-6的时间
```python
resp, err = tziot.call(pipe, 0x2141000000000005, 1, 1000, bytearray([0x100 - 6]))
print("err:", err, "time:", resp)
```

输出：
```text
err: 0 time: b'2021-03-21 20:08:14 -0600 MST'
```

### 读取结构体格式时间
```python
import tziot
import sbc


class AckRidGetTime(sbc.LEFormat):
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
    pipe = tziot.bind_pipe_net(0x2141000000000401, pwd, '192.168.1.119', 12021)
    while not tziot.is_conn():
        pass
    resp, err = tziot.call(pipe, 0x2141000000000005, 2, 3000, bytearray())
    if err != 0:
        return

    ack = AckRidGetTime()
    if not ack.bytearray_to_struct(resp):
        return
    print(ack.time_zone, ack.year, ack.month, ack.day, ack.hour, ack.minute, ack.second, ack.weekday)


if __name__ == '__main__':
    main()
```

输出：
```text
8 2021 4 2 11 43 7 5
```
