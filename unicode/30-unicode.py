
"""
目前的unicode最多只到三字节。
unicode的字符范围是0～0x110000
如果超出此范围，则 chr() arg not in range(0x110000)
"""
a = [chr(i) for i in range(0x110000)]

r"""
只看其中的可打印字符，如果不可打印，则repr(i)会自动变成\U或者\x
"""
b = []
for i in a:
    j = repr(i)
    j = j.strip("'")
    if j.startswith(r'\x') or j.startswith(r'\U') or j.startswith(r'\u'):
        continue
    b.append(i)
print(len(a), '有效字符个数', len(b), 0x110000)
"""
可打印的unicode字符个数总共是137203个
"""
