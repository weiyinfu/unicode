import os
import json
from collections import Counter
from typing import List
from flask import redirect

from flask import Flask, jsonify, request, send_from_directory

"""
此网站是了解unicode的最佳窗口，但是知识只有自己探索出来才能认识深刻。本着重复造轮子的精神，在此研究unicode编码结构。
https://unicode-table.com/cn/

如果能够直接通过ttf字体文件直接识别不可显示区域就好了

运行方式，运行此程序，然后打开浏览器访问localhost:7777/index.html
"""

app = Flask(__name__)
curdir = os.path.abspath(os.path.dirname(__file__))
static_folder = os.path.join(curdir, '..', 'unicode_front')


def get_valid_chars():
    # 获取有效的字符
    b = []
    a = [(i, chr(i)) for i in range(0x110000)]
    for i in a:
        j = repr(i[1])
        j = j.strip("'")
        if j.startswith(r'\x') or j.startswith(r'\U') or j.startswith(r'\u'):
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


def split_by_char(a: List[tuple]):
    # 使用可打印字符分割unicode
    parts = []
    now = []
    for i in range(len(a)):
        if i + 1 < len(a) and a[i][0] + 1 == a[i + 1][0]:
            now.append(a[i])
        else:
            now.append(a[i])
            parts.append(now)
            now = []
    if now:
        parts.append(now)
    return parts


class Part:
    def __init__(self, beg: int, end: int, desc: str):
        self.beg = beg
        self.end = end
        self.desc = desc
        self.sub = []

    def contain(self, beg, end):
        return beg >= self.beg and end <= self.end

    def __str__(self):
        return f"{self.desc}[{self.beg},{self.end}]"

    def __repr__(self):
        return self.__str__()


part_desc = [
    {
        "name": "ASCII",
        "parts": [
            Part(0, 127, "ASCII（C0控制符及基本拉丁文）"),
            Part(ord('﹔'), ord('﹫'), '全角ASCII'),
            Part(ord('！'), ord('｠'), '全角ASCII2'),
        ]
    },

    {
        "name": '汉字',
        "parts": [
            Part(ord('⺀'), ord('⿕'), '汉字部首区'),
            Part(ord('㐀'), ord('䶵'), "汉字CJK Unified Ideographs Extension A"),
            Part(ord('一'), ord('鿕'), '简体汉字'),
            Part(ord('豈'), ord('舘'), '汉字二区'),
            Part(ord('並'), ord('龎'), '汉字三区'),
            Part(ord('㇀'), ord('㇣'), '笔画'),
            Part(0x3100, 0x312F, '汉语古典拼音'),
            Part(0x31A0, 0x31BF, '闽南话注音符号'),
            Part(0x2FF0, 0x2FFF, '汉语结构符号'),
        ]
    },

    {
        "name": "日语",
        "parts": [
            Part(ord("㌀"), ord('㍗'), 'Japanese Four'),
            Part(0x3040, 0x309F, '平假名'),
            Part(0x31F0, 0x31FF, '片假名拼音扩展'),
            Part(ord('㍱'), ord('㏟'), '日本多个字母'),
            Part(ord('ァ'), ord('ヿ'), '片假名'),
            Part(ord('、'), ord('〿'), '日语标点符号'),
            Part(ord('㋐'), ord('㋾'), '圆圈片假名'),
            Part(ord('｡'), ord('ﾾ'), '日语窄字符'),
        ]
    },
    {
        "name": '韩语',
        "parts": [
            Part(0x1100, 0x11FF, "韩语拼音"),
            Part(44032, 55203, '韩语文字'),
            Part(0x3130, 0x318F, '韩语兼容字母'),
            Part(ord('㈀'), ord('㈞'), '韩语圆圈文字'),
        ]
    },
    {
        "name": "不可显示",
        "parts": [
            Part(74880, 75075, "不可见字符1"),
            Part(93760, 93850, '不可见字符2'),
            Part(72971, 73007, '不可见字符3'),
            Part(82944, 83526, "不可见字符4"),
            Part(120832, 121483, '不可见字符5'),
            Part(94208, 111355, '不可见字符6'),
        ]
    },
    {
        "name": "象形文字",
        "parts": [
            Part(ord('𓀀'), ord('𓐮'), '埃及象形文字'),
            Part(ord('ⶀ'), ord('ⷞ'), '象形文字'),
            Part(ord('𐀀'), ord('𐃺'), '象形文字2'),
            Part(ord('𐘀'), ord('𐜶'), '象形文字3'),
            Part(ord('𐇐'), 66045, '象形文字4'),
            Part(ord('𖠀'), ord('𖨸'), '象形文字5'),
        ]
    },
    {
        "name": "图画",
        "parts": [
            Part(19904, 19967, '八卦'),
            Part(ord('🌀'), ord('🛶'), '图标'),
            Part(ord('🂠'), ord('🃟'), '扑克牌'),
            Part(ord('🀀'), ord('🂓'), '麻将'),
            Part(ord('🤐'), ord('🥞'), '表情图标区'),
            Part(ord('🜀'), ord('🟔'), '形状区'),
            Part(ord('🃠'), ord('🃵'), '奇特麻将'),
            Part(ord('─'), 10239, '棋盘符号'),
            Part(ord('⤀'), ord('⯯'), '箭头符号'),
            Part(ord("🠀"), ord('🢫'), '箭头'),
            Part(ord('←'), ord('␦'), '数学符号'),
            Part(ord('𝀀'), ord('𝇨'), '音乐符号'),
            Part(ord('྾'), ord('࿌'), '绣球'),
            Part(ord('࿎'), ord('࿚'), '万字')
        ]
    },
    {
        "name": "时间",
        "parts": [
            Part(ord("㏠"), ord("㏾"), "日期"),
            Part(ord("㍘"), ord("㍰"), "小时"),
            Part(ord('㋀'), ord('㋋'), '月份'),
        ]
    },
    {
        "name": "数字字母",
        "parts": [
            Part(ord('①'), ord('⒛'), '序号1到20'),
            Part(ord('𝟎'), ord('𝟿'), '数字'),
            Part(ord('𝐀'), ord('𝚣'), 'ABCD'),
            Part(ord('𝚨'), ord('𝟋'), '希腊字母'),
            Part(ord('⒜'), ord('⓿'), '字母数字加括号'),
            Part(ord('🄀'), ord('🉑'), '数字字母加边框区'),
            Part(ord('𝍠'), ord('𝍱'), '罗马数字'),
            Part(ord('À'), ord('ȳ'), '字母加音调'), Part(ord('𐄇'), ord('𐄳'), '数字2'),
        ]
    },
    {
        "name": "小语种",
        "parts": [
            {"name": "彝文", "parts": [
                Part(0xA000, 0xA48F, '彝文音节'),
                Part(0xA490, 0xA4CF, '彝文部首'),
            ]},
            Part(ord('𒀀'), ord('𒑳'), '楔形文字'), Part(ord('𞸃'), ord('𞻱'), '阿拉伯文'),
            Part(ord('ﰘ'), ord('﷽'), '阿拉伯文2'),
            Part(ord('𞡃'), ord('𞢉'), '不知名语言'),
            Part(ord('᐀'), ord('ᙿ'), '线点文'),
            Part(ord('ᚁ'), ord('᚜'), '线线文'),
            Part(ord('𐎀'), ord('𐏕'), '楔形文字2'),
            Part(ord('අ'), ord('ෆ'), '粗细笔画文'),
            Part(ord('𝈀'), ord('𝉅'), '奇怪字母'),
        ]
    },
    Part(0x2800, 0x28FF, '盲文符号'),
    Part(ord('𝌀'), ord('𝍖'), '点行区'),
    Part(ord('㈠'), ord('㊿'), '括号圆圈加汉字'),
    Part(ord('‐'), ord('‧'), '标点符号1'),
    Part(ord('‰'), ord('⁞'), '标点符号2'),
    Part(0xFE30, 0xFE4F, '竖形排版标点符号'),
    Part(ord('︐'), 0xFE1F, '汉语标点符号'),
]


