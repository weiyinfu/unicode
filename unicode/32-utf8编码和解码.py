import io

from tqdm import tqdm

"""
大头序，小头序

   |  Unicode符号范围      |  UTF-8编码方式  
 n |  (十六进制)           | (二进制)  
---+-----------------------+------------------------------------------------------  
 1 | 0000 0000 - 0000 007F |                                              0xxxxxxx  
 2 | 0000 0080 - 0000 07FF |                                     110xxxxx 10xxxxxx  
 3 | 0000 0800 - 0000 FFFF |                            1110xxxx 10xxxxxx 10xxxxxx  
 4 | 0001 0000 - 0010 FFFF |                   11110xxx 10xxxxxx 10xxxxxx 10xxxxxx  
 5 | 0020 0000 - 03FF FFFF |          111110xx 10xxxxxx 10xxxxxx 10xxxxxx 10xxxxxx  
 6 | 0400 0000 - 7FFF FFFF | 1111110x 10xxxxxx 10xxxxxx 10xxxxxx 10xxxxxx 10xxxxxx 

utf8只有第一个字节比较特殊，其它字节都很规范
utf8以字节为单位进行编码，开头最多是1111110x，这就限制了utf8最多使用6个字节表示。

utf8认为unicode最多有2^32个，超出此范围则utf8无法表示unicode
"""
print("utf8最多使用6个字节表示一个字符,utf8可以表示的字符个数 %s" % (
        2 ** 7
        + 2 ** (6 + 5)
        + 2 ** (12 + 4)
        + 2 ** (16 + 3)
        + 2 ** (20 + 2)
        + 2 ** (24 + 2)
        + 2 ** (30 + 1)
))

ind = list(range(0x110000))
a = [chr(i) for i in ind]


def int2byte(x: int):
    # 把int转成bytes
    return x.to_bytes(1, "big")


def enc(s: str):
    # 把字符s编码为utf8的bytes
    x = ord(s)
    if x < 128:
        return int2byte(x)
    o = io.BytesIO()
    bit_count = x.bit_length()
    assert bit_count <= 31
    byte_count = bit_count // 6 + 1
    if bit_count % 6 + byte_count + 1 > 8:
        # 如果最后一个字节的前导1放不开，那就需要额外一个字节
        byte_count += 1
    a = []
    for i in range(byte_count - 1):
        a.append(x & 0b00111111)
        x >>= 6
    mask = ((1 << byte_count) - 1) << (8 - byte_count)
    o.write(int2byte(mask | x))
    for v in a[::-1]:
        o.write(int2byte(0b10000000 | v))
    return o.getvalue()


def dec(b: bytes):
    if len(b) == 1:
        return chr(b[0])
    head_ones = 0
    for i in range(7, -1, -1):
        if b[0] & (1 << i):
            head_ones += 1
        else:
            break
    assert head_ones == len(b), "前导1的个数等于bytes个数%s" % head_ones
    for i in range(1, len(b)):
        assert (b[i] >> 6) == 0b10
    x = b[0] & ((1 << (7 - head_ones)) - 1)
    for i in range(1, len(b)):
        x = (x << 6) | (b[i] & 0b00111111)
    return chr(x)


def bytes2str(b: bytes):
    a = []
    for i in b:
        a.append(bin(i)[2:])
    return ",".join(a)


def test():
    b = [0] * len(ind)
    for ii, i in enumerate(a):
        try:
            b[ii] = bytes(i, "utf8")
        except:
            """
            为什么此处会抛出异常？
            因为0xD800～0xDFFF这2048(0x7FF)个字符用作其它用途。
            unicode设计之初，委员会认为0～FFFF两个字节共65536个字符足以表示地球上的所有字符，在内存中只需要2个字节就能表示一个字符。
            但不久之后发现65536个字符远远不够，在内存中需要用大于2个字节表示utf8字符，因此使用0xD800～0xDFFF作为扩展区域。
            """
            pass
    valid_b = [i for i in b if i]
    print(len(a), len(valid_b))

    for i in tqdm(range(len(a))):
        if not b[i]:
            continue
        mine = enc(a[i])
        dec_value = dec(mine)
        # print(bin(ind[i]), bytes2str(b[i]), bytes2str(mine), bin(ord(dec_value)))
        assert dec_value == a[i]
        assert b[i] == mine
    print("check over ")


test()
