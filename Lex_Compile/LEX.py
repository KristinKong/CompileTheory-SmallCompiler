# -*- coding:utf-8 -*-
import collections
import re
Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])
keywords = {'int', 'void', 'if', 'else', 'while', 'return'}


# 存储识别出来的单词栈
class Word:
    def __init__(self):
        self.top = -1
        self.wist = []

    def append(self, w):
        self.top += 1
        self.wist.append(w)

    def get_value(self, index):
        return self.wist[index].value

    def get(self, index):
        return self.wist[index]

    def write_to_file(self):    # 分词结果写入文件
        fp = open(u'测试结果/词法分析.txt', 'w')
        for s in self.wist:
            fp.write(str(s)+'\n')
        fp.close()


token_regulate = [                          # 正则表达式规则构成（用来识别出一个个的单词）
        ('START', r'(/\*)|(//)'),
        ('ID', r'[a-zA-Z]+[a-zA-z0-9]*'),   # 匹配id
        ('NUM', r'\d+'),                    # 匹配整型数字
        ('RANGE', r'[,;#(){}]'),            # 匹配 ;
        ('OP', r'(==)|(>=)|(<=)|(!=)|[-+*/><]'),
        ('ASSIGN', r'='),                   # 匹配 =
        ('NEWLINE', r'\n'),                 # 匹配换行
        ('SKIP', r'[ \t]+')                 # 匹配空格或tab键
    ]
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_regulate)
get_token = re.compile(tok_regex).match
word = Word()   # 存储所有单词的栈


# 识别出每个单词，并返回识别出单词的元组
def token_recognize(s, lipos):
    mo = get_token(s, lipos[1])
    if mo is not None:
        typ = mo.lastgroup                  # 跳过空格tab等
        while typ == 'SKIP' and mo is not None:
            lipos[1] = mo.end()
            mo = get_token(s, lipos[1])
            typ = mo.lastgroup
        if typ == 'NEWLINE':                # 该行不用处理，跳过换行和短注释
            lipos[0] += 1
            if mo.end() != len(s):
                raise RuntimeError('Unexpected character %r on line %d' % (s[lipos[1]], lipos[0]))
            return None
        elif typ == 'START':                # 注释开始，跳过长注释
            if mo.group(typ) == '/*':
                lipos[2] = False
            lipos[0] += 1
            return None
        else:                               # 有效单词，返回识别出来的词
            val = mo.group(typ)
            if typ == 'ID' and val in keywords:
                typ = val
            lipos[1] = mo.end()
            word.append(Token(typ, val, lipos[0], mo.start()))
            return Token(typ, val, lipos[0], mo.start())