def get_flat_parts():
    # 把树形结构的parts展平
    a = []

    def go(x):
        if type(x) == Part:
            a.append(x)
        else:
            for i in x['parts']:
                go(i)

    for i in part_desc:
        go(i)
    return a


def validate_parts(parts):
    # part_desc不能有重复描述
    cnt = Counter(i.desc for i in parts)
    for i in cnt:
        if cnt[i] > 1:
            print(i)
            raise Exception(f'multi part name {i}')
    a = [i for i in parts]
    a.sort(key=lambda x: x.beg)
    for i in range(len(a) - 1):
        if a[i].end >= a[i + 1].beg:
            print(f'两个区间有交集 {a[i]},{a[i + 1]}')
            raise Exception(f'两个区间有交集 {a[i]},{a[i + 1]}')


def see_chars(beg, end):
    # 查看一个区间中的全部字符
    print(''.join(chr(i) for i in range(beg, end + 1)))


def build_parts(flat_parts: List[Part]):
    # 给各个区间进行填充字符
    not_used = Part(-1, -1, '未使用')
    for i in a:
        father_part = []
        for j in flat_parts:
            if j.contain(i[0], i[0]):
                j.sub.append(i)
                father_part.append(j)
        used = len(father_part)
        assert used <= 1, f'a char can only belong to one part. {used} {father_part}'
        if used == 0:
            not_used.sub.append(i)
    print('not used count', len(not_used.sub))
    part_desc.append(not_used)
    flat_parts.append(not_used)


flat_parts = get_flat_parts()
validate_parts(flat_parts)
build_parts(flat_parts)
part_name2part = {i.desc: i for i in flat_parts}


@app.route("/api/parts")
def get_part_list():
    def go(x):
        if type(x) == Part:
            return {
                'desc': x.desc,
                'beg': x.beg,
                'end': x.end
            }
        else:
            a = []
            for i in x['parts']:
                a.append(go(i))
            return {
                'name': x['name'],
                'parts': a
            }

    a = []
    for i in part_desc:
        a.append(go(i))
    return jsonify(a)


@app.route("/api/get_part")
def get_part():
    part_name = request.args['part']
    part = part_name2part[part_name]
    subs = split_by_char(part.sub)
    for i, v in enumerate(subs):
        subs[i] = ''.join(i[1] for i in v)
    return jsonify({
        "beg": part.beg,
        "end": part.end,
        "desc": part.desc,
        "sub": subs
    })


@app.route("/<path:filename>")
def custom_static(filename):
    return send_from_directory(static_folder, filename)


@app.route("/")
def default_page():
    return redirect('/standard.html')


if __name__ == '__main__':
    app.run(debug=False, port=7777,host="0.0.0.0")
