# -*- coding: utf-8 -*-
import json
import os
import garbage
import base64
import tkinter as tk
import tkinter.messagebox
import tts
import uuid
from tkinter import filedialog
import pygame
pygame.mixer.init()

# 京东API密钥
jd_appkey = '输入你的'
jd_secretkey = '输入你的'
get_cityid = '310000'
gul_text = '欢迎使用垃圾分类系统\n 本软件基于京东Neuhub开放API开发'
# 初始化Tkinter
window = tk.Tk()
window.title('垃圾分类系统--Made by Siyuanxiong')
window.geometry('500x300')
cityId = tk.Variable(window, value='310000')
path_var = tk.StringVar()
# 背景
background = tk.Label(window, text=gul_text, bg='#808080', font=('Arial', 22), width=500, height=5).pack()
tk.Label(window, text='城市邮编：', font=('Arial', 18)).place(x=70, y=150)
tk.Label(window, text='文件地址：', font=('Arial', 18)).place(x=70, y=200)
inputCityId = tk.Entry(window, show=None, font=('Arial', 18), textvariable=cityId).place(x=165, y=150, anchor='nw')
inputpath = tk.Entry(window, show=None, font=('Arial', 18), textvariable=path_var).place(x=165, y=200, anchor='nw')
# 回车查询
window.bind('<Return>', lambda event: search())


def get_path():
    filetypes = [("png文件", "*.png"), ('jpg文件', '*.jpg')]
    path = filedialog.askopenfilename(title='选择单个文件', filetypes=filetypes)
    path_var.set(path)


def assign_cityid():
    global get_cityid
    get_cityid = cityId.get()


def search():
    global ps
    f = open(path_var.get(), 'rb')
    imgbase64 = base64.b64encode(f.read()).decode()

    url = 'https://aiapi.jd.com/jdai/garbageImageSearch'
    bodyStr = '{"cityId":\"' + get_cityid + '\","imgBase64":\"' + imgbase64 + '\"}'
    params = {
        'appkey': jd_appkey,
        'secretkey': jd_secretkey
    }

    response = garbage.wx_post_req(url, params, bodyStr=bodyStr)

    data = json.loads(response.text)
    list = []
    for index in range(len(data['result']['garbage_info'])):
        global max_index
        list.append(data['result']['garbage_info'][index]['confidence'])
        max_index = list.index(max(list))

    catalog = data['result']['garbage_info'][max_index]['cate_name']
    ps = data['result']['garbage_info'][max_index]['ps']
    tts_read()
    tk.messagebox.showinfo('垃圾类型为：', "垃圾类型为："+catalog+"\n"+ps)


def tts_read():
    url = 'https://aiapi.jd.com/jdai/tts_vip'
    bodyStr_ori = '\'' + "请注意"+ ps + '\''  # body中的内容
    bodyStr = bodyStr_ori.encode("UTF-8")
    params = {
        'Service-Type': 'synthesis',
        'Request-Id': uuid.uuid1(),
        'Sequence-Id': '-1',
        'Protocol': '1',
        'Net-State': '2',
        'Applicator': '1',
        'Property': '{"platform":"Linux","version":"0.0.0.1","parameters":{"aue":"3","vol":"10.0","sr":"16000","sp":"1.0","tim":"0","tte":"0"}}',
        'appkey': jd_appkey,
        'secretkey': jd_secretkey
    }

    response_tts = tts.wx_post_req(url, params, bodyStr=bodyStr)
    data = json.loads(response_tts.text)
    audio_base64 = data['result']['audio']
    resultdata = base64.b64decode(audio_base64)
    audio = open('audio.mp3', "wb")
    audio.write(resultdata)
    audio.close()
    pygame.mixer.music.load("audio.mp3")
    pygame.mixer.music.play()
    os.remove('audio.mp3')


#三个按钮的生成
tk.Button(window, text="确认", command=assign_cityid).place(x=400, y=150)
tk.Button(window, text="选择文件", command=get_path).place(x=400, y=200)
tk.Button(window, text="查询", command=search).place(x=240, y=250)

#循环体保持
window.mainloop()





