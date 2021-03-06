#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import json
import requests
import urllib
from decimal import Decimal
from decimal import getcontext
import numpy as np
# 测试Restful API执行gremlin
# 垃圾,点和边要单独查?
# 把ui里脚本的g换成hugegraph.traversal()
# gremlin_srcipt = """hugegraph.traversal().V().hasLabel("attack_pattern_0")"""
# gremlin_srcipt = """hugegraph.traversal().V().hasLabel("attack_pattern_0")"""
# gremlin_srcipt = """hugegraph.traversal().E().hasLabel("attack_event_0")"""
# gremlin_srcipt = """hugegraph.traversal().V().group().by(label)"""
# gremlin_srcipt = """hugegraph.traversal().V().hasLabel('attack_pattern_0').out().has('pattern_node_id',within(1))"""
# gremline_for_pattern_0 = """'subGraph = g.E().hasLabel('icmp_echo_ping').subgraph('subGraph').cap('subGraph').next()
#                         sg = subGraph.traversal()
#                         sg.E()'"""
# url = "http://127.0.0.1:8080/gremlin?gremlin="
# url = url + gremline_for_pattern_0
# response = requests.get(url)
# print response.status_code
# print response.text

# Restful API例子
# url中的特殊字符编码规范:  https://www.w3cschool.cn/htmltags/html-urlencode.html

# http://localhost:8080/graphs/hugegraph/traversers/kout?source=%222:0%22&max_depth=1
# 从"2:0"点出发,一步可达的点集合,可以继续增加max_depth的值,当返回空时,max_depth=MAX_DISTANCE-1
# 用不着最短路径了,自带的最短路径用不了

# http://localhost:8080/graphs/hugegraph/traversers/rings?source=%222:0%22&max_depth=2&direction=OUT
# 可以求从原点出发最大n步内的环路,hugegraph的Rings功能

# http://localhost:8080/graphs/hugegraph/traversers/rays?source=%222:0%22&max_depth=2&direction=OUT
# 根据起始顶点、方向、边的类型（可选）和最大深度等条件查找发散到边界顶点的路径,hugegraph的Rays功能

# gremlin例子
# g.V().as('a').out('icmp_echo_ping').as('b').select('a','b')
# 由icmp_echo_ping类型的边相连的两个点的信息

# g.V().as('a').out('icmp_echo_ping').as('b').select('a','b').by('ip')
# 由icmp_echo_ping类型的边相连的两个点的ip的信息,

# g.V().where(out('icmp_echo_ping')).values('ip')
# 有icmp_echo_ping类型出边的点的ip值

# g.V().where(out('attack_event_0').count().is(gte(6))).values('pattern_node_id')
# 取出边类型为attack_event_0,且该类型出边条数大于等于6的点(的pattern_node_id值)

# g.V().where(__.not(out('icmp_echo_ping'))).where(__.in('icmp_echo_reply')).values('ip')
# 取出没有类型为icmp_echo_ping的出边,但是有icmp_echo_reply的入边的点(的ip)

# g.V().where(out('rpc_call').where(out('rpc_reply'))).values('ip')
# 取出有类型为rpc_call的出边,且接着这个出边,有类型为rpc_reply的第二跳出边的点(的ip)

# g.V('2:0').outE('attack_event_0').values('event_label')
# 取出从可疑点触发的攻击事件边的事件类型(会有重复),复杂一点,记下数量?
# g.E().hasLabel('attack_event_0').values('event_label')
# 攻击模式0下所有的边事件类型

# g.V('1:202.77.162.213').out().out().path()
# 从点202.77.162.213出发,连续两个出边的路线

# g.V().and(outE('icmp_echo_ping'), values('ip').is('202.77.162.213')).values('ts')
# 有icmp_echo_ping类型出边,且ip为202.77.162.213的点的ts值

# g.V().as('a').out('icmp_echo_ping').as('b').select('a','b')
# 取a->b的,边为icmp_echo_ping的所有a,b对

# g.V().group().by(bothE().count())
# 此方法可以把图中的所有点按照度进行分组,可用于取前k个节点(度由高到低)

