import tkinter as tk
import requests
import json
import time
import threading
import ctypes


#隐藏窗口
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)

url = ''
headers = {}
#尝试自动补全
try:
    print(url)
    with open('url.txt', 'rb') as fin:
        url = fin.read().decode('utf-8')
    print(url)
except:
    pass

#GUI元素创建
root = tk.Tk(className = ' HZOI MC Chat Client')
root.geometry("300x250")
root.resizable(width=False, height=False)
frm1 = tk.Frame(root, pady = 5)
frm2 = tk.Frame(root)
frm3 = tk.Frame(root)
frm4 = tk.Frame(root)
label = tk.Label(frm1, text = 'URL:')
PreIn = tk.Entry(frm1, width = 30)
PreIn.insert('insert', url)
Prebutton = tk.Button(frm1, text="Start", width = 5, height = 1)
Out = tk.Text(frm2, width = 40, height = 12, state = 'disabled')
Meg1 = tk.Message(frm3, width = 150)
Meg2 = tk.Message(frm3, width = 150)
In = tk.Entry(frm4, width = 35, state = 'disabled')
button = tk.Button(frm4, text="Send", width = 5, height = 1, state = 'disabled')

#更改Message部件中的文字
def SetMessage(Meg, s, col = None):
    if (col != None):
        Meg.config(fg = col)
    Meg.config(text = s)
    Meg.update()

#保持与服务器连接，获取消息
def Get():
    timestamp = 0
    while(1):
        #print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)))
        get_res = requests.get(url + '/up/world/world/' + str(timestamp) , headers = headers)
        #SetMessage(Meg1, 'Get code:' + str(get_res.status_code))
        if (get_res.status_code != 200):
            SetMessage(Meg1, 'Unconnected', 'red')
            #Meg1.config(fg = 'red')
            continue
        else:
            SetMessage(Meg1, 'Connected', 'green')
            #Meg1.config(fg = 'green')
        data = json.loads(get_res.content)
        for num in data['updates']:
            if (num['timestamp'] <= timestamp):
                continue
            if (timestamp == 0):
                with open('message.txt', 'ab+') as f:
                    f.write(('\n-------------------- {} --------------------\n').format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(num['timestamp'] / 1000))).encode('utf-8'))
            timestamp = num['timestamp']
            if (num['type'] == 'chat'):
                s1 = '[{}] <{}>: '.format(num['source'], num['playerName'])
                s2 = num['message']
                s = s1 + s2
                Out.config(state = 'normal')
                Out.insert('end', s1, 'LightSteelBlue')
                Out.insert('end', s2 + '\n')
                Out.config(state = 'disabled')
                Out.see('end')
                Out.update()
                with open('message.txt', 'ab+') as f:
                    f.write((s+'\n').encode('utf-8'))
                #print(s)
        #Get间隔
        time.sleep(1)

#按下Send按钮，发送消息
def Send(event):
    s = In.get()
    #print(s)
    In.delete(first = 0, last = tk.END)
    if (s == ''):
        return
    json =  {"name" : "","message" : s}
    SetMessage(Meg2, 'Pending...', 'grey')
    post_res = requests.post(url + '/up/sendmessage', json = json)
    if (post_res.status_code == 200): 
        Meg2.config(fg = 'green')
    else:
        Meg2.config(fg = 'red')
    SetMessage(Meg2, 'Post code:' + str(post_res.status_code))

#尝试URL连接
def GetStart():
    err = 0
    try:
        get_res = requests.get(url + '/up/world/world/1', timeout = 5)
    except:
        err = 1
    if (err or get_res.status_code != 200):
        if err:
            SetMessage(Meg1, 'URL错误', 'red')
            print('URL错误')
        else:
            SetMessage(Meg1, 'Cookie请求错误', 'red')
            print('Cookie请求错误')
        root.bind('<Return>', Start)
        Prebutton.bind('<Button-1>', Start)
        Prebutton.config(state = 'normal')
        PreIn.config(state = 'normal')
        return
    headers['Cookie'] = get_res.headers['Set-Cookie']
    print(headers['Cookie'])
    isthread = 0
    while (isthread == 0):
        try:
            thread1 = threading.Thread(target = Get)
            thread1.setDaemon(True)
            thread1.start()
            isthread = 1
        except:
            SetMessage(Meg1, '无法启动 Get 线程', 'red')
            print ("Error: 无法启动 Get 线程")
    root.bind('<Return>', Send)
    button.bind('<Button-1>', Send)
    In.config(state = 'normal')
    button.config(state = 'normal')
    In.focus()

#按下Start按钮
def Start(event):
    global url
    global headers
    url = PreIn.get()
    if (url == ''):
        return
    root.unbind('<Return>')
    Prebutton.unbind('<Button-1>')
    Prebutton.config(state = 'disabled')
    PreIn.config(state = 'disabled')
    SetMessage(Meg1, 'Connecting...', 'grey')
    if (url[:4] != 'http'):
        url = 'http://' + url
    
    isthread = 0
    while (isthread == 0):
        try:
            thread0 = threading.Thread(target = GetStart)
            thread0.start()
            isthread = 1
        except:
            SetMessage(Meg1, '无法启动 GetStart 线程', 'red')
            print ("Error: 无法启动 GetStart 线程")

root.bind('<Return>', Start)
Prebutton.bind('<Button-1>', Start)
Out.tag_config('LightSteelBlue', foreground = '#B0C4DE')
frm1.pack(fill = 'x')
frm2.pack(fill = 'x')
frm3.pack(fill = 'x')
frm4.pack(fill = 'x')
Out.pack()
label.pack(side = 'left')
Prebutton.pack(side = 'right')
PreIn.pack(side = 'left')
button.pack(side = 'right')
In.pack(side = 'left')
Meg1.pack(side = 'left')
Meg2.pack(side = 'right')
PreIn.focus()
root.mainloop()