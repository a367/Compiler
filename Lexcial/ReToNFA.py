# -*- coding: utf-8 -*-
# RegEx -> NFA
# Created by Shengjia Yan @2016-5-21
import networkx as nx
import matplotlib.pyplot as plt
import pydot
import os

class NFA:

    def __init__(self):
        self.graph = nx.MultiDiGraph()    # ��������ͼ
        self.first = -1       # ���
        self.last  = -1       # �յ�
        
    def __str__(self):
        return str(self.first) + '--' + str(self.graph[self.first]) + '--' + str(self.last)

    # �� nfa �洢�� .dot �ļ�
    def storeAsDot(self, name='nfa'):
        pass
        #nx.draw(self.graph)
        #nx.write_dot(self.graph, name + '.png')
        #dot = pydot.Dot(self.graph)
        #dot.write_png('zzz.png')

    # �� nfa �洢Ϊ dict��ʽ
    def graph2dict(self):
        self.dic = {}
        for node, nbrsdict in self.graph.adjacency_iter():
            EDGE = {}
            NBR = []
            for nbr, attr in nbrsdict.items():
                label = attr[0]['label']
                NBR.append(nbr)
            EDGE[label] = NBR
            self.dic[node] = EDGE

    def store(self):
        self.storeAsDot()
        self.graph2dict()
    
class NFAManager:
    def __init__(self):
        self.next_node = -1

    def feed(self, re):
        self.next_node = -1
        nfa = self.convert(re)
        nfa.store()
        return nfa

    # ���ӽڵ�
    def nextNode(self):
        self.next_node += 1
        return self.next_node

    # �� RegEx ת���� NFA
    def convert(self, input_str):
        
        # ����Բ����()��������Բ����)��λ��
        def findParenthesis(string, pos):
            temp = -1
            i = pos
            while i != len(string) and temp != 0:
                if string[i] == '(':
                    temp -= 1
                if string[i] == ')':
                    temp += 1
                    if temp == 0:
                        return i
                i += 1

        # ��������[]�������ҷ�����]��λ��
        def findSquareBrackets(string, pos):
            temp = -1
            i = pos
            while i != len(string) and temp != 0:
                if string[i] == '[':
                    temp -= 1
                if string[i] == ']':
                    temp += 1
                    if temp == 0:
                        return i
                i += 1
    
        # ���ս��ת��ΪNFA
        def convertTerminal2NFA(terminal):
            mg = NFA()
            mg.first = self.nextNode()
            mg.last = self.nextNode()
            mg.graph.add_edge(mg.first, mg.last, label=terminal)
            return mg

        # �ظ�
        def repeat(mg):
            first_nexts = [(i, mg.graph[mg.first][i][0]['label']) for i in mg.graph[mg.first]]
            for n, v in first_nexts:
                mg.graph.add_edge(mg.last, n, label=v)
            mg.graph.remove_node(mg.first)
            mg.first = mg.last
            return mg

        # ����
        def concat(mg1, mg2):
            mg1.graph = nx.union(mg1.graph, mg2.graph)
            mg1.graph.add_edge(mg1.last, mg2.first, label='epsilon')
            mg1.last  = mg2.last
            return mg1

        # ���Ʒ�
        def controlSymbols():
            return ['[', ']', '(', ')', '*', '|']

        # �ǿ��Ʒ���
        def isControlSymbol(char):
            return char in controlSymbols()

        # ���ս����
        def isTerminalSymbol(char):
            return not char in controlSymbols()

        # ��ȡ�����ս��
        def getAllTerminals(re):
            return set([char for char in re if isTerminalSymbol(char)])

        length = len(input_str)
        if length == 0:
            return False

        next_node = -1
        mg_stack = []
        i = 0

        while i < length:
            char = input_str[i]
            if isControlSymbol(char):   # �ǿ��Ʒ�
                if char == '(':
                    pos = findParenthesis(input_str, i + 1)
                    sub_mg = self.convert(input_str[i + 1 : pos])
                    mg_stack.append(sub_mg)
                    i = pos + 1
                if char == '[':
                    pos = findSquareBrackets(input_str, i+1)
                    sub_mg = self.convert(input_str[i + 1 : pos])
                    mg_stack.append(sub_mg)
                    i = pos + 1
                if char == '*':
                    prev = mg_stack.pop()
                    sub_mg = repeat(prev)
                    mg_stack.append(sub_mg)
                    i += 1
                if char == '|':
                    mg_stack.append(char)
                    i += 1
            elif isTerminalSymbol(char):
                mg_stack.append(convertTerminal2NFA(char))
                i += 1

        ret_mg = NFA()
        ret_mg.first = self.nextNode()
        ret_mg.last = self.nextNode()
        ret_mg.graph.add_nodes_from([ret_mg.first, ret_mg.last])

        prev = None
        for now in mg_stack:
            if now == '|':
                self.union(ret_mg, prev)
                prev = None
            else:
                if prev is not None:
                    prev = concat(prev, now)
                else:
                    prev = now
        if prev is not None:
            self.union(ret_mg, prev)
        return ret_mg

    # �ϲ�
    def union(self, nfa1, nfa2):
        nfa1.graph = nx.union(nfa1.graph, nfa2.graph)
        nfa1.graph.add_edge(nfa1.first, nfa2.first, label='epsilon')
        nfa1.graph.add_edge(nfa2.last, nfa2.last, label='epsilon')
        return nfa1


nfaManager = NFAManager()
nfa = nfaManager.feed('(0)|(1)|(a*)')
print nfa.dic
