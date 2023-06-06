import os
import json

import pandas as pd
from neo4j_driver import Neo4jConnection, Node

df = pd.read_csv('data/medical_data.csv')

#实体创建
def df2list(key):
    data = []
    for each in df[key]:
        if not isinstance(each, str):  # 如果 each 不是字符串类型
            each = str(each)           # 转换为字符串类型
        data.extend(each.split(','))
    data = set(data)
    return data

def durg():#药实体
    drugs = []
    for each in df['推荐药物']:
        try:
            drugs.extend(each.split(','))
        except:
            pass
    for each in df['常用药物']:
        try:
            drugs.extend(each.split(','))
        except:
            pass
    drugs = set(drugs)
    return drugs

def food():#食物实体
    foods = []
    for each in df['可以吃']:
        try:
            foods.extend(each.split(','))
        except:
            pass
    for each in df['不可以吃']:
        try:
            foods.extend(each.split(','))
        except:
            pass
    for each in df['推荐吃']:
        try:
            foods.extend(each.split(','))
        except:
            pass
    foods = set(foods)
    return foods

def produce():#药物厂商
    producers = []

    for each in df['具体药物']:
        try:
            for each_drug in each.split(','):
                producer = each_drug.split('(')[0]
                producers.append(producer)
        except:
            pass
    producers = set(producers)
    return producers

def disease_info():#疾病字典信息
    disease_infos = [] # 疾病信息
    for idx, row in df.iterrows():
        disease_infos.append(dict(row))
    return disease_infos

#关系创建

def deduplicate(rels_old):
    '''关系去重函数'''
    rels_new = []
    for each in rels_old:
        if each not in rels_new:
            rels_new.append(each)
    return rels_new

def rels_checks():#疾病-检查
    rels_check = []
    for idx, row in df.iterrows():
        checks = row['检查']
        if not isinstance(checks, str):  # 如果 checks 不是字符串类型
            checks = str(checks)         # 转换为字符串类型
        for each in checks.split(','):
            rels_check.append([row['疾病名称'], each])
    rels_check = deduplicate(rels_check)
    return rels_check

def rels_symptoms():#疾病-症状
    rels_symptom = []
    for idx, row in df.iterrows():
        symptoms = row['症状']
        if not isinstance(symptoms, str):  # 如果 symptoms 不是字符串类型
            symptoms = str(symptoms)       # 转换为字符串类型
        for each in symptoms.split(','):
            rels_symptom.append([row['疾病名称'], each])
    rels_symptom = deduplicate(rels_symptom)
    return rels_symptom

def rels_acompanys():#疾病-疾病（并发症）
    rels_acompany = []
    for idx, row in df.iterrows():
        acompany = row['并发症']
        if not isinstance(acompany, str):  # 如果 acompany 不是字符串类型
            acompany = str(acompany)       # 转换为字符串类型
        for each in acompany.split(','):
            rels_acompany.append([row['疾病名称'], each])
    rels_acompany = deduplicate(rels_acompany)
    return rels_acompany

def rels_recommanddrugs():#疾病-推荐药物
    rels_recommanddrug = []
    for idx, row in df.iterrows():
        try:
            for each in row['推荐药物'].split(','):
                rels_recommanddrug.append([row['疾病名称'], each])
        except:
            pass
    rels_recommanddrug = deduplicate(rels_recommanddrug)
    return rels_recommanddrug

def rels_commonddrugs():#疾病-常用药物
    rels_commonddrug = []
    for idx, row in df.iterrows():
        try:
            for each in row['常用药物'].split(','):
                rels_commonddrug.append([row['疾病名称'], each])
        except:
            pass
    rels_commonddrug = deduplicate(rels_commonddrug)
    return rels_commonddrug

def rels_noteats():#疾病-不可以吃
    rels_noteat = []
    for idx, row in df.iterrows():
        try:
            for each in row['不可以吃'].split(','):
                rels_noteat.append([row['疾病名称'], each])
        except:
            pass
    rels_noteat = deduplicate(rels_noteat)
    return rels_noteat

