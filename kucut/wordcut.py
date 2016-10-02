#! /usr/bin/python
# -*- coding: utf-8 -*-

import math,sys,string,re,bsddb,time,os.path,random,cPickle
import optparse

import AIMA.text
    
class NthGram(AIMA.text.NgramTextModel):
    def __init__(self,n,default):
        self._n = n
        AIMA.text.NgramTextModel.__init__(self,n=n,default=default)
        
    def train(self, token_lines, quiet=False):
        count = 0
        prev = 0
        total = len(token_lines)
        if not quiet: print '\nStart loading %d-gram' % (self._n)
        for token_line in token_lines:
            count += 1
            prev_word = []
            for t in token_line[1]:
                self.add_sequence(t[0])
                per = (count*100)/total
                if per != prev:
                    if not quiet: print '.',
                    prev = per

        if not quiet: print '\nComplete...'
        

class Dictionary:
    
    def __init__ (this, filename = None):
        this.dict = {}
        if filename is None: return

        this.extend(filename)
        
    def extend(this, filename):
        lines = open(filename,'r').readlines()      
        for line in lines:
            if line[0] != '#' or len(line.strip()) == 1:
                token = string.split(line)
                word = token[0]
                tag = []
                
                if len(token) > 1:
                    for t in token[1:]:
                        tag.append(t)
          
                if not this.contains(word):
                    this.add(word,tag)
        
    def add(this,word,tag):
        key1 = word[0]
        key2,key3 = '',''
        
        if len(word) > 1:
            key2 = word[1]
        if len(word) > 2:
            key3 = word[2]

        if this.dict.has_key(key1):
            if this.dict[key1].has_key(key2):
                if this.dict[key1][key2].has_key(key3):
                    if not this.dict[key1][key2][key3].has_key(word):
                        this.dict[key1][key2][key3][word] = tag
                else:
                    this.dict[key1][key2][key3] = {word:tag}
            else:
                this.dict[key1][key2] = {key3:{word:tag}}
        else:
            this.dict[key1] = {key2:{key3:{word:tag}}}
        
    def contains(this,word):
        key1 = word[0]
        key2,key3 = '',''
        
        if len(word) > 1:
            key2 = word[1]
        if len(word) > 2:
            key3 = word[2]
        
        if not this.dict.has_key(key1):
            return 0
        
        if not this.dict[key1].has_key(key2):
            return 0

        if not this.dict[key1][key2].has_key(key3):
            return 0
    
        return this.dict[key1][key2][key3].has_key(word)

    def gettag(this,word):
        key1 = word[0]
        key2,key3 = '',''
        
        if len(word) > 1:
            key2 = word[1]
        if len(word) > 2:
            key3 = word[2]
        
        if this.contains(word):
            return this.dict[key1][key2][key3][word]
        
        return []

    def count(this):
        i = 0
        for key1 in this.dict.keys():
            for key2 in this.dict[key1]:
                for key3 in this.dict[key1][key2]:
                    for word in this.dict[key1][key2][key3]:
                        i += 1
        return i
    
    def isprefix(this,word):
        key1 = word[0]
        key2,key3 = '',''

        if len(word) > 1:
            key2 = word[1]
        if len(word) > 2:
            key3 = word[2]

        if not this.dict.has_key(key1):
            return 0
    
        if key2 == '':
            return 1
        
        if not this.dict[key1].has_key(key2):
            return 0

        if key3 == '':
            return 1
        
        if not this.dict[key1][key2].has_key(key3):
            return 0

        if len(word) == 3:
            return 1

        for s in this.dict[key1][key2][key3]:
            if s != word and string.find(s,word) == 0:
                return 1
        return 0


class GenSyllable:
    def __init__(self,rules_file):
        self.rules = []
        self.variable = {}
        self.loadRules(rules_file)
    
    def loadRules(self, rules_file):
        lines = open(rules_file).readlines()
        stat = ''

        def mapVar(x):
            if self.variable.has_key(x):
                return self.variable[x]
            return x
        def trim(x):
            return x.strip().strip("'")
        
        
        def concat(x,y):
            return x+y
        
        for line in lines:
            if line.strip() == '#variable':
                stat = line.strip()
            elif line.strip() == '#rule':
                stat = line.strip()
            elif line.strip() != '' and stat != '':
                if stat == '#variable':
                    variable,value = map(trim,line.split(':='))
                    self.variable[variable] = value
                elif stat == '#rule':
                    tokens = map(trim,line.split('+'))
                    tokens = map(mapVar,tokens)
                    self.rules.append(reduce(concat,tokens))
            
    def contains(this, word):
        for rule in this.rules:
            reg = re.compile(rule).match(word)
            if reg is not None and reg.group() == word:
                return 1
        return 0


