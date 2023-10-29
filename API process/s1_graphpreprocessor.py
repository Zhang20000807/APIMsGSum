import json
import pickle

from tree_sitter import Language, Parser, Node


class variable_node:
    """变量节点，有如下属性：类型；值"""

    def __init__(self, type, value):
        # 格式：<int>.length
        self.type = type
        self.value = value  # value是在代码里的实际的值
        self.str = "<{0}>.{1}".format(self.type, self.value)

    def toString(self):
        return "<{0}>.{1}".format(self.type, self.value)


class api_node:
    """API节点，有如下属性：类型；值；参数"""

    def __init__(self, name, clas, value, args):
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


def code_parse(code, api_msg, sample_api_msg):
    tree = java_parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node
    tokens_index = tree_to_token_index(root_node)
    java_loc = code.split('\n')
    code_tokens = [index_to_code_token(x, java_loc) for x in tokens_index]

    list_var = []  # 存储变量节点
    dict_var = {}
    dict_name2class = {}  # 从变量名对应到var节点的字典
    dict_name2api = {}  # 从变量名对应到api节点的字典,但不管receiver
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
        dict_name2class[variable_value] = variable_node(variable_type, variable_value)
        list_var.append(variable_node(variable_type, variable_value))
    # for idx, n in enumerate(list_var):
    #     dict_var[n] = idx

    list_api = []  # 存储api节点
    edge_invoker = []  # api_node -> var_node
    edge_receiver = []  # api_node -> var_node
    edge_args = []  # api_node -> var_node
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
        if api_invoker in dict_name2class.keys():
            api_class = dict_name2class[api_invoker].type
            edge_invoker.append((api_node(api_invoker, api_class, api_value, api_args), dict_name2class[api_invoker]))
        elif api_invoker in ["System", "log"]:
            api_class = api_invoker
            var_node = variable_node("Object", api_class)
            list_var.append(var_node)
            edge_invoker.append((api_node(api_invoker, api_class, api_value, api_args), var_node))
        else:
            api_class = api_invoker
            var_node = variable_node("Object", api_class)
            list_var.append(var_node)
            edge_invoker.append((api_node(api_invoker, api_class, api_value, api_args), var_node))
        apinode = api_node(api_invoker, api_class, api_value, api_args)
        list_api.append(apinode)
        dict_name2api[apinode.str] = apinode

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
        if api_invoker in dict_name2class.keys():
            api_class = dict_name2class[api_invoker].type
        elif api_invoker in ["System", "log"]:
            api_class = api_invoker
        else:
            api_class = api_invoker
        tempnode = api_node(api_invoker, api_class, api_value, api_args)
        if receiver in dict_name2class.keys() and tempnode.str in dict_name2api.keys():
            # dict_name2api[tempnode.str].receiver = receiver # 字典中不管receiver，不同receiver共用一个api节点
            # dict_name2api[tempnode.str].update()
            edge_receiver.append((dict_name2api[tempnode.str], dict_name2class[receiver]))

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
        if api_invoker in dict_name2class.keys():
            api_class = dict_name2class[api_invoker].type
        elif api_invoker in ["System", "log"]:
            api_class = api_invoker
        else:
            api_class = api_invoker
        tempnode = api_node(api_invoker, api_class, api_value, api_args)
        if receiver in dict_name2class.keys() and tempnode.str in dict_name2api.keys():
            # dict_name2api[tempnode.str].receiver = receiver
            edge_receiver.append((dict_name2api[tempnode.str], dict_name2class[receiver]))

    java_query_text = '''
    (block(local_variable_declaration 
      type:(_)@type_name declarator:(variable_declarator 
      name:(identifier)@variable_name value:(object_creation_expression type:(type_identifier)@method_name 
        arguments:(argument_list)@args)@construct_method_assignmen))@var_declare_withconstructmethod)
    '''
    query = JAVA_LANGUAGE.query(java_query_text)
    # capture: list[Node, str]
    capture = query.captures(root_node)
    for i in range(len(capture)):
        node = capture[i][0]
        alias = capture[i][1]
        if alias != "var_declare_withconstructmethod":
            continue
        value = index_to_code_token((node.start_point, node.end_point), java_loc)
        # print("Node type: ", node.type, "Node alias: ", alias, "Node value:", value)
        node0, node1, node2, node3 = capture[i + 2][0], capture[i + 3][0], \
                                     capture[i + 4][0], capture[i + 5][0]
        receiver = index_to_code_token((node0.start_point, node0.end_point), java_loc)  # receiver
        api_invoker = index_to_code_token((node1.start_point, node1.end_point), java_loc)  # invoker
        api_value = index_to_code_token((node2.start_point, node2.end_point), java_loc)  # method_name
        api_args = index_to_code_token((node3.start_point, node3.end_point), java_loc)  # args
        if api_invoker in dict_name2class.keys():
            api_class = dict_name2class[api_invoker].type
        elif api_invoker in ["System", "log"]:
            api_class = api_invoker
        else:
            api_class = api_invoker
        tempnode = api_node(api_invoker, api_class, api_value, api_args)
        if receiver in dict_name2class.keys() and tempnode.str in dict_name2api.keys():
            # dict_name2api[tempnode.str].receiver = receiver
            edge_receiver.append((dict_name2api[tempnode.str], dict_name2class[receiver]))

    list_node = []
    dict_node = {}

    for n in list_var:
        list_node.append(n.toString())
    for a in list_api:
        list_node.append(a.nodetoken())
    for a in list_api:
        s = a.nodetoken()
        ClassAndMethodName = s.split("(")[0]
        if ClassAndMethodName not in api_msg.keys():
            if ClassAndMethodName.split(".")[1] in sample_api_msg.keys():
                list_node.append(sample_api_msg[ClassAndMethodName.split(".")[1]]["description"])
                list_node.append(sample_api_msg[ClassAndMethodName.split(".")[1]]["return_description"])
                continue
            continue
        apimsg = api_msg[ClassAndMethodName]
        list_node.append(apimsg["des"])
        list_node.append(apimsg["return_description"])
    list_node.append("METHOD DESCRIPTION")
    if "return_description" not in list_node:
        list_node.append("return_description")
    for idx, n in enumerate(list_node):
        dict_node[n] = idx

    edge_des_begin, edge_des_end = [], []
    edge_return_begin, edge_return_end = [], []
    for a in list_api:
        s = a.nodetoken()
        ClassAndMethodName = s.split("(")[0]
        if ClassAndMethodName not in api_msg.keys():
            if ClassAndMethodName.split(".")[1] in sample_api_msg.keys():
                edge_des_begin.append(dict_node[s])
                edge_des_end.append(dict_node[sample_api_msg[ClassAndMethodName.split(".")[1]]["description"]])
                edge_return_begin.append(dict_node[s])
                edge_return_end.append(dict_node[sample_api_msg[ClassAndMethodName.split(".")[1]]["return_description"]])
                continue
            edge_des_begin.append(dict_node[s])
            edge_des_end.append(dict_node["METHOD DESCRIPTION"])
            edge_return_begin.append(dict_node[s])
            edge_return_end.append(dict_node["return_description"])
            continue
        apimsg = api_msg[ClassAndMethodName]
        edge_des_begin.append(dict_node[s])
        edge_des_end.append(dict_node[apimsg["des"]])
        edge_return_begin.append(dict_node[s])
        edge_return_end.append(dict_node[apimsg["return_description"]])

    edge_corresponding_begin, edge_corresponding_end = [], []
    edge_receiver_begin, edge_receiver_end = [], []
    for e in edge_receiver:
        edge_receiver_begin.append(dict_node[e[0].nodetoken()])
        edge_receiver_end.append(dict_node[e[1].toString()])
        # 有receiver的必然有return，找到return对应的节点，具体：edge_receiver中增加一个，用起始节点找到edge_return中对应的其实节点，然后找到其结束节点，加入edge_corresponding_begin
        idx = edge_return_end[edge_return_begin.index(dict_node[e[0].nodetoken()])]
        edge_corresponding_begin.append(idx)
        edge_corresponding_end.append(dict_node[e[1].toString()])
    edge_invoker_begin, edge_invoker_end = [], []
    for e in edge_invoker:
        edge_invoker_begin.append(dict_node[e[0].nodetoken()])
        edge_invoker_end.append(dict_node[e[1].toString()])

    var_num = len(list_var)
    api_num = len(list_api)
    msg_num = len(list_node) - var_num - api_num
    # print("var_num:", var_num, "api_num:", api_num, "msg_num:", msg_num)
    node_type = [0] * var_num + [1] * api_num + [2] * msg_num
    # for node in range(var_num):
    #     node_type.append(0)
    # for node in range(api_num):
    #     node_type.append(1)
    # for node in range(msg_num):
    #     node_type.append(2)
    # print("     edge_receiver: ", [edge_receiver_begin, edge_receiver_end])  # api指向变量
    # print("     edge_invoker: ", [edge_invoker_begin, edge_invoker_end])  # api指向变量
    # print("     edge_description: ", [edge_des_begin, edge_des_end])
    # print("     edge_return: ", [edge_return_begin, edge_return_end])
    # print("     edge_corresponding: ", [edge_corresponding_begin, edge_corresponding_end])
    # print("node_inp:", list_node)
    # print("node_type:", node_type)
    edge_index_begin, edge_index_end = edge_receiver_begin + edge_invoker_begin + edge_des_begin + edge_return_begin + \
                                       edge_corresponding_begin, edge_receiver_end + edge_invoker_end + edge_des_end + \
                                       edge_return_end + edge_corresponding_end
    edge_index = [edge_index_begin, edge_index_end]
    # print("edge_index: ", edge_index)
    edge_type = [0] * len(edge_receiver_begin) + [1] * len(edge_invoker_begin) + [2] * len(edge_des_begin) + \
                [3] * len(edge_return_begin) + [4] * len(edge_corresponding_begin)
    # print("edge_type: ", edge_type)
    return list_node, node_type, edge_index, edge_type