# g.V().match(__.as('a').in('icmp_echo_ping').has('ip', '202.77.162.213').as('b'))
# 此方法是gremlin的模式匹配,满足则生成一个map<String, Object>,不满足则过滤掉
# 模式1: "a"对应当前节点,有icmp_echo_ping的入边
# 模式2: "b"对应节点"202.77.162.213"
# 效果: 得到从b出发的,且距离为1的所有节点对

# g.V().match(
#     __.as('a').out('icmp_echo_ping').as('b'),
#     __.as('b').in('rpc_call').as('c')).
#     where('a', neq('c')).
#     select('a','c').by('ip')
# 从某个节点a出发的icmp_echo_ping,到节点b,节点b有来自节点c的rpc_call的入边,where保证a和c

# g.V('1:202.77.162.213').match(
#     __.as('a').out('icmp_echo_ping').as('b'),
#     __.as('b').in('icmp_echo_reply').as('c')).
#     where('a', eq('c')).
#     select('a','b')
# 在本场景中也可以用,指定出发点的id,a等于c表示环

# g.V('2:0').bothE().otherV().simplePath().path()
# g.V('2:0').both().both().cyclicPath().path()

# subGraph = g.E().or(__.hasLabel('icmp_echo_ping'),
#                     __.hasLabel('icmp_echo_reply'))
#                     .subgraph('subGraph').cap('subGraph').next()
# sg = subGraph.traversal()
# sg.E()
# 多类型的边,生成的子图.即子图中既包含icmp_echo_ping类型的边,也包含icmp_echo_reply类型的边

# g.V("2:0").repeat(out()).times(2).path()
# 某点出发,out两次

# 需要的gremline功能
# 在图sg中,取出其中所有满足某个边属性条件的,边

# 这里不好用Restful API执行,可以使用hugegraph-tool的gremlin-execute指令执行
# gremlin-execute: 同步执行
# --script 执行脚本看来不太行
# --file 执行文件中的脚本,脚本语句的前后依赖不能太多,不然运行非常慢
# gremlin-schedule: 异步执行

# gremlin执行流程:
# 1. 根据需求设置gremlin语句
# 2. 将gremlin写入脚本文件
# 3. cmd拼接脚本文件
# 4. hugegraph-tool执行脚本文件
# 5. 分析返回结果

# 子图匹配步骤:
# 1. 从攻击模式图中提取特征信息(攻击模式图按照0,1,2,3,...编号)
#    gremlin脚本文件或者Restful API获取标签为attack_event_n的的边集合
#    特征信息包括:0点出边事件类型,0点到其他点的最远距离,环信息(如何表示?)
# 2. 按边事件类型提取子图,得到边集合,去除不关心的边(数据过滤1))
#    gremlin提供了subgraph方法
#    各种事件类型缺一不可,这里搜的边事件类型是和0号节点直接相连的事件类型(相对重要)
#    比如0->1->2,1->2的事件可以在最后一步模式匹配的时候再关心(皮之不存,毛将焉附)
# 3. 分析边集合,按照TIME WINDOW进行初步筛选,去除过旧的边(数据过滤2)
#    本地数据分析,JSON格式的边数据
# 4. 从边集合中提取点集合,得到过滤后的子图(该子图怎么存储,计算?)
#    本地数据分析,JSON格式的边数据中提取点数据
#    难点:过滤后的子图如何存放?保留在本地的话,不方便做图计算.简单整理之后,存回图谱?按照一种新的模式存储.
#    过滤后的子图肯定不能再存,需要在gremlin脚本中以图变量形式存在
#    所以,上面3步必须一次到位
# 5. 在上一步的子图中,计算各节点的度,并按照从达到小的顺序对节点进行排序(度越大,可疑程度越高)
#    参考gremlin中与节点度相关的图计算接口
# 6. 将可疑节点序列对应攻击模式中的0号节点,限定范围匹配(从可疑节点开始,1跳,2跳)
hugegraph_bin_path = "/home/lw/hugegraph-tools-1.3.0/bin/"
project_path = "/home/lw/myKGA/"
gremline_file_name = "gremlin_scripts"
tool_command = "gremlin-execute"

nodes_involved = []
global attack_counter


