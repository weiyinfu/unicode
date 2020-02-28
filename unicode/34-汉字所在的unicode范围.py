from poem.corpus import hanzi

"""
验证全部汉字都在某个区域内，此处需要一个字典文件
"""


def get_valid_chars():
    b = []
    a = [(i, chr(i)) for i in range(0x110000)]
    for i in a:
        j = repr(i[1])
        j = j.strip("'")
        if j.startswith(r"\x") or j.startswith(r"\U") or j.startswith(r"\u"):
            continue
        if 0xD800 <= i[0] <= 0xDFFF:
            # unicode扩展字符
            continue
        if i[0] > 129374:
            # 大于此值的都是无法正常显示的字符
            continue
        b.append(i)
    return b


a = get_valid_chars()
print("valid char count", len(a))


def get_all_zi():
    a = set()
    for i in hanzi.yinzi_without_tone:
        for z in i[1]:
            a.add(z)
    return a


def simple_chinese_contain_all_chinese():
    zi = get_all_zi()
    simple_range = [19968, 40917]
    bad_list = "〇"  # 黑名单，黑名单上的符号不属于汉字
    for i in zi:
        if i in bad_list:
            continue
        if not 19968 <= ord(i) <= 40917:
            print(i)
    print("简体中文区", simple_range, [hex(i) for i in simple_range])
    print("简体中文区字符个数", simple_range[1] - simple_range[0])
    print("字典中汉字个数", len(zi))
    print("字典中没有的字", "".join(set([chr(i) for i in range(19968, 40918)]) - set(zi)))
    print("字典中有但是不在区域的字", "".join(set(zi) - set([chr(i) for i in range(19968, 40918)])))


simple_chinese_contain_all_chinese()  # 进一步验证简体中文区包含全部汉字
"""
结论：
字典中全部汉字总共20377个，人类有史以来的字符个数为75971个，Unicode中字符个数20949个。
除了〇这个符号，字典中的全部字符都位于['0x4e00', '0x9fd5']
"""
