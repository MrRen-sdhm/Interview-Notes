# 将指定文件夹下所有md文件中的图片以html格式居中
import os
import shutil
import glob

path = './'
modify_flag = False


def img_formate(file_in):
    global modify_flag
    #file_in = "桌面笔记本.md"
    print(file_in)
    file_out = os.path.splitext(file_in)[0] + "_out.md" # 分离文件名与扩展名，然后添加后缀
    #print(os.path.splitext(file_in)[0]) # 分离文件名与扩展名
    #print(file_out)

    modify_flag = False # 重置全局变量

    def parase_line(lines):
        global modify_flag
        for s in lines:
            #print(s)
            if s[:9] == "<img src=":
                modify_flag = True
                print(s)
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
                modify_flag = True
                print(s)
                url = s.split('(')[-1].split(')')[0]
                #print(url)
                s_out = '<div align="center"> <img src="%s" width="400px" /> </div>\n' % url
                #print(s_out)
                fp.write(s_out)
            else:
                fp.write(s)

    file = open(file_in, 'r', encoding='gbk')
    fp = open(file_out, 'w', encoding='gbk')
    try:
        lines = file.readlines()
    except  UnicodeDecodeError:
        fp.close()
        file.close()
        file = open(file_in, 'r', encoding='utf-8')
        fp = open(file_out, 'w', encoding='utf-8')
        lines = file.readlines()
        parase_line(lines)
    else:
        parase_line(lines)


    fp.close()
    file.close()

    print("Modify: ", modify_flag, "\n")
    if modify_flag: # 修改过原文件
        shutil.move( file_in, os.path.splitext(file_in)[0] + "_bak.md")
        shutil.move( file_out, file_in)
    else:
        os.remove(file_out)


#f_list = os.listdir(path)
f_list = glob.glob(os.path.join(path, '*.md'))
#print(f_list)
for f in f_list:
    #print (f)
    img_formate(f)