class Segmentation:
    
    def IsSymbol(c):
        if len(c) > 1:
            return 0
        if string.find('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\',:?.*&^%$#@!+_-><{}[]()/\\\"æ|Ï',c) > -1:
            return 1
        return 0
    IsSymbol = staticmethod(IsSymbol)
    
    def IsNumber(number):
        if len(number) > 1:
            for d in number:
                if string.find('0123456789,.๑๒๓๔๕๖๗๘๙๐'.decode('uft8').encode('cp874'),d)==-1:
                    return 0
            return 1
        if string.find('0123456789๑๒๓๔๕๖๗๘๙๐'.decode('utf8').encode('cp874'),number) > -1:
            return 1
        return 0
    IsNumber = staticmethod(IsNumber)

    def IsThaiChar(c):
        if len(c) > 1:
            return 0
        return not Segmentation.IsNumber(c) and not Segmentation.IsSymbol(c)
    IsThaiChar = staticmethod(IsThaiChar)

    def IsThaiWord(word):
        for w in word:
            if not Segmentation.IsThaiChar(w):
                return 0
        return 1
    IsThaiWord = staticmethod(IsThaiWord)   
    
    def __init__(this,input='',syllable=None,lexicon=None,debug=False,
                 quiet=False,database=None,gw=0.5,
                 lw=0.5,output_dir='',no_local=False,mode='word',
                 blank=None,home='',extend=None):
        this.hasunknown = 0
        this.completeList = []
        this.line = ''
        this.IsComplete = 0
        this.unknownWord = []
        this.dict = syllable
        this.lexiconDict = lexicon
        this.gensyl = GenSyllable(os.path.join(home,'dict/rules.txt'))
        this.preferenceDict = Dictionary(os.path.join(home,'dict/totalDict.txt'))
        this.suspectDict = Dictionary(os.path.join(home,'dict/hidden.txt'))
        this.input_file = ''
        this.prohibitPattern = {}
        this.debug = debug
        this.quiet = quiet
        this.mode = mode
        this.blank = blank
        this.home = home

        if database != None:
            this.trigram = bsddb.hashopen(database,'r')
            this.corpus_size = int(this.trigram['unigrams'])

        this.gw = float(gw)
        this.lw = float(lw)
        this.output_dir = output_dir
        this.no_local = no_local

        if extend != None:
            this.loadExtendDictionary(extend)
            
    def loadExtendDictionary(self, extend):
        tokens = extend.split(':')
        for token in tokens:
            if token == 'PERSON':
                self.preferenceDict.extend(os.path.join(self.home,'dict/firstname.txt'))
                self.preferenceDict.extend(os.path.join(self.home,'dict/lastname.txt'))
            elif token == 'COUNTRY':
                self.preferenceDict.extend(os.path.join(self.home,'dict/country.txt'))
            else:
                self.preferenceDict.extend(token)
            
    def setLine(this,s):
        this.line = s.strip()
        this.IsComplete = 0
    
    def _getchargroup(this,c):
        code = ord(c)
        if code >= 224 and code <= 228:
            return 2
        elif code == 210 or code == 211 or code == 208:
            return 3
        elif code == 209 or (code >= 212 and code <= 218) or (code >= 231 and code <= 238):
            return 1;
        elif code >= 161 and code <= 206:
            return 4
        else:
            return 5

    def presegment(this):
        output = '' 
        x = range(len(this.line))
        for i in x:
            if len(this.line)-i>2 and this._getchargroup(this.line[i])==4 and this._getchargroup(this.line[i+1])==1 and this._getchargroup(this.line[i+2])==3:
                output += (this.line[i]+this.line[i+1]+this.line[i+2]+' ')
                x[0:2]=[]
            elif len(this.line)-i>2 and this._getchargroup(this.line[i])==4 and this._getchargroup(this.line[i+1])==3 and this._getchargroup(this.line[i+2])==1:
                output += (this.line[i]+this.line[i+1]+this.line[i+2]+' ')
                x[0:2]=[]
            elif len(this.line)-i>2 and this._getchargroup(this.line[i])==4 and this._getchargroup(this.line[i+1])==1 and this._getchargroup(this.line[i+2])==1:
                output += (this.line[i]+this.line[i+1]+this.line[i+2]+' ')
                x[0:2]=[]
            elif len(this.line)-i>2 and this._getchargroup(this.line[i])==2 and this._getchargroup(this.line[i+1])==4 and this._getchargroup(this.line[i+2])==1:
                output += (this.line[i]+this.line[i+1]+this.line[i+2]+' ')
                x[0:2]=[]
            elif len(this.line)-i>1 and this._getchargroup(this.line[i])==4 and this._getchargroup(this.line[i+1])==1:
                output += (this.line[i]+this.line[i+1]+' ')
                x[0:1]=[]
            elif len(this.line)-i>1 and this._getchargroup(this.line[i])==4 and this._getchargroup(this.line[i+1])==3:
                output += (this.line[i]+this.line[i+1]+' ')
                x[0:1]=[]
            elif len(this.line)-i>1 and this._getchargroup(this.line[i])==2 and this._getchargroup(this.line[i+1])==4:
                output += (this.line[i]+this.line[i+1]+' ')
                x[0:1]=[]
            else:
                output += (this.line[i]+' ')
        return string.split(output[0:len(output)-1])
                
    def accessdict(this,d,pline,punc):
        clist,alist = [],[]
        start = 0
        i = 0
        while i < len(pline):
            pre = pline[i]
            if len(alist) > 0:
                j = 0
                while j < len(alist):
                    activepair = alist[j]

                    if punc != '':
                        temp = string.replace(activepair[0],punc,'') + pline[i]
                    else:
                        temp = activepair[0] + pline[i]
                        
                    temp2 = activepair[0] + punc + pline[i]

                    if d.contains(temp):
                        clist.append([temp2,[activepair[1],activepair[1]+len(temp)]])
                    
                    if d.isprefix(temp):
                        activepair[0] = temp2
                    else:
                        del alist[j]
                        j-=1
                    j+=1

                if d.isprefix(pline[i]) :
                    alist.append([pline[i],start])
            else:
                alist.append([pline[i],start])

            if d.contains(pline[i]):
                clist.append([pline[i],[start,start+len(pre)]])

            start += len(pre)
            i+=1

        return clist    

    def arrange(this,clist):
        result = []
        this.hasunknown = 1

        i = len(clist)-1
        while i>=0 :
            p = clist[i]
            word = p[0]
            position = p[1]
            start = position[0]
            end = position[1]
            if len(result) > 0:
                check = 0
                j = 0
                while j<len(result):
                    temp1 = result[j]
                    temp2 = temp1[1]
                    temp3 = temp1[0]

                    if end == temp2[0]:
                        result[len(result):len(result)+1] = [[word+' '+temp3,[position[0],temp2[1]]]]
                        if start == 0:
                            del result[j]
                            j-=1
                        check = 1
                    elif end < temp2[0] and temp2[1] != len(this.line):
                        del result[j]
                        j-=1

                    j+=1
                    
                if not check and end == len(this.line):
                    tmp = clist[i]
                    result[len(result):len(result)+1] = [[tmp[0],tmp[1]]]
            else:
                tmp = clist[i]
                result[len(result):len(result)+1] = [[tmp[0],tmp[1]]]
        
            i-=1
            
        if len(result) == 0:
            this.hasunknown = 1
        else:
            for p in result:
                if p[1][0] == 0 and p[1][1] == len(this.line):
                    this.hasunknown = 0
                    break

        if not this.hasunknown:
            i=0
            while i<len(result):
                p1 = result[i]
                p2 = p1[1]
                if p2[0] != 0 or p2[1] != len(this.line):
                    result[i:i+1] = []
                    i-=1
                i+=1

        return result

    def doguess(this,rlist,clist):
        gBegin = 0
        gEnd = len(this.line)
        gBegin2 = 0
        gEnd2 = len(this.line)
        this.IsComplete = 0

        maxBegin = len(this.line)+1

        for r in rlist:
            begin = r[1][0]
            end = r[1][1]
            if begin < maxBegin and end == len(this.line):
                maxBegin = begin
                gEnd = begin

        nearMax = len(this.line)+1
        sbound = 0

        for c in clist:
            begin = c[1][0]
            end = c[1][1]
            if maxBegin-end < nearMax and maxBegin-end > 0:
                nearMax = maxBegin - end
                gBegin = end
                sbound = begin

        lIndex = -1
        lmax = 0

        for c in clist:
            length = len(c[0])
            begin = c[1][0]
            end = c[1][1]
            if end == gBegin and length > lmax:
                lmax = length
                lIndex = clist.index(c)

        s1 = this.line[gBegin:gEnd]

        clist.insert(lIndex+1,[s1,[gBegin,gEnd]])
        
        this.unknownWord[len(this.unknownWord):len(this.unknownWord)+1] = [s1]

        overlap = 0
        for c in clist:
            begin = c[1][0]
            end = c[1][1]
            if begin == gBegin and end > gEnd:
                gBegin2 = end
                overlap = 1

        if overlap:
            i = len(rlist)-1
            while i >= 0:
                begin = rlist[i][1][0]
                end = rlist[i][1][1]
                if begin > gBegin2:
                    gEnd2 = begin
                    s2 = this.line[gBegin2:gEnd2]
                    if not this.dict.contains(s2):
                        this.unknownWord[len(this.unknownWord):len(this.unknownWord)+1] = [s2]
                    clist.insert(lIndex+3,[s2,[gBegin2,gEnd2]])
                    break
                i-=1
        
        rlist = []

        rlist = this.arrange(clist)

        if len(rlist) == 0 :
            return []

        for r in rlist:
            if r[1][0]  == 0 and r[1][1] == len(this.line):
                this.IsComplete = 1

        return rlist

    def divideAllCompleteList(self,clist):
        tmp = []
        mark = []
        for w,p in clist:
            tmp += p
        for i in set(tmp):
            check = True
            for w,p in clist:
                if i > p[0] and i < p[1]:
                    check = False
                    break
            if check:
                mark.append(i)

        mid = len(mark)/2 


        result = []
        result.append(self.line[0:mark[mid]])
        result.append(self.line[mark[mid]:len(self.line)])
        return result
    
    def combineResult(self,result1,result2):
        results = []
        if len(result1) == 0:
            return result2
        if len(result2) == 0:
            return result1
        for r1 in result1[0]:
            for r2 in result2[0]:
                results.append(r1+' '+r2)
        if len(result1) > 1 and len(result2) > 1:
            return results, result1[1] and result2[1]
    
    def mergeUnknownByHeuristic(self,tokens):
        result,tmp = '',''
        start = 0
        count = 0
        for token in tokens:
            if not start and (self.lexiconDict.contains(token) or Segmentation.IsSymbol(token)):
                result += ' '+token
            elif not start and (not self.lexiconDict.contains(token) or not Segmentation.IsSymbol(token) or not Segmentation.IsNumber(token)):
                start = 1
                result += ' '+token
            elif start and not count and self.suspectDict.contains(token):
                tmp = token
                count = 1
            elif start and not count and (Segmentation.IsSymbol(token) or not self.suspectDict.contains(token)):
                start = 0
                result += ' '+token
            elif start and not count and not self.lexiconDict.contains(token):
                result += token
            elif start and count and not self.lexiconDict.contains(token) and not Segmentation.IsSymbol(token):
                result += tmp+token
                tmp = ''
                count = 0
            elif start and count and (self.lexiconDict.contains(token) or Segmentation.IsSymbol(token)):
                result += ' '+tmp+' '+token
                count = start = 0
                tmp = ''

        if len(tokens) == 2:
            return (result+tmp).strip().split()
        else:
            return (result+' '+tmp).strip().split()
    
    def mergeSyllableByDictionary(self,split_line,my_dict,bypass=0,filter=True):
        self.setLine(split_line.replace(' ',''))
        tokens = split_line.split()

        completeList = self.accessdict(my_dict,tokens,'')

        if not bypass and len(completeList) > 40:
            result = self.divideAllCompleteList(completeList)
            pair = []
            for r in result:
                self.setLine(r)
                r = self.docut(bypass=1,filter=filter)
                tmp = []
                for x in r[0]:
                    for y in self.mergeSyllableByDictionary(x,my_dict,1,filter=filter):
                        tmp.append(y)
                pair = self.combineResult(pair,(tmp,0))
            al = pair[0]
            if len(al) > 1 and filter:
                al = self.filterResult(al)
            return al
        else:
            result = self.arrange(completeList)

            if result == None:
                return []
            if self.hasunknown:
                while result is not None and not self.IsComplete:
                    result = self.doguess(result,completeList)
            al = []
            for r in result:
                if al.count(r[0]) == 0:
                    al.append(r[0])
            
            if len(al) > 1 and filter:
                al = self.filterResult(al)

            return al
    
    def _hasUnknownWord(self,line):
        tokens = line.split()
        for token in tokens:
            if not self.lexiconDict.contains(token):
                return True
        return False
        
    def complete(self,clist):
        tmp = {}
        for w,p in clist:
            if p[0] not in tmp:
                tmp[p[0]] = [(w,p[1])]
            else:
                tmp[p[0]] += [(w,p[1])]

        s = len(self.line)
        t = 0
        X = tmp.keys()
        X.sort()
        fill = []
        for x in tmp:
            if x < s:
                s = x
            check = False
            for w,y in tmp[x]:
                if y > t:
                    t = y
                if y in tmp or y == len(self.line):
                    check = check or True
                else:
                    check = check or False
            if not check:
                check2 = False
                for i in X:
                    if i > y:
                        fill.append((y,i))
                        check2 = True
                        break
                if not check2:
                    fill.append((y,len(self.line)))

        if s != 0:
            fill.append((0,s))

        #if t != len(self.line):
        #    fill.append((t,len(self.line)))

        for s,t in fill:
            clist.append([self.line[s:t],[s,t]])

        ctmp = map(lambda x:(x[1],x[0]),clist)
        ctmp.sort()
        ctmp = map(lambda x:(x[1],x[0]),ctmp)

        return ctmp


    def docut(this,bypass=0,filter=True):
        this.unknownWord = []
        
        pline = this.presegment()

        this.completeList = this.accessdict(this.dict,pline,'')
        this.completeList = this.complete(this.completeList)

        #print 'line',this.line.decode('cp874')
        #for w,p in this.completeList:
        #    print w.decode('cp874'),p

        if not bypass and len(this.completeList) > 40:
            result = this.divideAllCompleteList(this.completeList)
            pair = []
            for r in result:
                this.setLine(r)
                pair = this.combineResult(pair,this.docut(bypass=1,filter=filter))
            al = pair[0]
            if len(al) > 1 and filter:
                al = this.filterResult(al)
        
            tmp_list = []
            if this.mode == 'word':
                for line in al:
                    tmp = this.mergeSyllableByDictionary(line,this.preferenceDict,filter=filter)
                    for t in tmp:
                        if tmp_list.count(t) == 0:
                            tmp_list.append(t)
                al = this.mergeUnknownSyllable(tmp_list)
                if filter:
                    al = this.filterResult(al)
            elif this.mode == 'morpheme':
                for line in al:
                    if this._hasUnknownWord(line):
                        tmp = this.mergeSyllableByDictionary(line,this.preferenceDict,filter=filter)
                        for t in tmp:
                            if tmp_list.count(t) == 0:
                                tmp_list.append(t)
                    else:
                        tmp_list.append(line)
                al = this.mergeUnknownSyllable(tmp_list)

            return al,pair[1] 

        else:
            result = this.arrange(this.completeList)
            if result == None:
                return [],[]
            if this.hasunknown:
                while result is not None and not this.IsComplete:
                    result = this.doguess(result,this.completeList)
                this.hasunknown = 1
            if len(result) == 0:
                return [],[]
            al = [] 
            for r in result:
                if al.count(r[0]) == 0:
                    al.append(r[0])
            if len(al) > 1 and filter:
                al = this.filterResult(al)
            tmp_list = []

            if this.mode == 'word':
                for line in al:
                    tmp = this.mergeSyllableByDictionary(line,this.preferenceDict,filter=filter)
                    for t in tmp:
                        if tmp_list.count(t) == 0:
                            tmp_list.append(t)

                #for t in tmp_list:
                #    print t.decode('cp874')
                al = this.mergeUnknownSyllable(tmp_list)
                #for a in al:
                #    print a.decode('cp874')
                #print ''

                if filter:
                    al = this.filterResult(al)
            elif this.mode == 'morpheme':
                for line in al:
                    if this._hasUnknownWord(line):
                        tmp = this.mergeSyllableByDictionary(line,this.preferenceDict,filter=filter)
                        for t in tmp:
                            if tmp_list.count(t) == 0:
                                tmp_list.append(t)
                    else:
                        tmp_list.append(line)
                al = this.mergeUnknownSyllable(tmp_list)
            elif this.mode == 'syllable':
                al = this.mergeUnknownSyllable(al)

            return al,this.hasunknown
        
    def filterResult(this,result,punc=''):
        max = 0
        maxlist = []
        for r in result:
            tokens = string.split(r)
            cost = len(string.replace(r,' ',''))  + 10000  - (len(tokens)*3)
            for token in tokens:
                if punc != '':
                    token = token.replace(punc,'')
                if not this.lexiconDict.contains(token):
                    if this.gensyl.contains(token):
                        cost -= 0.5
                    else:
                        cost -= 1.0
                elif len(token) == 1:
                    cost -= 0.5
                else:
                    cost+=0.5
            maxlist.append((cost,r))

        maxlist.sort()

        return [maxlist[-1][1]]

    def preMergeUnknownWord(self,results):
        al = []
        for result in results:
            token = string.split(result)
            i = 1
            result = token[0] 
            while i < len(token):
                if not self.lexiconDict.contains(token[i-1]) and \
                   not self.lexiconDict.contains(token[i]) and \
       ((Segmentation.IsThaiWord(token[i-1]) and Segmentation.IsThaiWord(token[i])) or\
       ((not Segmentation.IsThaiWord(token[i-1]) and not Segmentation.IsThaiWord(token[i])))):
                    result += token[i]
                else:
                    result += ' ' + token[i]
                i+=1
            if result[0] is ' ':
                result = result[1:len(result)]
            al.append(result)

        return al
    
    def mergeUnknownSyllable(this,unknownlist):
        al = []
        for unknown in unknownlist:
            token = string.split(unknown)
            result = ''
            j = 0
            while j < len(token):
                if len(token[j]) == 1 and token[j] != '_' and Segmentation.IsThaiChar(token[j]):
                    if j > 0 and token[j-1] != '_' and j < len(token)-1 and token[j+1] != '_':
                        if this.gensyl.contains(token[j-1]+token[j]) and this.gensyl.contains(token[j]+token[j+1]):
                            result += token[j]
                        elif this.gensyl.contains(token[j-1]+token[j]):
                            result += token[j]
                        elif this.gensyl.contains(token[j]+token[j-1]):
                            result += ' ' + token[j] + '+'
                        elif token[j] == 'Í' or token[j] == 'Ê':
                            result += ' ' + token[j] + '+'
                        elif this.lexiconDict.contains(token[j-1]):
                            result += ' ' + token[j] + '+'
                        else:
                            result += token[j]

                    elif j>0 and token[j-1] != '_':
                        result += token[j]
                    elif j<len(token)-1 and token[j+1] != '_':
                        result += ' ' + token[j] + '+'
                    elif j == 0:
                        result += ' ' + token[j] + '+'
                    else:
                        result += token[j]
                        
                elif len(token[j]) < 4 and j > 0 and not this.lexiconDict.contains(token[j]) and string.find(token[j],'ì') > -1:
                    result += token[j]
                elif j > 0 and this.gensyl.contains(token[j-1]+token[j]):
                    result += token[j]
                elif j > 0 and j < len(token)-1 and this.gensyl.contains(token[j-1]+token[j]+token[j+1]):
                    result += token[j] + token[j+1]
                    j += 1
                else:
                    result += ' '+token[j]
                j+=1

            result = string.replace(result,'+ ','')
            result = string.replace(result,'+','')
            
            # check len before (workaround)
            if len(result) > 0 and result[0] is ' ':
                result = result[1:len(result)]

            if al.count(result) == 0:
                al.append(result)
            
        return al
    
    def splitWordDisambiguous(self,result):
        before = len(result)
        rtmp = []
        if len(result) > 1:
            for j in range(len(result)-1):
                start = result[j].split()
                for r in result[j+1:]:
                    tokens = r.split()
                    tmp = []
                    for i in range(len(start)):
                        if i<len(start)-1 and i<len(tokens)-1 and start[i] != tokens[i]:
                            if start[i].find(tokens[i]) == 0:
                                if len(tmp) == 0 or tmp[-1] != start[i][:len(tokens[i])]:
                                    tmp.append(start[i][:len(tokens[i])])
                                if len(tmp) == 0 or tmp[-1] != start[i][len(tokens[i]):]:
                                    tmp.append(start[i][len(tokens[i]):])
                            elif tokens[i].find(start[i]) == 0:
                                if len(tmp) == 0 or tmp[-1] != tokens[i][:len(start[i])]:
                                    tmp.append(tokens[i][:len(start[i])])
                                if len(tmp) == 0 or tmp[-1] != tokens[i][len(start[i]):]:
                                    tmp.append(tokens[i][len(start[i]):])
                            elif start[i].find(tokens[i]) > 0:
                                if len(tmp) == 0 or tmp[-1] != start[i][:len(start[i])-len(tokens[i])]:
                                    tmp.append(start[i][:len(start[i])-len(tokens[i])])
                                if len(tmp) == 0 or tmp[-1] != start[i][len(start[i])-len(tokens[i]):]:
                                    tmp.append(start[i][len(start[i])-len(tokens[i]):])
                            elif tokens[i].find(start[i]) > 0:
                                if len(tmp) == 0 or tmp[-1] != tokens[i][:len(tokens[i])-len(start[i])]:
                                    tmp.append(tokens[i][:len(tokens[i])-len(start[i])])
                                if len(tmp) == 0 or tmp[-1] != tokens[i][len(tokens[i])-len(start[i]):]:
                                    tmp.append(tokens[i][len(tokens[i])-len(start[i]):])
                            else:
                                if len(tmp) != 0 and start[i].find(tmp[-1]) == 0 and tmp[-1] != start[i][len(start[i])-len(tmp[-1]):]:
                                    tmp.append(start[i][len(start[i])-len(tmp[-1]):])
                                    if tokens[i].find(tmp[-1]) == 0 or tmp[-1] != tokens[i][len(tokens[i])-len(tmp[-1]):]:
                                        tmp.append(tokens[i][len(tokens[i])-len(tmp[-1]):])
                                if len(tmp)!=0 and tokens[i].find(tmp[-1])==0 and tmp[-1] != tokens[i][len(tokens[i])-len(tmp[-1]):]:
                                    tmp.append(tokens[i][len(tokens[i])-len(tmp[-1]):])
                                    if start[i].find(tmp[-1]) == 0 or tmp[-1] != start[i][len(start[i])-len(tmp[-1]):]:
                                        tmp.append(start[i][len(start[i])-len(tmp[-1]):])
                        else:
                            tmp.append(start[i])
                    
                    if len(tmp) > 0:
                        rtmp.append(tmp)

            cat = lambda x,y:x+' '+y
            check = 0
            for r in rtmp:
                if len([x for x in r if len(x) == 1 and Segmentation.IsThaiChar(x)]) == 0:
                    s = reduce(cat,r)
                    if not check:
                        result = []
                        result.append(s)
                        check = 1
                    elif check and len(s) > len(result[0]):
                        result = []
                        result.append(s)
                    elif check and len(s) == len(result[0]):
                        result.append(s)

        wordAmbiguous = ''
        if len(result) < before:
            wordAmbiguous = result[0]   
                        
        return result,wordAmbiguous

    def mergeUnknownByRules(self,line):
        cat = lambda x,y:x+y
        pattern = r'.*(¹ÒÂ|¹Ò§|¹Ò§ÊÒÇ _) ([^_]+)'
        reg = re.compile(pattern)
        m = reg.match(line)
        if m is not None:
            name = m.group(2)
            if len(name.strip().split()) > 1:
                p = m.group(2).strip()
                return line
        return line

    def foo(self,pair,txt):
        s = ''
        for i in range(len(pair))[1:]:
            s += txt[pair[i-1]:pair[i]] + '+'
        return s.strip('+')

    def _df_search(self, link, start, end, txt, results):
        if not start in link:
            s = txt + ' ' + str(start)
            results.append(tuple(map(int,s.strip().split())))
            return
        for n in link[start]:
            self._df_search(link,n,end,txt+' '+str(start),results)
        return

    def tokenize(self,lines,style='Normal',space=0,
                 no_stat=False,skip=False,no_heuristic=False,get_all=False,
                 output_stream=None):
        results = []
        ambiguous = []
        wordAmList = []
        count = 0
        line_count = 0
        use_filter = not no_heuristic

        for line in lines:
            try:
                if isinstance(line, unicode):
                    line = line.strip().encode('iso8859_11')
                else:
                    line = line.strip().decode('utf8').encode('iso8859_11')
            except:
                print 'encoding error:', line

            if not self.quiet: print line_count
            tokens = string.split(line.replace('+','<-plus->').strip())
            tmp = []
            line_count += 1

            if space and len(tokens) == 0:
                results.append((line_count,[([''],1)]))
                continue
            
            for token in tokens:
                count+=1
                self.setLine(token)
                
                result,unknown = self.docut(filter=use_filter)

                if len(result) > 1:
                    result = self.prohibitDisambiguous(result)
                                
                if self.mode == 'word':
                    result = self.preMergeUnknownWord(result)
                if not no_stat:
                    result,wordAm = self.splitWordDisambiguous(result)
                elif no_stat and skip and len(result) > 1:
                    result = ['']
                elif no_stat and get_all and len(result) > 1:
                    print 'this option is not implemented yet'
                else:
                    result = [result[random.randrange(0,len(result))]]                  

                if no_stat:
                    if output_stream != None:
                        output_stream.write('%s\n' % (result[0]))
                    continue
                if not space:
                    if len(result) > 1:
                        ambiguous.append((count,[(r.split(),1) for r in result]))
                    else:
                        results.append((count,[(result[0].split(),1)]))
                else:
                    tmp = self.combineList(tmp,result)
                        
            if space:
                if len(tmp) > 1:
                    ambiguous.append((line_count,[(r.split(),1) for r in tmp]))
                elif len(tmp) > 0 and style=='Normal':
                    self.mergeUnknownByRules(tmp[0])
                    results.append((line_count,[(tmp[0].split(),1)]))

        if no_stat:
            return results,ambiguous
        
        if self.mode== 'word':
            if not no_stat:     
                model = NthGram(n=2,default=0)
                if not self.no_local:
                    model.train(results,self.quiet)
                results = self.bigramMergeUnknown(model,results,self.suspectDict)       

                model = NthGram(n=2,default=0)
                if not self.no_local:
                    model.train(ambiguous,self.quiet)
                ambiguous = self.bigramMergeUnknown(model,ambiguous,self.suspectDict)
                
                i = 0
                while i < len(ambiguous):
                    if len(ambiguous[i][1]) == 1:
                        results.append(ambiguous[i])
                        ambiguous.remove(ambiguous[i])
                        i-=1
                    i+=1
            
                ambiguous = self.bigramProbDisambiguous(results,ambiguous,style)
                results.sort()
        
            tmp_results = []

            for result in results:
                tmp_contents = []
                number,contents = result
                for content in contents:
                    tokens,modify = content
                    if len(tokens) > 1:
                        if not no_stat:
                            tokens = self.statWordDisambiguousLine(reduce(lambda x,y:x+' '+y,tokens)).split()
                        tokens = self.mergeUnknownByHeuristic(tokens)
                    tmp_contents.append((tokens,modify))
                tmp_results.append((number,tmp_contents))
            
            return tmp_results,ambiguous
        else:
            ambiguous = self.bigramProbDisambiguous(results,ambiguous,style)
            results.sort()
            return results,ambiguous

    def _getTrigram(self,x=None,y=None,z=None):
        if x != None and y != None and z != None:
            try:
                return float(self.trigram['%s %s %s'%(x,y,z)])/float(self.trigram['trigrams'])
            except KeyError,e:
                return 1.0/float(self.trigram['trigrams'])
        if x != None and y != None:
            try:
                return float(self.trigram['%s %s'%(x,y)])/float(self.trigram['bigrams'])
            except KeyError,e:
                return 1.0/float(self.trigram['bigrams'])
        try:
            return float(self.trigram['%s'%(x)])/float(self.trigram['unigrams'])
        except KeyError,e:
            return 1.0/float(self.trigram['unigrams'])
                
    def _mi(self,x,y):  
        p_x = self._getTrigram(x)
        p_y = self._getTrigram(y)
        p_xy = self._getTrigram(x+y)
        
        return math.log(p_xy/(p_x*p_y))     
    
    def _stat_global(self, s, side):
        n = len(s.split())
        if n == 3:
            x,y,z = s.split()
            if side == 'left':
                return 0.6*self._getTrigram(x,y,z)+0.3*self._getTrigram(y,z)+0.1*self._getTrigram(z)
            elif side == 'right':
                return 0.6*self._getTrigram(x,y,z)+0.3*self._getTrigram(x,y)+0.1*self._getTrigram(x)
        if n == 2:
            x,y = s.split()
            if side == 'left':
                return 0.7*self._getTrigram(x,y)+0.3*self._getTrigram(y)
            elif side == 'right':
                return 0.7*self._getTrigram(x,y)+0.3*self._getTrigram(x)
        return self._getTrigram(s)
            
    
    def statWordDisambiguousLine(self,line):
        result = []
        words = line.strip().split()
        x = y = z = a = b = l_mi_l = l_mi_r = g_mi_l = g_mi_r = 0
        l_cost = r_cost = 0
        cost =  [0,0]
        for i in range(len(words))[1:-1]:
            if self.lexiconDict.contains(words[i-1]+words[i]) and self.lexiconDict.contains(words[i]+words[i+1]):
                l_w_l = words[i-1]+words[i]
                l_w_r = words[i+1]
                
                r_w_l = words[i-1]
                r_w_r = words[i]+words[i+1]
                
                cost = []
                
                count = 0
                for w_l,w_r in [(l_w_l,l_w_r),(r_w_l,r_w_r)]:
                    try:
                        l_s = self._stat_global(words[i-3]+' '+words[i-2]+' '+w_l,'left')
                    except IndexError,e:
                        try:
                            l_s = self._stat_global(words[i-2]+' '+w_l,'left')
                        except IndexError,e:
                            l_s = self._stat_global(w_l,'left')
                                
                    try:
                        r_s = self._stat_global(w_r+' '+words[i+2]+' '+words[i+3],'right')
                    except IndexError,e:
                        try:
                            r_s = self._stat_global(w_r+' '+words[i+2],'right')
                        except IndexError,e:
                            r_s = self._stat_global(w_r,'right')

                    prob = (0.5*l_s)+(0.5*r_s)
                    f_prob = 0
                    if l_s + r_s != 0:
                        f_prob = (2.0*l_s*r_s)/(l_s+r_s)
                    
                        
                    if count == 0:
                        mi_l = self._mi(words[i-1],words[i])
                        cost.append('%.10f,%.10f,%.10f'%(prob,f_prob,mi_l))
                    else:
                        mi_r = self._mi(words[i],words[i+1])
                        cost.append('%.10f,%.10f,%.10f'%(prob,f_prob,mi_r))
                    count += 1

                test = 0
                for j in [0,1,2]:
                    test += int(float(cost[0].split(',')[j]) > float(cost[1].split(',')[j]))

                if test >= 2:
                    result.append(i-1)
                else:
                    result.append(i)
                
        output = words[0]
        for i in range(len(words))[1:]:
            if result.count(i-1):
                output += words[i]
            else:
                output += ' '+words[i]
                
        return output
    
    def bigramMergeUnknown(self,model,lines,suspect_list):
        results = []
        modify = count = pre = 0
        total = len(lines)
        Threshold1 = 100
        Threshold2 = 0.1

        for line in lines:
            count += 1
            per = (count*100)/total
            if per != pre:
                if not self.quiet: print '.',
                pre = per
            tmp = []
            for t in line[1]:
                L = [''] + t[0] + ['']
                modify_token = []
                skip = 0
                each_modify = 0
                if t[1]: # Check modification line
                    for i in range(len(L))[1:-1]: # Merge unknown by using Bigram
                        prev = L[i-1]
                        next = L[i+1]
                        token = L[i]
                        if (prev != '' and token != '') and not self.lexiconDict.contains(token) and Segmentation.IsThaiWord(token) and Segmentation.IsThaiWord(prev) and suspect_list.contains(prev):
                            if len(model) > 0 and (len(model)*model[(prev,token)] > 1.5 or L[i-2] == ''):
                                prev = modify_token[-1]
                                del modify_token[-1]
                                modify_token.append(prev+token)
                                modify =  each_modify = 1
                            else:
                                x,y = 0,0
                                x_p,y_p = 0.0,0.0
                                                            
                                if self.trigram.has_key(L[i-2]+' '+prev):
                                    x = float(self.trigram[L[i-2]+' '+prev])
                                    x_p = self._getTrigram(L[i-2],prev)
                                if self.trigram.has_key(prev+' '+token):
                                    y = float(self.trigram[prev+' '+token])
                                    y_p = self._getTrigram(prev,token)
                                ### first case ###
                                if (x == 0 and y == 0) or (x < y or x_p < y_p) or (x > y and (x < Threshold1 or x_p < Threshold2)):
                                    prev = modify_token[-1]
                                    del modify_token[-1]
                                    modify_token.append(prev+token)
                                    modify =  each_modify = 1
                                else:
                                    modify_token.append(token)
                                    
                        elif next != '' and token != '' and not self.lexiconDict.contains(token) and Segmentation.IsThaiWord(token) and Segmentation.IsThaiWord(next)  and suspect_list.contains(next):
                            if len(model) > 0 and (len(model)*model[(token,next)] > 1 or L[i+2] == ''):
                                modify_token.append(token+next)
                                modify = each_modify = skip = 1
                            else:
                                x,y = 0,0
                                x_p,y_p = 0.0,0.0
                                if self.trigram.has_key(next+' '+L[i+2]):
                                    x = float(self.trigram[next+' '+L[i+2]])
                                    x_p = self._getTrigram(next,L[i+2])
                                if self.trigram.has_key(token+' '+next):
                                    y = float(self.trigram[token+' '+next])
                                    y_p = self._getTrigram(token,next)
                                if (x == 0 and y == 0) or (x < y or x_p < y_p) or (x > y and (x < Threshold1 or x_p < Threshold2)):
                                    modify_token.append(token+next)
                                    modify = each_modify = skip = 1
                                else:
                                    modify_token.append(token)

                        elif not skip:
                            modify_token.append(token)
                        else:
                            skip = 0
                        
                    i = 0

                    while i < len(modify_token): #Merge adjacent unknown word
                        if each_modify and i < len(modify_token)-1 and not self.lexiconDict.contains(modify_token[i]) and not self.lexiconDict.contains(modify_token[i+1]):
                            modify_token[i] = modify_token[i]+modify_token[i+1]
                            del modify_token[i+1]
                        elif each_modify and i > 0 and not self.lexiconDict.contains(modify_token[i-1]) and not self.lexiconDict.contains(modify_token[i]):
                            modify_token[i] = modify_token[i-1]+modify_token[i]
                            del modify_token[i-1]
                        i+=1
                    tmp_token = []

                    tmp_token = modify_token
                        
                    if not tmp.count((tmp_token,each_modify)):
                        if len(tmp) > 0 and len(tmp[0][0]) > len(tmp_token):
                            tmp = []
                            tmp.append((tmp_token,each_modify))
                        elif len(tmp) == 0 or len(tmp[0][0]) == len(tmp_token):
                            tmp.append((tmp_token,each_modify))
                elif not tmp.count(t):
                    if len(tmp) > 0 and len(tmp[0][0]) > len(t[0]):
                        tmp = []
                        tmp.append(t)
                    elif len(tmp) == 0 or len(tmp[0][0]) == len(t[0]):
                        tmp.append(t)

            if each_modify:
                model.train([(line[0],tmp)],self.quiet)
                
            results.append((line[0],tmp))


        if modify:
            results = self.bigramMergeUnknown(model,results,suspect_list)

        return results

    def prohibitDisambiguous(self,results):
        al = []
        for result in results:
            if not self.IsProhibitPattern(result):
                al.append(result)
        return al
    
    def bigramProbDisambiguous(self,results,ambiguous,style):
        unigram_model = NthGram(n=1,default=1)
        bigram_model = NthGram(n=2,default=1)
        
        if not self.no_local:
            unigram_model.train(results,self.quiet)
            bigram_model.train(results,self.quiet)

        ambiguous_tmp = []
        
        if self.debug:
            local = open(self.output_dir+self.input_file+'.debug','w')
        
        def id(key):
            return int(self.dbindex[key])

        for lines in ambiguous:
            cost = []
            test = [[] for x in range(len(lines[1]))]
            first = True
            xcompare = []

            for j in range(len(lines[1][0][0])):
                compare = []
                diff = 0
                for i in range(len(lines[1])):
                    if len(compare) > 0 and not compare.count(lines[1][i][0][j]):
                        diff = 1
                        compare.append(lines[1][i][0][j])
                    else:
                        compare.append(lines[1][i][0][j])
                
                if diff:
                    for x in compare:
                        if x not in xcompare:
                            xcompare.append(x)

            for i in range(len(lines[1])):
                r_prob_ex,l_prob_ex,r_prob_in,l_prob_in = 1,1,1,1
                
                for j in range(len(lines[1][0][0])):
                    try:
                        n1 = lines[1][i][0][j+1]
                    except IndexError,e:
                        n1 = ''
                    try:
                        n2 = lines[1][i][0][j+2]
                    except IndexError,e:
                        n2 = ''
                    try:
                        p1 = lines[1][i][0][j-1]
                    except IndexError,e:
                        p1 = ''
                    try:
                        p2 = lines[1][i][0][j-2]
                    except IndexError,e:
                        p2 = ''
                        
                    w = lines[1][i][0][j]

                    if w in xcompare and p1 in xcompare and n1 not in xcompare:
                        r_prob_in_unigram,r_prob_in_bigram = 0,0
                        r_prob_ex_unigram,r_prob_ex_bigram,r_prob_ex_trigram = 0,0,0
                        
                        if w != '' and n1 != '' and n2 != '':
                            r_ex_tmp = self._stat_global(w+' '+n1+' '+n2,'right')
                        elif w != '' and n1 != '':
                            r_ex_tmp = self._stat_global(w+' '+n1,'right')
                        elif w != '':
                            r_ex_tmp = self._stat_global(w,'right')
                        
                        if len(unigram_model) > 0 and len(bigram_model) > 0:
                            r_in_tmp = (0.1*unigram_model[(w)])+(0.3*bigram_model[(w,n1)])
                        else:
                            r_in_tmp = 0

                        r_prob_ex = r_ex_tmp
                        r_prob_in = r_in_tmp

                    elif w in xcompare and p1 not in xcompare and n1 in xcompare:
                        l_prob_in_unigram,l_prob_in_bigram = 0,0
                        l_prob_ex_unigram,l_prob_ex_bigram,l_prob_ex_trigram = 0,0,0

                        if p2 != '' and p1 != '' and w != '':
                            l_ex_tmp = self._stat_global(p2+' '+p1+' '+w,'left')
                        elif p1 != '' and w != '':
                            l_ex_tmp = self._stat_global(p1+' '+w,'left')
                        elif w != '':
                            l_ex_tmp = self._stat_global(w,'left')
                        if len(unigram_model) > 0 and len(bigram_model) > 0:
                            l_in_tmp = (0.1*unigram_model[(w)])+(0.3*bigram_model[(p1,w)])
                        else:
                            l_in_tmp = 0
                        l_prob_ex = l_ex_tmp
                        l_prob_in = l_in_tmp

                prob_ex = (0.5*r_prob_ex)+(0.5*l_prob_ex)
                prob_in = (0.5*r_prob_in)+(0.5*l_prob_in)
                cost.append('%.15f'%((self.lw*prob_in) + (self.gw*prob_ex)))
                
            results.append((lines[0],[lines[1][cost.index(max(cost))]]))
                
            ambiguous_tmp.append(lines)

            if self.debug:
                for i in range(len(cost)):
                    local.write('%s ' % (cost[i]))
                    for x in lines[1][i][0]:
                        local.write(str(x)+' ')
                    local.write('\n')
                local.write('\n')

        if self.debug:
            local.close()

        return ambiguous_tmp


    def loadProhibitPattern(self,prohibit_file):
        lines = open(prohibit_file,'r').readlines()
        for line in lines:
            self.prohibitPattern[line.strip()] = 1

    def IsProhibitPattern(self,line):
        tokens = line.strip().split()
        for i in range(len(tokens))[1:]:
            code = tokens[i-1]+' '+tokens[i]
            if self.prohibitPattern.has_key(code):
                return 1
        return 0
    
    def combineList(self,list1,list2):
        if len(list1) == 0:
            return list2
        if len(list2) == 0:
            return list1

        results = []
        for l1 in list1:
            for l2 in list2:
                results.append(l1+' '+self.blank+' '+l2)

        return results

if __name__ == '__main__':
    syldict = Dictionary('dict/syl-lex.txt')
    lexdict = Dictionary('dict/syl-lex.txt')
    segmentor = Segmentation(syllable=syldict,lexicon=lexdict)
    segmentor.resegment('test_em.random.cut','test_em.txt','test_em.01.cut',2)
#   segmentor.simple_cut(open('../testxyz.txt').readlines(),'testxyz.01.syl-lex.cut')
    
#   segmentor.simple_cut_all(open('../testxyz.txt').readlines(),'testxyz.all.cut')
#   segmentor.em_cut(open('../testxyz.txt').readlines(),'xxx','em_prob_init.txt')
#   segmentor.em_gen_prob_file('testxyz.01.word.cut')
#   print segmentor.check_cost('testxyz.01.word.cut')
#   for i in [2,3,4,5,6,7,8,9]:
#       segmentor.resegment('testxyz.0%d.word.cut' % (i),
#                           open('../testxyz.txt').readlines(),
#                           'testxyz.0%d.word.cut' % (i+1))
