# -*- coding:utf-8 -*-
from ClassType import *


def print_ls(i, s):
    if s[0] != 'Call' and s[0] != 'Par':
        print i, "\t", " (", s[0], " , ", s[1], " , ", s[2], " , ", s[3], ")"
    else:
        print i, "\t", s[0], "\t", s[1]


# 从栈顶开始填写当前待用活跃信息
def fill_active_info():
    i = exp_list.top
    while i in xrange(exp_list.base, exp_list.top+1):
        ls = exp_list.get(i)        # 每条中间代码（以list变量存储）
        j = 0
        for j in xrange(1, len(ls)):               # 如果参数不存在
            if ls[j] == '_' or ls[j] is None or ls[j].isdigit():
                j += 1
            else:
                if ls[j] not in Avalue.keys():     # 参数不在临时变量管理表中,需要加入管理
                    mem = table_stack.look_mem(ls[j])
                    Avalue[ls[j]] = Ava(mem)
                m = i + 1
                while m <= exp_list.top:            # 在后续中间代码中用到该变量
                    if ls[j] in exp_list.get(m):
                        Avalue[ls[j]].vlist.insert(0, m)  # 该变量出现的位置加入活跃信息链
                        break
                    m += 1
                j += 1
        if ls[0] == 'Par':
            Avalue[ls[1]].vlist.append(exp_list.top)
        i -= 1


# 每生成一条目标代码，需要更新一次待用活跃信息链
def refresh_active_info(index):
    for i in Avalue.keys():
        ls = Avalue[i].vlist     # 待用活跃信息编号<=当前正在处理的产生式编号
        if len(ls) and ls[0] <= index:          # 移除过时信息
            Avalue[i].vlist.remove(ls[0])


# 将当前寄存器中的变量存入内存，腾出寄存器
def store_reg(i):
    Register[i].flag = False  # 该寄存器被标记无效，里边的信息需要写回内存
    MEM.append(True)
    s = ['MOV', '['+str(MEM.top)+']', i]
    Avalue[Register[i].content].mem = '['+str(MEM.top)+']'
    Code.append(s)


# 判断一个变量在寄存器里还是内存里，有限返回寄存器位置信息
def judge_reg_or_men(s):
    temp = Avalue[s].reg   # 在寄存器里则返回寄存器
    try:
        if temp is not None and Register[temp].flag and Register[temp].content == s:
            return temp
        else:                  # 当前值只存在于内存里,返回内存
            return Avalue[s].mem
    except AttributeError, data:
        print data


# 获得一个变量的类型
def get_type(s):
    if s.isdigit():  # 是立即数的话返回自身
        return s
    else:
        return judge_reg_or_men(s)  # 在寄存器里返回寄存器


# 生成赋值语句代码
def gen_mov(s1, s2):
    temp = get_type(s2)
    s = ['MOV', s1, temp]
    Code.append(s)
    if s1 in Register.keys():
        Register[s1].content = s2
        Register[s1].flag = True
        Avalue[s2].reg = s1


# 获得一个寄存器
def get_register(name):
    k = Avalue[name].reg
    if k is not None:          # 该变量存在于寄存器中
        if Register[k].flag and Register[k].content == name:   # 并且寄存器中的值是有效的
            return k
    far_index = -1
    for i in Register.keys():  # 当前有空闲寄存器
        if Register[i].flag is False:
            gen_mov(i, name)
            return i
        n = Register[i].content  # 寄存器中当前存储的内容
        ls = Avalue[n].vlist     # 当前的活跃信息链
        if len(ls) == 0:         # 当前寄存器在后续没有被用到
            return i
        elif ls[0] > far_index:
            far_index = ls[0]
            best = i  # 最佳被替换的寄存器下标
    store_reg(best)                       # 替换寄存器
    gen_mov(best, name)
    Register[best].flag = True            # 寄存器繁忙
    return best


