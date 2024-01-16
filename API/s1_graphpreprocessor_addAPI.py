# 处理实际各数据所对应的API图, 这份代码加上了没有在各查询语句中出现的API
import json
import pickle
import re
from APInameprocess_test import preprocess_api_name
from tree_sitter import Language, Parser, Node
# from test import code_parse


class variable_node:
    """变量节点，有如下属性：类型；值"""

    def __init__(self, id, type, value):
        # 格式：<int>.length
        self.id = id
        self.type = type
        self.value = value  # value是在代码里的实际的值
        self.str = "<{0}>.{1}".format(self.type, self.value)

    def toString(self):
        return "<{0}>.{1}".format(self.type, self.value)


class api_node:
    """API节点，有如下属性：类型；值；参数"""

    def __init__(self, id, name, clas, value, args):
        self.id = id
        self.name = name  # input
        self.clas = clas  # String
        self.value = value  # contains
        self.args = args  # ("o")
        self.receiver = "None"  # ("o")
        self.str = "{0}.{1}{2}#invoker:{3}#receiver:{4}".format(self.clas, self.value, self.args, self.name,
                                                                self.receiver)

    def update(self):
        self.str = "{0}.{1}{2}#invoker:{3}#receiver:{4}".format(self.clas, self.value, self.args, self.name,
                                                                self.receiver)

    def toString(self):
        print(
            "{0}.{1}{2}  invoker:{3}  receiver:{4}".format(self.clas, self.value, self.args, self.name, self.receiver))

    def nodetoken(self):
        return "{0}.{1}{2}".format(self.clas, self.value, self.args)


def tree_to_token_index(root_node):
    '''
    定位代码token，返回token在代码中原始位置

    从root_node开始，深度遍历其孩子节点：
    1. 如果root_node没有孩子（root_node是叶节点）或者root_node是字符串或者注释，直接返回code_snippet对应的位置
        个人猜想：
        估计某些编程语言的string和comment类型的语法树只有单引号、双引号叶子节点，而该节点内容被忽略掉了
    2. 如果有孩子节点，深度遍历，回溯时获取结果

    使用的属性:
    root_node.start_point: tuple[int, int]
    root_node.end_point: tuple[int, int]

    参数: root_node: Node

    返回: code_tokens: list[tuple[tuple[int,int], tuple[int, int]]]
    '''

    # 我突然发现该代码没有检测到cpp的string（也就是"hell world"），所以我改了第一行的第二个条件
    # 其他编程语言可能会有改变，所以需要小心谨慎
    # 原代码行：
    # if (len(root_node.children) == 0 or root_node.type == 'string') and root_node.type != 'comment':

    if (len(root_node.children) == 0 or root_node.type.find('string') != -1) and root_node.type != 'comment':
        return [(root_node.start_point, root_node.end_point)]
    else:
        code_tokens = []
        for child in root_node.children:
            code_tokens += tree_to_token_index(child)
        return code_tokens


def index_to_code_token(index, code):
    '''
    从 tree_to_token_index 返回的token位置元组列表 以及 代码行 生成代码token
    这里第二个参数，GraphCodeBert项目源代码写的是code，不是line_of_code

    1. 如果token起止都在同一行
        定位该代码行，定位改行的起止列，获取token
    2. token跨行【比如Python三个单引号包围的注释、或者Javascript中的模板字符串等等】
        1) 定位首行的token所在列
        2) 循环遍历到目标行之前，所有内容
        3) 定位末行的token所在列
        以上内容拼接即可

    参数: index: list[tuple[tuple[int,int], tuple[int, int]]]
    参数: code: list[str]

    返回: s: str
    '''
    start_point = index[0]
    end_point = index[1]
    if start_point[0] == end_point[0]:
        s = code[start_point[0]][start_point[1]:end_point[1]]
    else:
        s = ""
        s += code[start_point[0]][start_point[1]:]
        for i in range(start_point[0] + 1, end_point[0]):
            s += code[i]
        s += code[end_point[0]][:end_point[1]]
    return s


