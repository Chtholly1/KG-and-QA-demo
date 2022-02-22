#
import re
import sys
import collections

class TempMethod:
    def __init__(self, graph, template_path):
        self.characters = self.load_word_list('data/ori_data/characters.txt')
        self.groups = self.load_word_list('data/ori_data/groups.txt')
        self.race = self.load_word_list('data/ori_data/races.txt')
        race_str = '|'.join(self.race).replace('(', '（').replace(')', '）').replace('?', '')
        characters_str = '|'.join(self.characters).replace('(', '（').replace(')', '）').replace('?', '')
        group_str = '|'.join(self.groups).replace('(', '（').replace(')', '）').replace('?', '')
        self.r_race = re.compile(r"(%s)" % (race_str))
        self.r_char = re.compile(r'(%s)' % (characters_str))
        self.r_group = re.compile(r'(%s)' % (group_str))

        self.template_dict = {}
        self.graph = graph
        self.word_del = re.compile(r'(xx和xx|xx势力|xx种族|xx族|xx)')
        self.relation_map = {'race':'种族', 'group':'势力', 'title':'头衔', 'relation':'关系'}
        with open(template_path, encoding='utf8') as f:
            temp_label = ''
            for line in f:
                if not line.strip():
                    continue
                if line.strip().startswith('#'):
                    temp_label = line.strip()[1:]
                    self.template_dict[temp_label] = []
                else:
                    self.template_dict[temp_label].append(line.strip())
        return

    def load_word_list(self, path):
        temp_list = []
        with open(path, encoding='utf8') as f:
            for line in f:
                temp_list.append(line.strip())
        return temp_list

    def match(self, question):
        for key, val in self.template_dict.items():
            for template in val:
                real_temp = self.word_del.sub('', template)
                if question.find(real_temp) >= 0:
                    return key

    def relation_query(self, key, question_type, type=0):
        query_res = ''
        if type == 0:
            query_res = self.graph.run(
                "MATCH (n:ns0__Character)-[:ns0__%s]-(m:ns0__%s) "
                "WHERE n.ns0__name = $name "
                "RETURN m.ns0__name"%(self.relation_map[question_type], question_type.capitalize()),
                {"name": key}
            )
        if type == 1:
            query_res = self.graph.run(
                "MATCH (n:ns0__Character)-[:ns0__%s]-(m:ns0__%s) "
                "WHERE m.ns0__name = $name "
                "RETURN n.ns0__name"%(self.relation_map[question_type], question_type.capitalize()),
                {"name": key}
            )
        if type == 2:
            query_res = self.graph.run(
                "MATCH (n:ns0__Character) "
                "WHERE n.ns0__name = $name "
                "RETURN n.ns0__%s"%(self.relation_map[question_type]),
                {"name": key}
            )
        if type == 3:
            query_res = self.graph.run(
                "match(n:ns0__Character)-[relation]-(m:ns0__Character) "
                "where n.ns0__name = $name0 and m.ns0__name = $name1 "
                "return relation",
                {"name0": key[0], "name1":key[1]}
            )
        return query_res

    def generate_answer(self, question_type, question):
        query_res_list = []
        race_list = self.r_race.findall(question)
        character_list = self.r_char.findall(question)
        group_list = self.r_group.findall(question)
        print("关键词提取:")
        if race_list:
            print(race_list)
        if character_list:
            print(character_list)
        if group_list:
            print(group_list)
        if question_type == 'race':
            # 主要有三种类型的问题:1.xx是什么什么族的? 2.x族有哪些人？ 3.A和B是什么关系？

            if character_list:
                for item in character_list:
                    query_res = self.relation_query(item, question_type, type=0)
                    query_res_list.append(query_res)
            elif race_list:
                for item in race_list:
                    query_res = self.relation_query(item, question_type, type=1)
                    query_res_list.append(query_res)
        if question_type == 'group':
            if character_list:
                for item in character_list:
                    query_res = self.relation_query(item, question_type, type=0)
                    query_res_list.append(query_res)
            elif group_list:
                for item in group_list:
                    query_res = self.relation_query(item, question_type, type=1)
                    query_res_list.append(query_res)
        if question_type == 'title':
            if character_list:
                for item in character_list:
                    query_res = self.relation_query(item, question_type, type=2)
                    query_res_list.append(query_res)
        if question_type == 'relation':
            if len(character_list) == 2:
                query_res = self.relation_query(character_list, question_type, type=3)
                query_res_list.append(query_res)
        return query_res_list