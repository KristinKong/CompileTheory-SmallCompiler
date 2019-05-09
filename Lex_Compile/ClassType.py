# -*- coding:utf-8 -*-
import collections

op_list = {"==": "!=", "!=": "==", ">": "<", ">=": "<=", "<": ">", "<=": ">="}
code_list = {"j": "JMP", "j==": "JE", "j!=": "JNE", "j>": "JG", "j>=": "JGE", "j<": "JL", "j<=": "JLE"}

# 声明表中的元组类型(类似于不可改变的类）
LocVar = collections.namedtuple('LocVar', ['name', 'type', 'place'])


# 定义寄存器类
class Reg:
    def __init__(self):
        self.flag = False    # 寄存器可用与否的标志
        self.content = None  # 寄存器中存储内容

    def reset(self):         # 寄存器重置函数，当前帧处理完后寄存器可再分配
        self.flag = False
        self.content = None


# 寄存器变量初始化
def reg_reset():
    for i in Register.keys():
        Register[i].reset()


# 定义当前栈帧活动变量类
class Ava:
    def __init__(self):
        self.reg = None      # 当前变量所在的寄存器
        self.mem = None      # 当前变量所在的内存
        self.vlist = []      # 当前变量的待用活跃信息

    def __init__(self, mem):
        self.mem = '[' + str(mem) + ']'
        self.reg = None
        self.vlist = []

# 寄存器数组
Register = {'EAX': Reg(), 'EBX': Reg(), 'ECX': Reg(), 'EDX': Reg()}
# 临时变量栈帧
Avalue={}


# 定义普通的栈操作类
class Gtack:
    def __init__(self):         # 构造函数
        self.top = -1           # 栈顶元素下标
        self.lab = 0            # 跳转标签
        self.prtb = ''          # 当前处理的函数调用表名称
        self.stack = []

    def append(self, w):        # 栈顶添加一个元素
        self.top += 1
        self.stack.append(w)

    def pop(self):              # 栈顶元素出栈
        self.top -= 1
        return self.stack.pop()

    def find(self, w):          # 当前变量是否在寄存器中
        i = 0
        while i in xrange(0, self.top + 1):
            if self.stack[i].content == w:
                return i
        return -1

    def back_patch(self, p, lab):   # 目标代码标签回填
        self.stack[p][1] = lab

    def print_code(self):           # 打印生成的目标代码
        for s in self.stack:
            print s

    def write_to_file(self):        # 目标代码写入文件
        fp = open(u'测试结果/目标代码.txt', 'w')
        i = 0
        for s in self.stack:
            if type(s) is str:
                fp.write((s+'\n'))
            elif len(s) is 2:
                fp.write('\t'+(str(s[0])+'\t'+str(s[1])+'\n'))
            else:
                fp.write('\t'+(str(s[0])+'\t'+str(s[1])+','+str(s[2])+'\n'))
            i += 1
        fp.close()

    def clear(self):
        self.top = -1  # 栈顶元素下标
        self.lab = 0  # 跳转标签
        self.prtb = ''  # 当前处理的函数调用表名称
        self.stack = []



# 存储一张声明表
class Stable:
    def __init__(self, fid, ftyp, index):
        self.id = fid          # 声明表名字
        self.typ = ftyp        # 声明表类型
        self.parent = index    # 声明表父节点
        self.lenth = -1        # 当前声明表的长度
        self.parm = 0          # 当前形参个数
        self.vlist = []

    def setparm(self):         # 记下当前形参个数
        self.parm = self.lenth

    def push_var(self, wd):    # 把局部变量存入当前声明表
        self.vlist.append(wd)
        self.lenth += 1

    def find(self, n1):        # 查找变量id是否存在于当前声明表中
        for i in self.vlist:
            if i.name == n1:
                return True
        return False

    def find_mem_loc(self, na):  # 查询当前变量是否存在，若存在，返回内存地址
        for i in self.vlist:
            if i.name == na:
                return i.place
        return None