def code_parse(code, api_msg, sample_api_msg, num):
    tree = java_parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node
    # tokens_index = tree_to_token_index(root_node)
    java_loc = code.split('\n')
    # code_tokens = [index_to_code_token(x, java_loc) for x in tokens_index]

    list_var = []  # 存储变量节点
    list_api = []  # 存储api节点
    edge_invoker = []  # var_node -> api_node
    edge_receiver = []  # api_node -> var_node

    dict_id2var = {}  # 从id对应到var节点的字典
    idx_list_var = 0
    dict_name2var = {}  # 从变量名对应到var节点的字典

    dict_id2api = {}  # 从变量名对应到api节点的字典,但不管receiver
    idx_list_api = 0
    # 本地变量声明String input = "Hello World";
    java_query_text = '''
    (block(local_variable_declaration type:(_)@type_name declarator:(variable_declarator name:(identifier)@variable_name))@var_declare)
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "var_declare":
            continue
        node1, node2 = capture[i + 1][0], capture[i + 2][0]
        variable_type = index_to_code_token((node1.start_point, node1.end_point), java_loc)
        variable_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)
        # 新建var节点变量，需要在两个字典和一个列表中加入
        node_temp = variable_node(idx_list_var, variable_type, variable_value)
        dict_id2var[idx_list_var] = node_temp
        dict_name2var[variable_value] = node_temp
        idx_list_var += 1
        list_var.append(node_temp)

    # 把函数参数作为本地变量加进来findPLV(int M_PriceList_ID, int a, string s);
    java_query_text = '''
    (formal_parameter type:(_)@type name:(identifier)@method_name)
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "paramete":
            continue
        node1, node2 = capture[i + 1][0], capture[i + 2][0]
        variable_type = index_to_code_token((node1.start_point, node1.end_point), java_loc)
        variable_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)
        # 新建var节点变量，需要在两个字典和一个列表中加入
        node_temp = variable_node(idx_list_var, variable_type, variable_value)
        dict_id2var[idx_list_var] = node_temp
        dict_name2var[variable_value] = node_temp
        idx_list_var += 1
        list_var.append(node_temp)

    edge_args = []  # api_node -> var_node
    # 单纯的api被调用input.reversed(); invoker + api
    # java_query_text = '''
    # (method_invocation object: (identifier)@invoker name:(identifier)@method_name arguments:(argument_list)@args)@method_invoke
    # '''
    java_query_text = '''
    (expression_statement(method_invocation
    object: (_)@invoker 
	name:(identifier)@method_name 
	arguments:(argument_list)@args) @method_invoke)
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "method_invoke":
            continue
        node1, node2, node3 = capture[i + 1][0], capture[i + 2][0], capture[i + 3][0]
        api_invoker = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # invoker，input
        api_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # method_name，reversed
        api_args = index_to_code_token((node3.start_point, node3.end_point), java_loc)  # args
        if api_invoker in dict_name2var.keys():
            var_id = dict_name2var[api_invoker].id
            invoker_type = dict_name2var[api_invoker].type
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, invoker_type, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((var_id, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1
        else:
            # 没出现过，要新建变量，变量类型为""空值
            invoker_name = api_invoker
            node_temp = variable_node(idx_list_var, "", invoker_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[invoker_name] = node_temp
            list_var.append(node_temp)
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, api_invoker, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((idx_list_var, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1

    # api调用并赋予已存在变量，如str = input.toUpperCase();
    java_query_text = '''
    (assignment_expression left:(identifier)@variable_name right:(method_invocation object: (identifier)@invoker name:(identifier)@method_name arguments:(argument_list)@args))@variable_assignment
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "variable_assignment":
            continue
        node0, node1, node2, node3 = capture[i + 1][0], capture[i + 2][0], capture[i + 3][0], \
                                     capture[i + 4][0]
        receiver = index_to_code_token((node0.start_point, node0.end_point), java_loc)  # receiver
        api_invoker = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # invoker
        api_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # method_name
        api_args = index_to_code_token((node3.start_point, node3.end_point), java_loc)  # args

        # 把上面做过的事儿重新做一遍
        if api_invoker in dict_name2var.keys():
            var_id = dict_name2var[api_invoker].id
            invoker_type = dict_name2var[api_invoker].type
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, invoker_type, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((var_id, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1
        else:
            # 没出现过，要新建变量，变量类型为""空值
            invoker_name = api_invoker
            node_temp = variable_node(idx_list_var, "", invoker_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[invoker_name] = node_temp
            list_var.append(node_temp)
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, api_invoker, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((idx_list_var, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1

        if receiver in dict_name2var.keys():
            var_id = dict_name2var[receiver].id
            edge_receiver.append((idx_list_api - 1, var_id))
        else:
            # 没出现过，要新建变量，变量类型为""空值
            receiver_name = receiver
            node_temp = variable_node(idx_list_var, "", receiver_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[receiver_name] = node_temp
            list_var.append(node_temp)
            idx_list_var += 1
            edge_receiver.append((idx_list_api - 1, idx_list_var - 1))

    # api调用并赋予新定义变量，如int length = input.length();
    java_query_text = '''
    (block(local_variable_declaration 
    	type:(_)@type_name declarator:(variable_declarator 
      name:(identifier)@variable_name value:(method_invocation object: (identifier)@invoker name:(identifier)@method_name arguments:(argument_list)@args)))@var_declare_withmethod)
      '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "var_declare_withmethod":
            continue
        node0, node1, node2, node3 = capture[i + 2][0], capture[i + 3][0], \
                                     capture[i + 4][0], capture[i + 5][0]
        receiver = index_to_code_token((node0.start_point, node0.end_point), java_loc)  # receiver
        api_invoker = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # invoker
        api_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # method_name
        api_args = index_to_code_token((node3.start_point, node3.end_point), java_loc)  # args

        # 把上面做过的事儿重新做一遍
        if api_invoker in dict_name2var.keys():
            var_id = dict_name2var[api_invoker].id
            invoker_type = dict_name2var[api_invoker].type
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, invoker_type, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((var_id, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1
        else:
            # 没出现过，要新建变量，变量类型为""空值
            invoker_name = api_invoker
            node_temp = variable_node(idx_list_var, "", invoker_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[invoker_name] = node_temp
            list_var.append(node_temp)
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, api_invoker, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((idx_list_var, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1

        if receiver in dict_name2var.keys():
            var_id = dict_name2var[receiver].id
            edge_receiver.append((idx_list_api - 1, var_id))
        else:
            # 没出现过，要新建变量，变量类型为""空值
            receiver_name = receiver
            node_temp = variable_node(idx_list_var, "", receiver_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[receiver_name] = node_temp
            list_var.append(node_temp)
            idx_list_var += 1
            edge_receiver.append((idx_list_api - 1, idx_list_var - 1))

    # 构造函数返回给新建变量如StringBuilder sb = new StringBuilder();
    # 这个语句有点问题，处理不了MutableBigInteger q=new MutableBigInteger(), a2=new MutableBigInteger(a), b2=new MutableBigInteger(mod);
    java_query_text = '''
    (block(local_variable_declaration 
      type:(_)@type_name declarator:(variable_declarator 
      name:(identifier)@variable_name value:(object_creation_expression type:(type_identifier)@method_name 
        arguments:(argument_list)@args)@construct_method_assignmen)+)@var_declare_withconstructmethod
    )
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "var_declare_withconstructmethod":
            continue
        # print(capture[i])
        value = index_to_code_token((node.start_point, node.end_point), java_loc)
        # print("Node type: ", node.type, "Node alias: ", alias, "Node value:", value)
        node0, node1, node2, node3 = capture[i + 2][0], capture[i + 3][0], \
                                     capture[i + 4][0], capture[i + 5][0]
        receiver = index_to_code_token((node0.start_point, node0.end_point), java_loc)  # receiver sb
        # print("receiver: ",receiver)
        api_invoker = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # invoker new StringBuilder()
        # print("api_invoker: ", api_invoker)
        api_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # method_name StringBuilder
        # print("api_value: ", api_value)
        api_args = index_to_code_token((node3.start_point, node3.end_point), java_loc)  # args ()
        # print("api_args: ", api_args, "\n")
        # 构造函数节点 调用者调用类型及方法名都是StringBuilder
        node_temp = api_node(idx_list_api, api_value, api_value, api_value, api_args)
        list_api.append(node_temp)
        dict_id2api[idx_list_api] = node_temp
        idx_list_api += 1

        # 这个不需要invoker
        if receiver in dict_name2var.keys():
            var_id = dict_name2var[receiver].id
            edge_receiver.append((idx_list_api - 1, var_id))
        else:
            # 没出现过，要新建变量，变量类型为""空值
            # print(receiver)
            receiver_name = receiver
            node_temp = variable_node(idx_list_var, "", receiver_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[receiver_name] = node_temp
            list_var.append(node_temp)
            idx_list_var += 1
            edge_receiver.append((idx_list_api - 1, idx_list_var - 1))

    # 构造函数返回给已有变量如sf = new StringBuffer();
    java_query_text = '''
    (assignment_expression 
	left:(identifier)@variable_name 
    right:(object_creation_expression type:(type_identifier)@method_name 
    arguments:(argument_list)@args))@construct_assignment
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "construct_assignment":
            continue
        value = index_to_code_token((node.start_point, node.end_point), java_loc)
        # print("Node type: ", node.type, "Node alias: ", alias, "Node value:", value)
        node0, node1, node2 = capture[i + 1][0], capture[i + 2][0], capture[i + 3][0]
        receiver = index_to_code_token((node0.start_point, node0.end_point), java_loc)  # receiver sf
        api_value = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # method_name StringBuffer
        api_args = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # args ()
        # 构造函数节点 调用者调用类型及方法名都是StringBuilder
        node_temp = api_node(idx_list_api, api_value, api_value, api_value, api_args)
        list_api.append(node_temp)
        dict_id2api[idx_list_api] = node_temp
        idx_list_api += 1

        # 这个不需要invoker
        if receiver in dict_name2var.keys():
            var_id = dict_name2var[receiver].id
            edge_receiver.append((idx_list_api - 1, var_id))
        else:
            # 没出现过，要新建变量，变量类型为""空值
            receiver_name = receiver
            node_temp = variable_node(idx_list_var, "", receiver_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[receiver_name] = node_temp
            list_var.append(node_temp)
            idx_list_var += 1
            edge_receiver.append((idx_list_api - 1, idx_list_var - 1))

    # 在上面没有出现过的API统一加进来
    java_query_text = '''
            (method_invocation object: (identifier)@invoker name:(identifier)@method_name arguments:(argument_list)@args)@method_invoke
            '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "method_invoke":
            continue
        node1, node2, node3 = capture[i + 1][0], capture[i + 2][0], capture[i + 3][0]
        api_invoker = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # invoker
        api_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # method_name
        api_args = index_to_code_token((node3.start_point, node3.end_point), java_loc)  # args

        if api_invoker in dict_name2var.keys():
            var_id = dict_name2var[api_invoker].id
            invoker_type = dict_name2var[api_invoker].type
            api_str = "{0}.{1}{2}#invoker:{3}#receiver:{4}".format(invoker_type, api_value, api_args, api_invoker,
                                                                   "None")
            if api_str not in [api.str for api in list_api]:
                num += 1
                # 新建api节点变量，需要在列表中加入，在字典中加入
                node_temp = api_node(idx_list_api, api_invoker, invoker_type, api_value, api_args)
                list_api.append(node_temp)
                dict_id2api[idx_list_api] = node_temp
                # 加入到invoker边中
                edge_invoker.append((var_id, idx_list_api))
                idx_list_var += 1
                idx_list_api += 1
        else:
            num += 1
            # 没出现过，要新建变量，变量类型为""空值
            invoker_name = api_invoker
            node_temp = variable_node(idx_list_var, "", invoker_name)
            dict_id2var[idx_list_var] = node_temp
            dict_name2var[invoker_name] = node_temp
            list_var.append(node_temp)
            # 新建api节点变量，需要在列表中加入，在字典中加入
            node_temp = api_node(idx_list_api, api_invoker, api_invoker, api_value, api_args)
            list_api.append(node_temp)
            dict_id2api[idx_list_api] = node_temp
            # 加入到invoker边中
            edge_invoker.append((idx_list_var, idx_list_api))
            idx_list_var += 1
            idx_list_api += 1

    # print([i.str for i in list_var])
    # print([i.id for i in list_api])
    # print(edge_invoker)
    # print(edge_receiver)
    len_var = len(list_var)
    # print(len_var)
    list_node = []

    for n in list_var:
        list_node.append(n.toString())
    for a in list_api:
        list_node.append(a.nodetoken())

    edge_invoker_begin, edge_invoker_end = [], []
    for e in edge_invoker:
        edge_invoker_begin.append(e[0])
        edge_invoker_end.append(e[1] + len_var)

    edge_receiver_begin, edge_receiver_end = [], []
    for e in edge_receiver:
        edge_receiver_begin.append(e[0] + len_var)
        edge_receiver_end.append(e[1])

    idx_list_node = len(list_node)
    edge_des_begin, edge_des_end = [], []
    edge_return_begin, edge_return_end = [], []
    edge_corresponding_begin, edge_corresponding_end = [], []
    for a in list_api:
        edge_des_begin.append(a.id + len_var)
        edge_return_begin.append(a.id + len_var)
        s = a.nodetoken()
        ClassAndMethodName = s.split(".")[0]+"."+s.split(".")[1].split("(")[0]
        # description, return_type = "", ""
        if ClassAndMethodName not in api_msg.keys():
            if "." not in ClassAndMethodName:
                print(a.toString())
                print(ClassAndMethodName)
            if ClassAndMethodName.split(".")[1] in sample_api_msg.keys():
                # 加入max_pooling的api信息
                description = sample_api_msg[ClassAndMethodName.split(".")[1]]["description"]
                return_type = sample_api_msg[ClassAndMethodName.split(".")[1]]["return_description"]
            else:
                # 加入启发式规则生成的API描述
                _, description, return_type = preprocess_api_name(ClassAndMethodName.split(".")[1])
                # 不要启发式规则
                # description, return_type = "METHOD DESCRIPTION", "return_description"
        else:
            # 精确定位
            apimsg = api_msg[ClassAndMethodName]
            description = apimsg["des"]
            return_type = apimsg["return_description"]
        # 加入到边里面
        list_node.append(description)
        edge_des_end.append(idx_list_node)
        idx_list_node += 1

        list_node.append(return_type)
        edge_return_end.append(idx_list_node)
        if (a.id + len_var) in edge_receiver_begin:
            idx = edge_receiver_begin.index(a.id + len_var)
            edge_corresponding_begin.append(edge_receiver_end[idx])
            edge_corresponding_end.append(idx_list_node)
        idx_list_node += 1

    var_num = len(list_var)
    api_num = len(list_api)
    msg_num = len(list_node) - var_num - api_num

    node_type = [0] * var_num + [1] * api_num + [2] * msg_num
    edge_index_begin, edge_index_end = edge_receiver_begin + edge_invoker_begin + edge_des_begin + edge_return_begin + \
                                       edge_corresponding_begin, edge_receiver_end + edge_invoker_end + edge_des_end + \
                                       edge_return_end + edge_corresponding_end
    edge_index = [edge_index_begin, edge_index_end]
    edge_type = [0] * len(edge_receiver_begin) + [1] * len(edge_invoker_begin) + [2] * len(edge_des_begin) + \
                [3] * len(edge_return_begin) + [4] * len(edge_corresponding_begin)

    # 加入方法本体name作为唯一节点
    # 如果什么节点都没有会报错
    java_query_text = '''
    (program(local_variable_declaration
  declarator: (variable_declarator
    name: (identifier) @method_name)
))
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    if len(capture) != 0:
        node = capture[0][0]
        alias = capture[0][1]
        assert alias == "method_name"
        # 启发式规则
        _, description, return_type = preprocess_api_name(index_to_code_token((node.start_point, node.end_point), java_loc))
        # 不要启发式规则
        # description, return_type = "METHOD DESCRIPTION", "return_description"
        list_node.append(description)
        node_type.append(3)
    else:
        pattern = re.compile(r'\w+(?=\s*\()')
        # 在文本中查找匹配项
        match = pattern.search(code)
        if match:
            list_node.append(match.group(0))
        else:
            print(code)
            exit()
        node_type.append(3)

    return list_node, node_type, edge_index, edge_type, num


if __name__ == '__main__':
    JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
    PY_LANGUAGE = Language('build/my-languages.so', 'python')
    java_parser = Parser()
    java_parser.set_language(JAVA_LANGUAGE)

    with open("result/api_msg.pkl", 'rb') as f:
        api_msg = pickle.load(f)
    with open("result/sample_api_msg.pkl", 'rb') as f:
        sample_api_msg = pickle.load(f)  # 方法名不包含class时用这个
    num = 0
    datalist = ["test", "valid", "train"]
    for d in datalist:
        filename = "raw_data/" + d + "_data.json"
        with open(filename, 'r') as f:
            code_datas = json.load(f)
        for code_data in code_datas:
            code = code_data["code"]
            code_data["graph"] = {}
            # list_node, node_type, edge_index, edge_type, num = code_parse(code, api_msg, sample_api_msg, num)
            code_data["graph"]["node_inp"], code_data["graph"]["node_type"], code_data["graph"]["edge_index"], \
            code_data["graph"]["edge_type"], num = code_parse(code, api_msg, sample_api_msg, num)
        newfilename = "code_new2_rule/" + d + "_graphdata.json"
        with open(newfilename, 'w', encoding='utf-8') as f:
            json.dump(code_datas, f)
        print(d + "Finished！")
        print("新增:", num)