def rels_doeats():#疾病-可以吃
    rels_doeat = []
    for idx, row in df.iterrows():
        try:
            for each in row['可以吃'].split(','):
                rels_doeat.append([row['疾病名称'], each])
        except:
            pass
    rels_doeat = deduplicate(rels_doeat)
    return rels_doeat

def rels_recommandeats():#疾病-推荐吃
    rels_recommandeat = []
    for idx, row in df.iterrows():
        try:
            for each in row['推荐吃'].split(','):
                rels_recommandeat.append([row['疾病名称'], each])
        except:
            pass
    rels_recommandeat = deduplicate(rels_recommandeat)
    return rels_recommandeat

def rels_drug_producers():
    rels_drug_producer = []
    for each in df['具体药物']:
        try:
            for each_drug in each.split(','):
                producer = each_drug.split('(')[0]
                drug = each_drug.split('(')[1][:-1]
                rels_drug_producer.append([producer, drug])
        except:
            pass
    rels_drug_producer = deduplicate(rels_drug_producer)
    return rels_drug_producer

def department(a,b):
    rels_category = []  # 关系：疾病-科室
    rels_department = []  # 关系：小科室-大科室
    for idx, row in df.iterrows():
        department = row['科室']
        if not isinstance(department, str):  # 如果 department 不是字符串类型
            department = str(department)     # 转换为字符串类型
        if len(department.split(',')) == 1:
            rels_category.append([row['疾病名称'], department])
        else:
            big = department.split(',')[0]  # 大科室
            small = department.split(',')[1]  # 小科室
            rels_category.append([row['疾病名称'], small])
            rels_department.append([small, big])
    rels_category = deduplicate(rels_category)
    rels_department = deduplicate(rels_department)

    a=rels_category
    b=rels_department


def build():

    symptoms = df2list('症状')
    departments= df2list('科室')
    checks = df2list('检查')
    drugs=durg()
    foods=food()
    producers=produce()
    disease_infos=disease_info()

    rels_check=rels_checks()
    rels_symptom=rels_symptoms()
    rels_acompany=rels_acompanys()
    rels_recommanddrug=rels_recommanddrugs()
    rels_commonddrug=rels_commonddrugs()
    rels_noteat=rels_noteats()
    rels_doeat=rels_doeats()
    rels_recommandeat=rels_recommandeats()
    rels_drug_producer=rels_drug_producers()

    rels_category = []  # 关系：疾病-科室
    rels_department = []  # 关系：小科室-大科室
    department(rels_category,rels_department)




    g= Neo4jConnection('neo4j://localhost:7687/', 'neo4j', '12345678')
    for disease_dict in disease_infos:#创建疾病实体
        try:
            node = Node("Disease",
                        name=disease_dict['疾病名称'],
                        desc=disease_dict['疾病描述'],
                        prevent=disease_dict['预防措施'],
                        cause=disease_dict['病因'],
                        easy_get=disease_dict['易感人群'],
                        cure_lasttime=disease_dict['疗程'],
                        cure_department=disease_dict['科室'],
                        cure_way=disease_dict['疗法'], 
                        cured_prob=disease_dict['治愈率'])
            g.create(node)
            # print('创建疾病实体：', disease_dict['疾病名称'])
        except:
            pass

    for each in drugs:#创建药物实体
        node = Node('Drug', name=each)
    g.create(node)

    for each in foods:#食物实体
        node = Node('Food', name=each)
    g.create(node)

    for each in checks:#检查
        node = Node('Check', name=each)
    g.create(node)

    for each in departments:#科室
        node = Node('Department', name=each)
    g.create(node)

    for each in producers:#科室
        node = Node('Producer', name=each)
    g.create(node)

    for each in symptoms:#症状
        node = Node('Symptom', name=each)
    g.create(node)

    g.relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
    g.relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
    g.relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
    g.relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
    g.relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
    g.relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
    g.relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
    g.relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
    g.relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
    g.relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
    g.relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')


build()
        

