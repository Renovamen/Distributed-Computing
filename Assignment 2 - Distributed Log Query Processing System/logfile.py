import random
import sys
def creat_log(vm_id):
    def random_str():
        characters = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOsoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        random_str = ''
        for i in range(20):
            random_str += characters[random.randint(0, len(characters) - 1)]
        return random_str

    pages = ['/register','/login','add_user','recommend','/item/1','/item/2','/item/3','/shop/','/search/','/delete','/update','/change','/index','/category/a','/category/b','/category/c']
    for i in range(100):
        pages.append("/index/"+random_str())

    webs = ['www.google.com','www.baidu.com','tongji.edu.cn','allspark.ink']
    webs.extend(pages)

    hours = []
    for i in range(0,24):
        hours.append(str(i) if len(str(i)) > 1 else "0"+str(i))

    minutes = []
    for i in range(0,30):
        m = i+random.randint(0,29)
        minutes.append(str(m) if len(str(m)) > 1 else "0"+str(m))

    seconds = []
    for i in range(0,50):
        t = i+random.randint(0,9)
        seconds.append(str(t) if len(str(t)) > 1 else "0"+str(t))

    status = ['200','201','400','401','404','506']

    with open('machine{}.log'.format(vm_id), 'w') as f:
        f.write("ZouXiaohanissocool.\n")
        for i in range(0, 90):
            h = random.choice(hours)
            m = random.choice(minutes)
            s = random.choice(minutes)
            page = random.choice(pages)
            web = random.choice(webs)
            sta = random.choice(status)
            day = '2019-01-01'
            time_local = day + " " + h + ":" + m + ":" + s
            f.write(time_local + "\001" + page + "\001" + sta + "\001" + web + "\n")
        for i in range(0,10):
            day = 'xxxx-xx-xx'
            f.write(day + "\001" + page + "\001" + sta + "\001" + web + "\n")

creat_log(sys.argv[1])