# 定义一个栈,存储声明表栈帧
class Tack:
    def __init__(self):
        self.top = -1
        self.stack = []

    def append(self, s):        # 向栈中添加一个元素
        self.top += 1
        self.stack.append(s)

    def pop(self):              # 将栈顶元素pop出栈
        self.top -= 1
        return self.stack.pop()

    def get(self):              # 获得栈顶元素
        return self.stack[self.top]

    def settop(self):
        self.stack[self.top].setparm()

    def get_name(self):
        return self.stack[self.top].id

    def lookup(self, n1):       # 寻找声明表中有无该变量
        stemp = self.get()
        while stemp is not None:
            if stemp.find(n1):
                return True
            else:
                stemp = stemp.parent
        return False

    def look_active(self, n1):  # 查询变量出口是否活跃,从父节点开始查
        stemp = self.get()
        stemp = stemp.parent
        while stemp is not None:
            if stemp.find(n1):
                return True
            else:
                stemp = stemp.parent
        return False

    def look_mem(self, na):    # 查询该变量在内存中是否定义
        stemp = self.get()
        while stemp is not None:
            ret = stemp.find_mem_loc(na)
            if ret is not None:
                return ret
            else:
                stemp = stemp.parent
        return -1

    def clear(self):
        self.top = -1
        self.stack = []


# 中间代码生成类
class Prex:
    def __init__(self):
        self.base = 0          # 存储中间代码块的起始下标
        self.top = -1          # 存储中间代码块的当前栈顶下标
        self.t_dex = -1        # 存储中间代码临时变量T的下标
        self.stack = []        # 存储中间代码的栈

    def append(self, w):       # 追加一个元素到栈顶
        self.top += 1
        self.stack.append(w)

    def pop(self):             # 栈顶弹出一个元素
        self.top -= 1
        return self.stack.pop()

    def get(self, index):      # 获得相应下标的栈中元素
        return self.stack[index]

    def pro_temp_index(self):  # 产生临时变量T
        self.t_dex += 1
        return "T" + str(self.t_dex)

    def back_patch(self, ex_index, aim_index):      # 回填中间代码编号
        self.stack[ex_index][3] = str(aim_index)

    def print_list(self):
        i = 0
        for i in xrange(0, self.top+1):
            s = self.stack[i]
            if s[0] != 'Call' and s[0] != 'Par':
                print i, "\t", " (", s[0], " , ", s[1], " , ", s[2], " , ", s[3], ")"
            else:
                print i, "\t", s[0], "\t", s[1]

    def write_to_file(self):
        fp = open(u'测试结果/中间代码.txt', 'w')
        i = 0
        for s in self.stack:
            if s[0] != 'Call' and s[0] != 'Par':
                fp.write((str(i)+"\t("+str(s[0])+" , "+str(s[1])+" , "+str(s[2])+" , "+str(s[3])+")\n"))
            else:
                fp.write((str(i)+"\t"+str(s[0])+"\t"+str(s[1])+'\n'))
            i += 1
        fp.close()

    def clear(self):
        self.base = 0          # 存储中间代码块的起始下标
        self.top = -1          # 存储中间代码块的当前栈顶下标
        self.t_dex = -1        # 存储中间代码临时变量T的下标
        self.stack = []        # 存储中间代码的栈


table_stack = Tack()
table_stack.append(None)   # 声明表处理栈
table_stack.append(Stable('Glob', 'static', None))
func_entrance = []         # 存储函数调用入口地址
a_stack = Tack()           # 处理表达式的栈
call_stack = Tack()        # 处理函数调用参数
exp_list = Prex()          # 存储所有的表达式
back_stack = []            # 存储中间代码回填的入口
lab_stack = []             # 存储目标代码回填的地址和编号
MEM = Tack()               # 可用待分配内存
Code = Gtack()             # 生成目标代码
Syn_Stack = []             # 语法栈


def ord_clear(a):
    while len(a):
        a.pop()


def initiative():
    table_stack.clear()
    table_stack.append(None)  # 声明表处理栈
    table_stack.append(Stable('Glob', 'static', None))
    ord_clear(func_entrance)
    a_stack.clear()
    call_stack.clear()
    exp_list.clear()
    ord_clear(back_stack)
    ord_clear(lab_stack)
    MEM.clear()
    Code.clear()
    ord_clear(Syn_Stack)
