import os
import shutil

file_in = "桌面笔记本.md"
file_out = file_in.split('.')[0] + "_out.md"
file = open(file_in, 'r', encoding='UTF-8')
fp = open(file_out, 'w')

lines = file.readlines()
for s in lines:
    #print(s)
    if "<img src=" in s:
        #print(s[10:])
        s1 = s[10:] # 后缀， 从第一个引号之后开始
        url_len = s1.find('"')
        #print (url_len) # 查找第一个引号
        url = s1[:url_len]
        #print(url)
        s_out = '<div align="center"> <img src="%s" width="400px" /> </div>\n' % url
        #print(s_out)
        fp.write(s_out)
    elif "![" in s:
        url = s.split('(')[-1].split(')')[0]
        #print(url)
        s_out = '<div align="center"> <img src="%s" width="400px" /> </div>\n' % url
        #print(s_out)
        fp.write(s_out)
    else:
        fp.write(s)

fp.close()
file.close()

shutil.move( file_in, file_in.split('.')[0] + "_bak.md")
shutil.move( file_out, file_in)

