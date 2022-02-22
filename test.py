import re
import sys

from py2neo import Graph
from template_method import TempMethod

#链接neo4j图谱
graph = Graph("http://localhost:7474/", auth=("neo4j", '123456'))

#加载问题模板
c = TempMethod(graph, 'data/question_template.txt')

#本次的问题
question = '阿克蒙德和萨格拉斯是什么关系?'
print("提问：\n%s\n"%(question))
#判断问题的大类
question_type = c.match(question)
print("类别:\n%s\n"%(question_type))
#根据问题及分类进行答案生成
query_res_list = c.generate_answer(question_type, question)
print()
#打印答案
print("答案：")
for query_res in query_res_list:
    for d in query_res.data():
        for key, val in d.items():
            print(key, val)