if __name__ == '__main__':
    JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
    PY_LANGUAGE = Language('build/my-languages.so', 'python')

    # 举一个java例子
    java_parser = Parser()
    java_parser.set_language(JAVA_LANGUAGE)

    with open("raw_data/train_data.json", 'r') as f:
        code_datas = json.load(f)

    java_code_snippet = '''
    private int findPLV(int M_PriceList_ID) {
        String input = "Hello World";
        String str = "World";
        str = "World";
        str = input.toUpperCase();
        input.reversed();
        int length = input.length();
        String output = input.toUpperCase();
        boolean contains = input.contains("o");
        int index = input.indexOf("W");
    '''
    with open("result/api_msg.pkl", 'rb') as f:
        api_msg = pickle.load(f)
    with open("result/sample_api_msg.pkl", 'rb') as f:
        sample_api_msg = pickle.load(f)  # 方法名不包含class时用这个
    # code_parse(java_code_snippet, api_msg, sample_api_msg)
    for code_data in code_datas:
        code = code_data["code"]
        code_data["graph"] = {}
        list_node, node_type, edge_index, edge_type = code_parse(code, api_msg, sample_api_msg)
        code_data["graph"]["node_inp"], code_data["graph"]["node_type"], code_data["graph"]["edge_index"], \
            code_data["graph"]["edge_type"] = code_parse(code, api_msg, sample_api_msg)
        # print()

    with open("code/train_graphdata.json",'w',encoding='utf-8') as f:
        json.dump(code_datas, f)