def execute_command(cmd):
    sub = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    str1 = sub.stdout.read()
    sub.communicate()
    str1 = str1.decode()
    # print str1
    return str1

def extract_max_distance(source_node_id):
    print "获取攻击节点可达的最远距离..."
    max_distance = 1
    while(True):
        url = "http://localhost:8080/graphs/hugegraph/traversers/kout"
        pms = {
            "max_depth": max_distance
        }
        pms["source"] = "\"%s\""%source_node_id
        url_encoded = urllib.urlencode(pms)
        # cmd = "curl " + url
        # print cmd
        # print url_encoded
        r = requests.get(url, params = pms)
        # print r.url
        # print r.status_code
        # print type(r.content)
        tmp_dict = json.loads(r.content)
        end_while = False
        for key in tmp_dict:
            if key == "vertices" and tmp_dict[key] == []:
                max_distance -= 1
                end_while = True
        if end_while:
            break
        max_distance += 1
    return max_distance

def extract_key_events(pattern_num):
    print "获取关键事件..."
    tmp_events = set()
    pattern = "attack_event_" + str(pattern_num)
    with open("gremlin_scripts", "w") as f:
        line = """g.V().outE('{attack_event_num}').values('event_label')\n""".format(attack_event_num = pattern)
        f.write(line)
        f.close()
    cmd = hugegraph_bin_path + "hugegraph " + tool_command + " --file " + project_path + gremline_file_name
    result = execute_command(cmd)
    # print result
    lines = result.split('\n')
    # print lines
    for item in lines:
        if item != "" and item != "Run gremlin script":# Run gremlin script是hugegraph的输出
            tmp_events.add(item)
    return tmp_events

def extract_attack_pattern_edgelabel_id(PATTERN_NUM):
    url = "http://localhost:8080/graphs/hugegraph/schema/edgelabels/"
    edgelabel = "attack_event_" + str(PATTERN_NUM)
    url = url + edgelabel
    r = requests.get(url)
    tmp_dict = json.loads(r.content)
    return tmp_dict["id"]

def extract_edgelabelid_by_edgelabel(edgelabel):
    url = "http://localhost:8080/graphs/hugegraph/schema/edgelabels/"
    url = url + edgelabel
    r = requests.get(url)
    tmp_dict = json.loads(r.content)
    return tmp_dict["id"]

def extract_edge_by_edgeid(edge_id):
    url = "http://localhost:8080/graphs/hugegraph/graph/edges/"
    url = url + edge_id
    r = requests.get(url)
    tmp_dict = json.loads(r.content)
    return tmp_dict

def extract_attack_event_by_edgeid(edge_id):
    url = "http://localhost:8080/graphs/hugegraph/graph/edges/"
    url = url + edge_id
    r = requests.get(url)
    tmp_dict = json.loads(r.content)
    return tmp_dict["properties"]["event_label"]

def extract_event_chain_paths(source_node_id, MAX_DISTANCE, PATTERN_NUM):
    print "提取攻击事件链(无环)..."
    tmp_paths = []
    # 攻击事件链结构
    # 可以先用Rays方法求出其到边界节点的所有可能路径,然后把路径转为事件链.因为是特征子图,计算量不会太大.
    # event(n1),event(n2),...,event(n3)
    url = "http://localhost:8080/graphs/hugegraph/traversers/rays"
    pms = {
        "max_depth": MAX_DISTANCE,
        "direction": "OUT"
    }
    pms["source"] = "\"%s\""%source_node_id
    # url_encoded = urllib.urlencode(pms)
    r = requests.get(url, params = pms)
    tmp_dict = json.loads(r.content)
    print tmp_dict
    print tmp_dict["rays"]
    # 根据路径确定边id,边id由两点id以及边标签id决定,所以选查出边标签id,最后拼出边id
    edgelabel_id = extract_attack_pattern_edgelabel_id(PATTERN_NUM)
    for item in tmp_dict["rays"]:
        i = 0
        # print item["objects"][2]
        attack_event_sequence_arr = []
        attack_event_sequence = ""
        while i + 1 < len(item["objects"]):
            tmp_src = item["objects"][i]
            tmp_dst = item["objects"][i+1]
            # tmp_sec, tmp_dst是一小段路径
            edge_id = "S" + tmp_src + ">" + str(edgelabel_id) + ">>S" + tmp_dst
            print edge_id
            attack_event = extract_attack_event_by_edgeid(edge_id)
            attack_event_sequence_arr.append(attack_event)
            i += 1
        for e in attack_event_sequence_arr:
            attack_event_sequence = attack_event_sequence + e + ">"
        if attack_event_sequence not in tmp_paths:
            tmp_paths.append(attack_event_sequence)
    return tmp_paths