# 生成加减代码
def gen_add_sub(ss, func):
    temp = get_type(ss[2])
    if temp in Register.keys():
        Code.append([func, temp, get_type(ss[1])])
        Avalue[ss[3]].reg = temp    # 动态更新当前栈帧信息
        Register[temp].flag = True  # 寄存器繁忙
        Register[temp].content = ss[3]  # 加减的值暂存在寄存器里
    else:
        best = get_register(ss[1])
        Code.append([func, best, get_type(ss[2])])
        Avalue[ss[3]].reg = best  # 动态更新当前栈帧信息
        Register[best].flag = True  # 寄存器繁忙
        Register[best].content = ss[3]  # 加减的值暂存在寄存器里


# 生成乘除代码
def gen_mul_div(ss, func):          # 累乘器EAX被占用（不是被乘数）
    if Register['EAX'].flag and Register['EAX'].content != ss[1]:
        if len(Avalue[Register['EAX'].content].vlist):   # 寄存器中的变量后续还要用到
            store_reg('EAX')                             # 需要存储寄存器变量
        gen_mov('EAX', ss[1])       # 移动变量到寄存器里
    s = [func, get_type(ss[2])]      # 如果当前乘数在寄存器里
    Code.append(s)
    Avalue[ss[3]].reg = 'EAX'        # 动态更新当前栈帧信息
    Register['EAX'].flag = True      # 寄存器繁忙
    Register['EAX'].content = ss[3]  # 乘除的值暂存在寄存器里


# 生成跳转代码
def gen_jump(ss, func):
    if func == 'j':
        Code.append([code_list[func], None])
        lab_stack.append(Code.top)
        Code.append('Lab' + str(Code.lab) + ':')
        Code.lab += 1
    else:
        # s = "CMP\t" + temp1 + "," + temp2
        s = ['CMP', get_type(ss[1]), get_type(ss[2])]
        Code.append(s)
        s = [code_list[func], None]
        Code.append(s)
        lab_stack.append(Code.top)


# 获得当前函数调用入口
def get_entrance(tb):
    for i in func_entrance:
        if tb == i.id:          # 找到函数入口表名称
            return i
    return None


# 生成参数传递
def gen_transfer_call(index):
    start = index
    for index in xrange(start, exp_list.top + 1):
        ls = exp_list.get(index)
        if ls[0] == 'Call':                  # 处理当前参数调用
            tb = get_entrance(ls[1])         # 找到当前参数调用表的入口名称
            tl = 0
            if tb == None:
                return "Semantic Error!"
            for i in xrange(0, call_stack.top+1):  # 把实参的值传给形参单元
                if tl <= tb.parm:
                    mem = tb.vlist[tl].place  # 找到形参单元对应的内存
                    t = call_stack.pop()
                    if t == 'ECX':
                        Code.append(['MOV', '[' + str(mem) + ']', 'ECX'])
                    else:
                        gen_mov('[' + str(mem) + ']', t)
                    tl += 1
                else:
                    call_stack.append('ECX')
                    Code.append(['Call', tb.id])  # 生成Call调用
                    break
        else:
            call_stack.append(ls[1])
    Code.append(['Call', tb.id])
    return None


# 生成目标代码,正向生成
def gen_aim_code():
    for i in xrange(exp_list.base, exp_list.top + 1):
        ls = exp_list.get(i)  # 每条中间代码（以list变量存储）
        if ls[0] == '+':
            gen_add_sub(ls, 'ADD')
        elif ls[0] == '-':
            gen_add_sub(ls, 'SUB')
        elif ls[0] == '*':
            gen_mul_div(ls, 'MUL')
        elif ls[0] == '/':
            gen_mul_div(ls, 'DIV')
        elif ls[0] == '=':
            gen_mov(Avalue[ls[3]].mem, ls[1])
        elif ls[0] == 'Par' or ls[0] == 'Call':
            ret = gen_transfer_call(i)
            if ret is not None:
                return ret
            break
        else:
            gen_jump(ls, ls[0])
        refresh_active_info(i)
    return None


# 生成目标代码函数，以基本块为单位生成
def code_generate():
    if exp_list.top >= exp_list.base:  # 若有基本则需要处理基本块
        Avalue.clear()
        reg_reset()
        fill_active_info()
        ret = gen_aim_code()
        if ret is not None:
            return ret
        exp_list.base = exp_list.top + 1
    return None


