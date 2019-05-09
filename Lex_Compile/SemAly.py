# -*- coding:utf-8 -*-
from CodeGen import *
from ClassType import *
from LEX import word


# 建立一张新的变量声明表
def make_table(n1, t1):
    new_table = Stable(n1, t1, table_stack.get())
    table_stack.append(new_table)  # 把新的变量声明表入栈


# 将变量存入当前声明表
def add_var(n2, t2):
    t = table_stack.get()          # 获取当前声明表
    MEM.append(True)               # 分配内存
    t.push_var(LocVar(n2, t2, MEM.top))


# 判断变量是否存在于声明表
def judge_id(t):
    if t.type == 'ID' and table_stack.lookup(t.name) is False:
        return False
    else:
        return True


# 处理赋值表达式和加法表达式
def cope_exp():
    t3 = a_stack.pop()
    t2 = a_stack.pop()
    t1 = a_stack.pop()
    if judge_id(t1) and judge_id(t3):
        if t2.name == '=':
            s = [t2.name, t3.name, '_', t1.name]
            exp_list.append(s)
        else:
            temp = exp_list.pro_temp_index()
            s = [t2.name, t1.name, t3.name, temp]
            exp_list.append(s)
            a_stack.append(LocVar(temp, "Temp", None))   # 生成变量"T"的下标
        return None
    else:
        return "Semantic Error"


# 生成中间代码表达式
def generate_exp():
    if a_stack.top > 0:     # 表达式栈不空
        cope_exp()          # 生成中间代码表达式
    elif a_stack.top == 0:
        t = a_stack.pop()
        return None
    else:
        return None


# 生成跳转的中间代码
def generate_jump():
    if a_stack.top > 0:
        t3 = a_stack.pop()
        t2 = a_stack.pop()
        t1 = a_stack.pop()
        if judge_id(t1) and judge_id(t3):       # 优化跳转语句，只生成两条跳转语句
            if t2.name in op_list.keys():       # 生成与判断符号不同的跳转符号
                s = ['j'+op_list[t2.name], t1.name, t3.name, None]
                exp_list.append(s)              # 当前需要回填语句入口地址入栈
                back_stack.append(exp_list.top)
            return None
        else:
            return "Semantic Error"
    elif a_stack.top == 0:
        t = a_stack.pop()
        s = ['jz', t.name, '_', None]
        exp_list.append(s)
        back_stack.append(exp_list.top)        # 当前需要回填语句入栈
        return None
    else:
        return None


def back_patch_while():         # 回填while语句入口地址
    pos = back_stack.pop()
    s = ['j', '_', '_', str(pos)]
    exp_list.append(s)
    exp_list.back_patch(pos, exp_list.top+1)
    return None


def back_patch_if_else():       # 回填if-else语句,if入口地址
    pos = back_stack.pop()      # 中间代码入口地址
    # s = str(exp_list.top + 1) + "\t(j, _ , _ , " + "xxx)"
    exp_list.append(['j', '_', '_', None])    # 回填地址为下一个语句地址
    exp_list.back_patch(pos, exp_list.top+1)
    back_stack.append(exp_list.top)
    Code.back_patch(lab_stack.pop(), 'Lab' + str(Code.lab))  # 回填目标代码跳转地址


def generate_call():           # 生成call的参数
    if a_stack.top > 0:        # 表达式栈有待生成的表达式
        return cope_exp()
    elif a_stack.top == 0:     # 表达式栈顶是调用参数
        t = a_stack.pop()
        call_stack.append(LocVar(t.name, "Par", None))
    return None


# 生成call调用的名字
def call_end():
    while call_stack.top >= 0:
        t = call_stack.pop()
        if t.type == "Par":
            s = ['Par', t.name]
            exp_list.append(s)
        else:
            s = ['Call', t.name]
            exp_list.append(s)
    return None