def extract_event_chain_cyclicpaths(source_node_id, PATTERN_NUM):
    print "提取攻击事件链(环路)..."
    # 先确定环路查找的最大深度
    url = "http://localhost:8080/gremlin"
    pms = {}
    tmp_paths = []
    edgelabel = "attack_event_" + str(PATTERN_NUM)
    pms["gremlin"] = "hugegraph.traversal().E().hasLabel(\"%s\").count()"%edgelabel
    # url_encoded = urllib.urlencode(pms)
    r = requests.get(url, params = pms)
    tmp_dict = json.loads(r.content)
    depth = tmp_dict["result"]["data"][0] # 保守起见,设为边个数
    pms.clear()
    # 使用rings方法查找环路
    url = "http://localhost:8080/graphs/hugegraph/traversers/rings"
    pms["source"] = "\"%s\""%source_node_id
    pms["max_depth"] = depth
    pms["direction"] = "OUT"
    # url_encoded = urllib.urlencode(pms)
    r = requests.get(url, params = pms)
    tmp_dict = json.loads(r.content)
    edgelabel_id = extract_attack_pattern_edgelabel_id(PATTERN_NUM)
    for item in tmp_dict["rings"]:# 照抄上面的
        i = 0
        # print item["objects"][2]
        attack_event_sequence_arr = []
        attack_event_sequence = ""
        while i + 1 < len(item["objects"]):
            tmp_src = item["objects"][i]
            tmp_dst = item["objects"][i+1]
            # tmp_sec, tmp_dst是一小段路径
            edge_id = "S" + tmp_src + ">" + str(edgelabel_id) + ">>S" + tmp_dst
            print edge_id
            attack_event = extract_attack_event_by_edgeid(edge_id)
            attack_event_sequence_arr.append(attack_event)
            i += 1
        for e in attack_event_sequence_arr:
            attack_event_sequence = attack_event_sequence + e + ">"
        if attack_event_sequence not in tmp_paths:
            tmp_paths.append(attack_event_sequence)
    return tmp_paths

def extract_suspicious_nodes_from_datagraph(KEY_EVENTS, K):
    print "查找可疑点序列..."
    request_body = {
        "bindings": {},
        "language": "gremlin-groovy",
        "aliases": {}
    }
    orSequence = ""
    for i in KEY_EVENTS:
        orSequence = orSequence + "__.hasLabel(\"%s\")"%i + ","
    orSequence = orSequence[:-1] # 去除结尾的逗号
    # print orSequence
    line1 = "subGraph = hugegraph.traversal().E().or(" + orSequence + ").subgraph(\"subGraph\").cap(\"subGraph\").next()\n"
    line2 = "sg = subGraph.traversal()\n"
    line3 = "sg.V().group().by(bothE().count())\n"
    request_body["gremlin"] = line1 + line2 + line3
    # print request_body
    url = "http://localhost:8080/gremlin"
    # pms_encoded = urllib.urlencode(request_body)
    r = requests.post(url, json=request_body)
    # print r.content
    tmp_dict = json.loads(r.content)
    for i in tmp_dict["result"]["data"]:
        key_list = i.keys()
        # print key_list
    degree = []
    candidates = []
    for i in key_list:
        degree.append(int(i))
    degree.sort(reverse=True)
    # print degree
    j = 0
    # 格式奇怪,要自己解析
    if K > len(tmp_dict["result"]["data"][0]):# K不能过大
        K = len(tmp_dict["result"]["data"][0])
    while j < K:
        for item in tmp_dict["result"]["data"][0][str(degree[j])]: # 度相同的节点们
            candidates.append(item["id"])
        j += 1
    return candidates

