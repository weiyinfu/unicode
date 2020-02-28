"""
每一个横向的字符占1个宽度，每个竖向字符占2两个宽度
"""
theme = [{
    "name": 'bold',
    "corner": ['┏', '┓', '┗', '┛'],  # 左上，右上，左下，右下
    'edge': ['┳', '┫', '┻', '┣'],  # 上右下左
    'center': '╋',
    'join': ['━━━', '┃']
}, {
    'name': 'common',
    'corner': ['┌', '┐', '└', '┘'],
    'edge': ['┬', '┤', '┴', '├'],
    'center': '┼',
    'join': ['───', '│'],
}]
big_chess = '⚪⚫'
small_chess = '○●'


class Board:
    def __init__(self, rows, cols, bold=False):
        self.th = theme[0] if bold else theme[1]
        self.a = [[' '] * cols for _ in range(rows)]
        a = self.a
        th = self.th
        self.rows = rows
        self.cols = cols
        a[0][0] = th['corner'][0]
        a[0][-1] = th['corner'][1]
        a[-1][0] = th['corner'][2]
        a[-1][-1] = th['corner'][3]
        for i in range(1, cols - 1):
            a[0][i] = th['edge'][0]
            a[-1][i] = th['edge'][2]
        for i in range(1, rows - 1):
            a[i][0] = th['edge'][3]
            a[i][-1] = th['edge'][1]
        for x in range(1, rows - 1):
            for y in range(1, cols - 1):
                a[x][y] = th['center']

    def put(self, x, y, ch):
        self.a[x][y] = ch
        return self

    def tos(self):
        h_sep = self.th['join'][0]
        c_sep = self.th['join'][1]
        col_sep = '\n' + (' ' * len(h_sep)).join([c_sep] * self.cols) + '\n'
        s = col_sep.join(self.th['join'][0].join(i) for i in self.a)
        return s


def international_chess(b: Board):
    # 国际象棋
    s = {0: '♖♘♗♕♔♗♘♖', 1: '♙♙♙♙♙♙♙♙', -1: '♜♞♝♚♛♝♞♜', -2: '♟♟♟♟♟♟♟♟'}
    for k, v in s.items():
        for j, chess in enumerate(v):
            b.put(k, j, chess)


for bold in (True, False):
    print('bold', bold)
    b = Board(8, 8, bold)
    international_chess(b)
    print(b.tos())

print(Board(9, 9).put(0, 0, 'a').put(3, 3, 'b').tos())
print(Board(9, 9, True).put(0, 0, 'c').put(3, 3, 'd').tos())
