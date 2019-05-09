# -*- coding:utf-8 -*-
import json
from LEX import token_recognize, word
from SemAly import sem_analyse
from ClassType import *

step = [0]        # 记录语法分析步骤栈
syn_list = []   # 为了输出格式对齐，先存一下语法分析栈
pre_dict = {}   # 以json方式读取预测分析表，并存为字典
with open("prelist.json", 'r') as f:
    pre_dict = json.load(f)
    f.close()


# 语法分析程序
def syn_analyse(str_line, syn_op, line_pos):
    if syn_op[0]:     # flag = true，把具体的id和数字换为ID/NUM
        if syn_op[2].typ == 'ID':
            syn_op[1] = 'ID'
        elif syn_op[2].typ == 'NUM':
            syn_op[1] = 'NUM'
        else:
            syn_op[1] = syn_op[2].value
        s = str(step[0])+'\t'+str(Syn_Stack)+'\t('+str(syn_op[1])+')\t'+str(syn_op[3])+'\n'
        # print s
        syn_list.append(s)    # 加入语法栈
        syn_op[3] = ""
        st_top = Syn_Stack.pop()
        if st_top not in pre_dict.keys():    # 如果st_top（即栈顶）是终结符
            if st_top == '#':
                if st_top == syn_op[1]:      # 程序正常结束
                    syn_op[0] = False
                else:
                    return 'Syn Error'       # 语法错误
            elif st_top == syn_op[1]:        # 如果是终结符的话，需要读入下一个字符
                syn_op[2] = token_recognize(str_line, line_pos)
            else:
                return 'Syn Error'
        else:      # 如果st_top（即栈顶）不是终结符
            if syn_op[1] in pre_dict.get(st_top):    # 查找预测分析表
                syn_op[3] = pre_dict[st_top][syn_op[1]]
                if syn_op[3]:                        # 表达式不空
                    ls = syn_op[3].split()           # 获取表达式并入语法分析栈
                    i = len(ls) - 1
                    while i:   # ls[i] 是表达式列表，需要逆向入栈
                        Syn_Stack.append(ls[i])
                        i -= 1
                else:
                    return sem_analyse(st_top)      # 需要执行相应的语义动作
                    syn_op[3] = ""
            else:
                return 'Syn Error'
    return None


def syn_write_to_file():   # 语法分析写入文件过程
    f_mdc = open(u'测试结果/语法分析.txt', 'w')
    f_mdc.write('由于语法栈中内容较多，为了便于区分，[]为语法栈内容，()为表达式内容\n\n')
    f_mdc.write('步骤\t[语法栈]\t(输入串)\t表达式\n')
    for l in syn_list:
        f_mdc.write(l)
    f_mdc.close()


def compile_main(filename):     # 编译器主程序
    initiative()  # 变量初始化
    f_input = open(filename, 'a+')
    f_input.write('#')
    f_input.seek(0)
    str_line = f_input.readline()
    line_pos = [1, 0, 1]        # 处理到的当前行编号 , 当前行下标 ,是否是注释
    syn_op = [True, None, None, None]  # 存储操作标志（判断是否注释），以及当前词
    step[0] = 0
    Syn_Stack.append('#')
    Syn_Stack.append('Prog')    # 初始化一个栈, 把开始符号#推入语法栈
    while str_line and syn_op[0]:
        if line_pos[2]:         # 不是注释
            syn_op[2] = token_recognize(str_line, line_pos)
            while syn_op[2] is not None and syn_op[0]:  # 元组存在
                res = syn_analyse(str_line, syn_op, line_pos)
                if res is not None:   # 语法分析错误，程序结束
                    print res, "in line", line_pos[0]
                    f_input.close()
                    return str(res)+'in line'+str(line_pos[0]+1)
                    syn_op[0] = 0
                    break
                step[0] += 1
            str_line = f_input.readline()
            line_pos[1] = 0
        else:
            line_pos[1] = -1
            while str_line and line_pos[1] == -1:   # 跳过形如 /* */的长注释
                str_line = f_input.readline()
                line_pos[0] += 1
                line_pos[1] = str_line.find('*/')
            line_pos[1] += 2
            line_pos[2] = True
    f_input.close()
    exp_list.write_to_file()
    Code.write_to_file()
    word.write_to_file()
    syn_write_to_file()
    return None