def execute_Gremlin(script):
    request_body = {
        "bindings": {},
        "language": "gremlin-groovy",
        "aliases": {}
    }
    request_body["gremlin"] = script
    url = "http://localhost:8080/gremlin"
    r = requests.post(url, json=request_body)
    tmp_dict = json.loads(r.content)
    return tmp_dict

def search_attack_event(SYMBOL_LIST, EVENT_SEQUENCE, V, IsCylic):# 一次针对某一个点,匹配一个攻击模式
    # 能不能在这里把边上的时间戳属性也取出来?或者说在得到a1,a2这些之后顺势拿出边上的时间戳
    # Q: 已经点序列id和边标签,求路径上的边属性?
    print "基于可疑节点进行攻击模式匹配..."
    print V
    # search_result = True
    v = V
    start_subsentence = "hugegraph.traversal().V('" + v + "').match(\n"
    match_subsentence = ""
    end_subsentence = ""
    where_subsentence = "" #环路匹配需要
    single_subsentences = []
    i = 0 # i用于取出符号
    for item in EVENT_SEQUENCE:
        if item != "" and i < len(SYMBOL_LIST)-1:
            if i == len(SYMBOL_LIST)-2 and IsCylic:# 环路匹配的最后一节是in边   不对,都是out边
                single_subsentence = "__.as('" + SYMBOL_LIST[i] + "').out('" + item + "').as('" + SYMBOL_LIST[i+1] + "'),"
            else:
                single_subsentence = "__.as('" + SYMBOL_LIST[i] + "').out('" + item + "').as('" + SYMBOL_LIST[i+1] + "'),"
            single_subsentences.append(single_subsentence)
            i += 1
        else:
            break
    for i in single_subsentences:
        match_subsentence += i
    match_subsentence = match_subsentence[:-1]
    end_subsentence = ").select("
    for symbol in SYMBOL_LIST:
        end_subsentence = end_subsentence + "'" + symbol + "',"
    end_subsentence = end_subsentence[:-1]
    end_subsentence += ").by('ip')"
    if not IsCylic:
        query_sentence = start_subsentence + match_subsentence + end_subsentence
    else:
        where_subsentence = ").where('" + SYMBOL_LIST[0] + "', eq('" + SYMBOL_LIST[len(SYMBOL_LIST)-1] + "')"
        query_sentence = start_subsentence + match_subsentence + where_subsentence + end_subsentence
    tmp_dict = execute_Gremlin(query_sentence)
    print query_sentence
    if len(tmp_dict["result"]["data"]):
        # 这里应该添加取时间戳的操作,最后把时间戳和tmp_dict["result"]["data"]的内容一并返回,后续的处理稍作修改
        print "成功!"
    else:
        print "失败!"
    return tmp_dict["result"]["data"]
        

