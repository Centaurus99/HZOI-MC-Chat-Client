import tkinter as tk
import requests
import json
import time
import threading

url = ''
headers = {}


root = tk.Tk(className = ' HZOI MC Chat Client')
root.geometry("300x250")
root.resizable(width=False, height=False)
frm1 = tk.Frame(root, pady = 5)
frm2 = tk.Frame(root)
frm3 = tk.Frame(root)
frm4 = tk.Frame(root)
label = tk.Label(frm1, text = 'URL:')
PreIn = tk.Entry(frm1, width = 30)
Prebutton = tk.Button(frm1, text="Start", width = 5, height = 1)
Out = tk.Text(frm2, width = 40, height = 12, state = 'disabled')
Meg1 = tk.Message(frm3, width = 100)
Meg2 = tk.Message(frm3, width = 100)
In = tk.Entry(frm4, width = 35, state = 'disabled')
button = tk.Button(frm4, text="Send", width = 5, height = 1, state = 'disabled')

def SetMessage(Meg, s, col = None):
    if (col != None):
        Meg.config(fg = col)
    Meg.config(text = s)
    Meg.update()

def Get():
    timestamp = 0
    while(1):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)))
        get_res = requests.get(url + '/up/world/world/' + str(timestamp) , headers = headers)
        SetMessage(Meg1, 'Get code:' + str(get_res.status_code))
        if (get_res.status_code != 200):
            Meg1.config(fg = 'red')
            continue
        else:
            Meg1.config(fg = 'green')
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
                Out.insert('insert', s1, 'LightSteelBlue')
                Out.insert('insert', s2 + '\n')
                Out.config(state = 'disabled')
                Out.see('end')
                Out.update()
                with open('message.txt', 'ab+') as f:
                    f.write((s+'\n').encode('utf-8'))
                print(s)
        time.sleep(1)

def Send(event):
    s = In.get()
    print(s)
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
    print(url)
    if (url[:4] != 'http'):
        url = 'http://' + url
    print(url)
    iscookie = 0
    while (iscookie == 0):
        get_res = requests.get(url + '/up/world/world/1')
        if (get_res.status_code != 200):
            SetMessage(Meg1, 'Cookie请求错误', 'red')
            print('Cookie请求错误')
            continue
        iscookie = 1
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
            print ("Error: 无法启动 Get 线程")
    root.bind('<Return>', Send)
    button.bind('<Button-1>', Send)
    In.config(state = 'normal')
    button.config(state = 'normal')

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
In.focus()
root.mainloop()