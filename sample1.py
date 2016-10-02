# -*- coding: utf-8 -*-
from kucut import SimpleKucutWrapper as KUCut
myKUCut = KUCut()
result = myKUCut.tokenize([u"ทดสอบทดสอบ"])
print u"\n".join(
            [u"\n".join(
                [u" ".join(
                    [w for w in line])
                     for line in p])
                 for p in result])