def extract_attack_event_by_event_chain(EVENT_CHAIN_PATHS, EVENT_CHAIN_CYCLICPATHS, SUSPICIOUS_NODES, PATTERN_NUM):
    print "开始攻击事件匹配..."
    Malicious_nodes = [] # 符合该攻击模式的所有的攻击节点
    for V in SUSPICIOUS_NODES: # 从可疑节点出发,理论上可能会匹配到多个. (一个可疑节点)->(若干个受害节点),可以写下来,写到文件中去.保存在一个全部变量中也可以
        result_dict = {}
        start_time = Decimal()
        end_time = Decimal()
        IsMalicious = True
        victim_nodes = set()
        ports_involved = set()
        print "匹配无环攻击序列..."
        for event in EVENT_CHAIN_PATHS:
            event_sequence = event.split('>')
            # event_sequence中实际事件个数为len(event_sequence)-1,去掉最后的空串
            symbol_list = [] # 符号表中的符号个数应比事件个数多1(点的别名)
            i = 1
            while i <= len(event_sequence):
                symbol_list.append("a" + str((i)))
                i += 1
            res = search_attack_event(symbol_list, event_sequence, V, False)
            if not len(res):
                IsMalicious = False
            else:
                print res
                # 可以按照边id来查,端点的id已知,需要知道边标签的序号,自己拼出边id 使用extract_edgelabelid_by_edgelabel方法
                index = 1
                scan_index = 0
                while scan_index < len(res):
                    index = 1
                    while index < len(symbol_list):
                        edgelabelid = extract_edgelabelid_by_edgelabel(event_sequence[index - 1])
                        edgeid = "S1:" + res[scan_index][symbol_list[index - 1]] + ">" + str(edgelabelid) + ">>S1:" + res[scan_index][symbol_list[index]]
                        edge_info = extract_edge_by_edgeid(edgeid)["properties"]
                        ports_involved.add(edge_info["src_p"])
                        ports_involved.add(edge_info["dst_p"])
                        tmp_ts = Decimal(edge_info["ts"])
                        if start_time == 0:
                            start_time = tmp_ts
                        if end_time == 0:
                            end_time = tmp_ts
                        # 更新时间戳
                        if start_time.compare(tmp_ts) > 0:
                            start_time = tmp_ts
                        if end_time.compare(tmp_ts) < 0:
                            end_time = tmp_ts
                        index += 1
                    scan_index += 1
                scan_index = 0
                while scan_index < len(res):
                    for sym in symbol_list:# 有问题!第一个ping扫描应该涉及很多节点才对
                        # print res[0][sym] # 涉及的节点
                        victim_nodes.add(res[scan_index][sym])
                    scan_index += 1
            print symbol_list
        print "匹配环路攻击序列..."
        for event in EVENT_CHAIN_CYCLICPATHS:
            event_sequence = event.split('>')
            symbol_list = []
            i = 1
            while i <= len(event_sequence):
                symbol_list.append("a" + str((i)))
                i += 1
            res = search_attack_event(symbol_list, event_sequence, V, True)
            if not len(res):
                IsMalicious = False
            else:
                print res
                index = 1
                scan_index = 0
                while scan_index < len(res):
                    index = 1
                    while index < len(symbol_list):
                        edgelabelid = extract_edgelabelid_by_edgelabel(event_sequence[index - 1])
                        edgeid = "S1:" + res[scan_index][symbol_list[index - 1]] + ">" + str(edgelabelid) + ">>S1:" + res[scan_index][symbol_list[index]]
                        edge_info = extract_edge_by_edgeid(edgeid)["properties"]
                        ports_involved.add(edge_info["src_p"])
                        ports_involved.add(edge_info["dst_p"])
                        tmp_ts = Decimal(edge_info["ts"])
                        # 初始化时间戳
                        if start_time == 0:
                            start_time = tmp_ts
                        if end_time == 0:
                            end_time = tmp_ts
                        # 更新时间戳
                        if start_time.compare(tmp_ts) > 0:
                            start_time = tmp_ts
                        if end_time.compare(tmp_ts) < 0:
                            end_time = tmp_ts
                        index += 1
                    scan_index += 1
                scan_index = 0
                while scan_index < len(res):
                    for sym in symbol_list:# 有问题!第一个ping扫描应该涉及很多节点才对
                        # print res[0][sym] # 涉及的节点
                        victim_nodes.add(res[scan_index][sym])
                    scan_index += 1
            print symbol_list
        if IsMalicious:
            Malicious_nodes.append(V)
            # 这种情况下,victim_nodes的内容才有效
            # 攻击模式应当对应一个攻击模式的标签,才合理.仅仅标上序号是不行的.
            # 可以先按Pattern-序号的形式记录,后面再补上序号和标签的对应关系即可
            print "确定恶意节点:"
            print V
            print "对应的受影响节点:"
            print victim_nodes
            print "受影响端口:"
            print ports_involved
            print "开始时间:"
            print start_time
            print "结束时间"
            print end_time
            print "+++++++++++++++++++++++++++++++++++++++++++++++++"
            global attack_counter
            result_dict["num"] = attack_counter # 用全局变量标个号
            attack_counter += 1
            result_dict["pattern"] = "attack-pattern-" + str(PATTERN_NUM) # 希望可以处理成label
            result_dict[V] = victim_nodes
            result_dict["ports"] = ports_involved
            result_dict["start_time"] = start_time
            result_dict["end_time"] = end_time
            nodes_involved.append(result_dict)
            print nodes_involved
            print "+++++++++++++++++++++++++++++++++++++++++++++++++"
    return Malicious_nodes

