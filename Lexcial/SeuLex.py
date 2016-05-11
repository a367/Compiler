#coding=utf8
import new
lex_path = '../code/lex.l'

class Re_Token():
    def __init__(self, lexer, re):
        self.lexer = lexer
        self.func = None
        self.re = re
        self.name = re

    def extends(self):
        if self.func != None:
            func = 'def callBack(self):\n' 
            for code in self.func.split('\n'):
                func+='\t'+code+'\n'
            exec func + '_method = callBack'
            self.__dict__['callBack'] = new.instancemethod(_method,self,None)


class Lex():

    # 初始化
    def __init__(self, path):
        self.lineno = 0
        with open(lex_path,'r') as f:
            self.parserLexFile(f.read())
    
    # 读取lex文件信息
    def parserLexFile(self, content):
        #定义区，规则区，用户定义代码区
        (define, rule, user) = content.split('%%')

        # 定义区数据读取
        temp_token = {}
        define = define.replace('\t',' ')
        defines = [d for d in define.split('\n') if d != '']
        for d in defines:
            token_name = d[:d.index(' ')]
            token_re = d[d.index('['):d.rindex(']')+1]
            temp_token[token_name] = token_re

        
        # 规则区数据读取
        tokenArr = self.ReTokenArr = []
        rules = [r for r in rule.split('\n') if r != '']
        code_flag = False
        code = ''
        cur_Token = None
        for r in rules:
            #print r
            if code_flag:
                if r.find('}') != -1:
                    code_flag = False
                    cur_Token.func = code[:-1]
                    tokenArr.append(cur_Token)
                    code = ''
                else:
                    code += r.strip() + '\n'
            elif r.find('"') != -1:
                token_re = r[r.index('"')+1:r.rindex('"')]
                tokenArr.append(Re_Token(self, token_re))
            elif r.find('{') == -1:
                token_re = r.strip()
                tokenArr.append(Re_Token(self, token_re))
            else:
                token_re = r[:r.rindex('{')].strip()
                cur_Token = Re_Token(self, token_re)
                code_flag = True

        # 替换定义区正规表达式
        for token in tokenArr:
            for k,v in temp_token.iteritems():
                    token.re = token.re.replace('{'+k+'}',v)
            token.extends()

        self.ReToNFA()
        # 用户定义代码区
        pass

    # 解析正规表达式
    def ReToNFA(self):
        for t in self.ReTokenArr:
            
            
lexer = Lex('../code/lex.l')


#NFA = {
#    'id':1,
#    0:{'a':[0,1],'b':[0],'ee':None},
#    1:{'a':None,'b':[2],'ee':None}
#    }

#print NFA[0]['a']