# 语义分析和中间代码生成程序
def sem_analyse(act):
    if act == "Mtab":               # 新建一张符号表,扫描到if/else/while语句块
        ret = code_generate()                # 处理之前的语句块
        make_table(word.get_value(word.top-1), word.get_value(word.top - 2))
        return ret
    elif act == "Mpro":             # 新建一张符号表,扫描到一个新的函数
        w2 = word.get_value(word.top-1)
        make_table(w2, word.get_value(word.top - 2))
        if w2 == "main":
            Code.append("START:")
            Code.append(["MOV", 'AX', 'DATA'])
            Code.append(["MOV", 'DS', 'AX'])
        else:
            Code.append(w2.upper() + ' PROC NEAR ')
        return None
    elif act == "Pnum":             # 记下当前形参个数
        table_stack.settop()
    elif act == 'Ptbr':             # 处理完当前符号表, if/else语句块
        ret = code_generate()       # 需要对基本块进行代码生成
        table_stack.pop()
        return ret
    elif act == 'Jels':             # if语句块后含有else,需要生成绝对跳转语句
        back_patch_if_else()
        return None
    elif act == 'Bkpr':             # 处理完当前if-else语句块/if语句块，需要回填
        pos = back_stack.pop()      # 回填中间代码地址
        exp_list.back_patch(pos, exp_list.top+1)
        s = 'Lab'+str(Code.lab)
        Code.back_patch(lab_stack.pop(), s)   # 回填目标代码跳转地址
        Code.append(s+':')
        Code.lab += 1
        return None
    elif act =='Endr':              # return语句块结束
        ret = code_generate()
        w1 = word.get_value(word.top - 1)
        w2 = word.get_value(word.top - 2)
        if w2 == "return":  # 需要带回返回值,可能不在当前帧变量里
            if Avalue.has_key(w1):
                Code.append(['MOV', 'ECX', judge_reg_or_men(w1)])
            else:
                Code.append(['MOV', 'ECX', table_stack.look_mem('i')])
        elif w1 != 'return':
            ls = exp_list.get(exp_list.top)
            Code.append(['MOV', 'ECX', judge_reg_or_men(ls[3])])
        return ret
    elif act == 'Epro':           # 处理完当前函数, procedure
        ret = code_generate()           # 对出口基本块进行代码生成
        tb = table_stack.get()
        if tb.id == "main":
            Code.append("CODE ENDS")
            Code.append("END START")
        else:
            Code.append('RET')
            Code.append(tb.id.upper() + ' ENDP ')
        func_entrance.append(table_stack.pop())
        return ret                # 存储过程调用的入口地址
    elif act == "Advr":           # 将扫描到的变量加进符号表里
        add_var(word.get_value(word.top-1), word.get_value(word.top - 2))
        return None
    elif act == "Mexp":           # 新建一个表达式栈处理表达式
        while a_stack.top != -1:
            a_stack.pop()
        return None
    elif act == "Push":           # 将参数和操作方法推进表达式栈
        w = word.get(word.top)
        a_stack.append(LocVar(w.value, w.typ, None))
        return None
    elif act == "Upex":           # 表达式栈顶出现可生成中间代码项
        return generate_exp()
    elif act =="Mpsk":            # 建立一个过程调用参数调用栈
        call_stack.append(a_stack.pop())
        while a_stack.top != -1:
            a_stack.pop()
        return None
    elif act =="Upsk":            # 参数调用栈顶出现可生成中间代码项
        return generate_call()
    elif act =="Pcsk" and call_stack.top >= 0:  # 过程调用结束
        call_end()
        ret = code_generate()     # 处理过程调用
        return ret
    elif act =="Jexp":            # 生成跳转表达式
        return generate_jump()
    elif act =="Jwhl":            # while 语句块结束
        back_patch_while()        # 回填while语句地址
        ret = code_generate()  # 生成代码
        lat = lab_stack.pop()
        pre = lab_stack.pop()
        p = Code.stack[pre-2].split(':')
        Code.back_patch(lat, p[0])
        Code.back_patch(pre, 'Lab' + str(Code.lab-1))   # 回填目标代码跳转地址
        table_stack.pop()
        return ret