# 计算Jaccord集合相似度,p和q是集合类型
def jaccard(p, q):
    return float(len(set.intersection(p, q)))/float(len(set.union(p, q)))

if __name__ == '__main__':
    # 工作分四部分:
    # 第一部分,图谱构建(基本完成,不在此文档中)
    # 第二部分,属性图挖掘进行攻击发现(基本完成)
    # 第三部分,属性图相似度计算进行攻击关联(有思路可以参考,吴东的超级告警方法,但也有不同的地方)
    # 第四部分,基于恶意节点影响度进行态势理解(考虑pagerank算法结合场景,考虑两个因素,第一,单步攻击的影响关系,第二,涉及攻击链的影响关系,
    # 还没做,但这个应该不太难,此算法有现成代码,最后只是给出态势值,说服力可能不够)
    # 思路先理清,文章不能着急写
    # 做的是特征匹配,而不是子图同构匹配,否则漏洞百出
    # 也可以理解为做的是模糊匹配,而不是精确匹配(不需要)
    attack_counter = 0
    PATTERN_NUM = 0
    MAX_DISTANCE = 1 # ok
    TIME_WINDOW = 600 # 自己设
    KEY_EVENTS = set() # 取和0点相连的attack_event_n的边的event_label属性, ok
    EVENT_CHAIN_PATHS = []
    EVENT_CHAIN_CYCLICPATHS = []
    SUSPICIOUS_NODES = []
    PATTERNS = 5
    K = 2 # 自己设
    # 从特征图中提取以下要素
    # 从可疑节点出发的匹配规则
    # K值(前K个可疑点),ok
    # 最大距离(限制匹配范围),ok
    # 环的处理(模式匹配/连续out匹配),环仍然要化为匹配规则
    while PATTERN_NUM < PATTERNS:
        KEY_EVENTS.clear() # 集合        # 阶段2的rpc_call和rpc_reply环匹配有问题,明明有这个环存在,但是匹配不到要清空
        print "开始抽取攻击模式图0的特征信息:"
        # source_node_id = "4:0" # 攻击特征图中的攻击节点 这个id太坑,不可控
        source_node_id = str(PATTERN_NUM+4) + ":0" # 实际就是相隔2
        MAX_DISTANCE = extract_max_distance(source_node_id)
        print "MAX_DISTANCE = " + str(MAX_DISTANCE)
        print "设置时间窗大小..."
        print "TIME_WINDOW = " + str(TIME_WINDOW)
        print "设置K值..."
        print "K = " + str(K)
        # 匹配规则的格式:
        # 可疑点出发,攻击事件链(思路,从攻击模式图中查找所有的事件链组合,重复也没事,链上每一步可能有不止一个事件(兼备,只要模式匹配能达到这个要求就行))
        # 提取关键事件(用于求边生成子图)
        KEY_EVENTS = extract_key_events(PATTERN_NUM)
        print KEY_EVENTS
        # 提取攻击事件链
        EVENT_CHAIN_PATHS = extract_event_chain_paths(source_node_id, MAX_DISTANCE, PATTERN_NUM)
        print "攻击事件链(无环):"
        print "EVENT_CHAIN_PATHS = "
        print EVENT_CHAIN_PATHS
        EVENT_CHAIN_CYCLICPATHS = extract_event_chain_cyclicpaths(source_node_id, PATTERN_NUM)
        print "攻击事件链(有环):"
        print "EVENT_CHAIN_CYCLICPATHS = "
        print EVENT_CHAIN_CYCLICPATHS
        SUSPICIOUS_NODES = extract_suspicious_nodes_from_datagraph(KEY_EVENTS, K)
        print "可疑节点id:"
        print "SUSPICIOUS_NODES = "
        print SUSPICIOUS_NODES
        MALICIOUS_NODES = extract_attack_event_by_event_chain(EVENT_CHAIN_PATHS, EVENT_CHAIN_CYCLICPATHS, SUSPICIOUS_NODES, PATTERN_NUM)
        print "恶意节点id:"
        print "MALICIOUS_NODES = "
        print MALICIOUS_NODES
        # 发现的攻击模式需要保存下来
        # 为下一步攻击链发现作准备
        # 匹配成功的结果:单步攻击的表示形式(恶意节点,受影响节点,事件集合,开始时间,结束时间,事件标签)
        # 事件标签还没有贴上. 可能会用到. 考虑"多因素关联"和"本体推理机"方法
        PATTERN_NUM += 1
    print nodes_involved
    # nodes_involved包含了所有单步攻击的信息
    # 分析任务
    # 1: 确定单步攻击的start_time和end_time属性
    # 2: 将攻击模式映射至标签,希望可以做类型关联度分析
    # 3: 单步攻击表示为(攻击节点,受影响节点,开始时间,结束时间,涉及端口,攻击标签)的六元组 (1,1,1,1,1,0)
    # 4: 从ip,端口,时间,类型等四个角度计算关联度,同时设置关联度阈值
    # 5: 类型需要一个从攻击序号到标签的映射关系
    # 6: 待定,参考论文
    # 关于攻击标签的考虑,这是一种比较明显的专家知识.最多作辅助使用,比如属于杀伤链的某个大阶段.
    # 弱化攻击标签的影响,好让我的"发现新攻击序列"的说法站得住脚
    a = set()
    b = set()
    a.add("111")
    b.add("111")
    b.add("222")
    a.add("333")
    a.add("444")
    print "测试杰卡徳相似度..." # 应用到ip,端口上
    print jaccard(a, b)
    # 要算出任意两个单步之间的关联度,设置一个n*n的关联矩阵
    for e in nodes_involved:
        print e
        # 挨个处理
        for key in e:
            if key == "pattern":
                print "convert attack patterns to labels"
            elif key == "num": # 是不是按照顺序来的?
                print e[key]
            else:
                print key
                print type(e[key]) # e[key]是受影响节点集合
                # 再想办法取出时间戳,现在回头取是不是有点难弄?能不能一开始就弄上? 可以
    print len(nodes_involved)
    # 先按时间顺序罗列一下?
    incidence_matrix = np.zeros((len(nodes_involved), len(nodes_involved)))
    print "初始化关联性度量矩阵..."
    print incidence_matrix
    # Corr( Ha, Hb) = ∑ w i × C i
    # C1: IP的集合相似度(受影响节点) 是否需要对子集之类的情况作一些修正?
    # C2: Port的集合相似度(参与通信的端口)
    # C3: 类型 APT的杀伤链模型
    for a in nodes_involved:
        for b in nodes_involved:
            if a["num"] == b["num"]:
                continue
            key1 = ""
            key2 = ""
            for key in a: # 恶意节点ip不太确定, key1和key2都代表恶意节点ip
                if key != "pattern" and key != "start_time" and key != "num" and key != "end_time" and key != "ports":
                    key1 = key
            for key in b:
                if key != "pattern" and key != "start_time" and key != "num" and key != "end_time" and key != "ports":
                    key2 = key
            c1 = jaccard(a[key1], b[key2]) # a[key1]和b[key2]分别代表受影响节点
            # 可以分情况考虑,如果key1和key2相同,说明这两个攻击关联性强(为同一个恶意节点发动的攻击)
            # 反之,如果key1和key2不同,那么就从受影响节点的集合来考虑. Jaccard常数为0,完全无关,非0,有关.
            # 还可以考虑一些其他的情况,比如key1或者key2在对方的受影响节点中,key2在key1的受影响节点中
            # 说明,key2可能是被key1入侵了,成为了新的肉机(当然,还需要时间上满足先后关系).这种情况,可以增加关联性值.
            c2 = jaccard(a["ports"], b["ports"])
            getcontext().prec = 4
            c = Decimal(0.5 * c1 + 0.5 * c2) # 暂时这么写
            incidence_matrix[a["num"], b["num"]] = incidence_matrix[b["num"], a["num"]] = c # 关联矩阵应该是个对称矩阵
    print "计算过后的关联性度量矩阵..."
    print incidence_matrix
    # 计算结束之后,需要设置规定"两者之间是否有相关关系"的阈值
    # 此后可以仿照吴东的方法,构建单步攻击时间关系图并从中挖掘攻击链
    # ...