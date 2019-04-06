import yaml
import logging
import socket
import thread
import json
import time
import random

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(threadName)-10s %(message)s',
    filename='Gossiper.log.' + str(int(time.time())),
    filemode='w',
)

LOGGER = logging.getLogger('Gossiper')

# gossip() 和 listen() 同步
member_list_lock = thread.allocate_lock()

def find_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

# 每个节点维护的成员列表
class MemberList(object):
    def __init__(self, gossiper):
        super(MemberList, self).__init__()
        self.gossiper = gossiper
        self.introducer_ip = gossiper.conf['introducer']['ip']
        self.threshold = gossiper.conf['threshold']
        # heartbeat 格式: {'heartbeat' : heartbeat, 'timestamp' : timestamp, 'status' : status}
        self.members = {}

    def __str__(self):
        delinator_begin = '%sMemberlist Begin%s\n' % ('-' * 15, '-' * 15)
        content = ['%s : %6d, %f, %s\n' % (id, info['heartbeat'], info['timestamp'], info['status']) for id, info in self.members.iteritems()]
        delinator_end = '%sMemberlist End%s\n' % ('-' * 15, '-' * 18)
        return delinator_begin + ''.join(content) + delinator_end

    def has_introducer(self):
        for id in self.members:
            if id.split('_')[0] == self.introducer_ip:
                return True
        return False

    def add_introducer(self):
        id = self.introducer_ip
        self.members[id] = {
            'heartbeat': 0, 
            'timestamp': 0,
            'status': 'ADDED',
        }
        LOGGER.info('[Added Introducer] %s : %s' % (id, str(self.members[id])))

    def del_introducer(self):
        if self.introducer_ip in self.members:
            del self.members[self.introducer_ip]
            LOGGER.info('[Deleted Introducer] %s' % self.introducer_ip)

    def merge(self, rumor):
        for id, heard in rumor.iteritems():
            if self.introducer_ip in self.members and id.split('_')[0] == self.introducer_ip:
                self.del_introducer()

            if heard['status'] == 'LEFT':
                # 收到重复的 LEFT rumor
                if not id in self.members or self.members[id]['status'] == 'LEFT':
                    continue
                else:
                    self.members[id].update({
                        'heartbeat' : heard['heartbeat'],
                        'timestamp' : time.time(),
                        'status'    : 'LEFT',
                    })
                    LOGGER.info('[LEFT] %s : %s' % (id, str(self.members[id])))
            elif heard['status'] == 'JOINED':
                # 监听到新节点加入
                if not id in self.members:
                    self.members[id] = {
                        'heartbeat' : heard['heartbeat'],
                        'timestamp' : time.time(),
                        'status'    : 'JOINED',
                    }
                    LOGGER.info('[JOINED] %s : %s' % (id, str(self.members[id])))
                else:
                    mine = self.members[id]
                    # 接受到 heartbeat 后更新信息
                    if heard['heartbeat'] > mine['heartbeat']:
                        mine.update({
                            'heartbeat' : heard['heartbeat'],
                            'timestamp' : time.time(),
                            'status'    : 'JOINED',
                        })
                        # LOGGER.info('[UPDATED] %s : %s' % (id, str(self.members[id])))
            else:
                LOGGER.info('Unhandled status (%s) in rumor' % heard['status'])


    def refresh(self):
        # 更新成员状态
        for id, info in self.members.items(): 
            if info['status'] == 'ADDED':
                continue
            if info['status'] == 'JOINED' and time.time() - info['timestamp'] > float(self.threshold['suspect']):
                info['status'] = 'SUSPECTED'
                LOGGER.info('[Suspected] %s : %s' % (id, self.members[id]))
            elif info['status'] == 'SUSPECTED' and time.time() - info['timestamp'] > float(self.threshold['fail']):
                LOGGER.info('[Failing] %s : %s' % (id, self.members[id]))
                del self.members[id]
            elif info['status'] == 'LEFT' and time.time() - info['timestamp'] > float(self.threshold['forget']):
                LOGGER.info('[Forgeting] %s : %s' % (id, self.members[id]))
                del self.members[id]

        if not self.has_introducer() and not self.gossiper.is_introducer():
            self.add_introducer()

    def get_one_to_gossip_to(self, status=('JOINED', 'ADDED')):
        candidates = [id for id, info in self.members.iteritems() if info['status'] in status]
        if not candidates:
            return None
        dest_id = random.choice(candidates)
        dest_ip = dest_id.split('_')[0]
        return dest_ip

    def gen_rumor(self, dest_ip):
        rumor_filter = lambda m : m[1]['status'] in ('JOINED', 'LEFT') and m[0].split('_')[0] != dest_ip
        rumor_candidates = {id : {'heartbeat' : info['heartbeat'], 'status' : info['status']} for id, info in self.members.iteritems()}
        rumor = dict(filter(rumor_filter, rumor_candidates.iteritems()))
        rumor[self.gossiper.id] = {
            'heartbeat' : self.gossiper.heartbeat,
            'status'    : self.gossiper.status,
        } 
        return rumor

    def count_member(self, status):
        return sum([1 for info in self.members.values() if info['status'] in status])

# 节点
class Gossiper(object):
    def __init__(self):
        super(Gossiper, self).__init__()
        with open('conf.yaml') as f:
            self.conf = yaml.safe_load(f)
        self.ip = find_local_ip()

        self.id = '%s_%d' % (self.ip, int(time.time()))
        self.heartbeat = 1
        self.timestamp = time.time()
        self.status = 'JOINED'
        
        # 自己不在自己维护的成员列表中
        self.member_list = MemberList(self)
        if not self.is_introducer():
            self.member_list.add_introducer()

    def is_introducer(self):
        return self.ip == self.conf['introducer']['ip']

    def heartbeat_once(self, last=False):
        self.heartbeat += 1
        self.timestamp = time.time()
        if last:
            self.status = 'LEFT'

    def gossip(self):
        LOGGER.info('Start gossiping!')
        while True:
            member_list_lock.acquire()
            self.member_list.refresh()

            if self.status == 'TO_LEAVE':
                dest_ip = self.member_list.get_one_to_gossip_to(('JOINED'))
                # 向成员列表中的节点发送自己要离开的信息
                if dest_ip:
                    self.heartbeat_once(last=True)
                    rumor = self.member_list.gen_rumor(dest_ip)
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(json.dumps(rumor), (dest_ip, self.conf['port']))
                    except Exception:
                        pass
                # 发送完 状态变为 AFTER_LEFT
                self.status = 'AFTER_LEFT'
                break
            elif self.status == 'JOINED':
                dest_ip = self.member_list.get_one_to_gossip_to()
                if dest_ip:
                    self.heartbeat_once()
                    rumor = self.member_list.gen_rumor(dest_ip)
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(json.dumps(rumor), (dest_ip, self.conf['port']))
                    except Exception:
                        pass
            else:
                LOGGER.info('Unhandled status (%s) of gossiper' % self.status)

            member_list_lock.release()

            time.sleep(float(self.conf['interval']['gossip']))

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.conf['port']))
        LOGGER.info('Start listening!')
        while self.status == 'JOINED':
            rumor = json.loads(sock.recvfrom(1024)[0].strip())
            if rumor:
                member_list_lock.acquire()
                self.member_list.merge(rumor)
                member_list_lock.release()

    def reading(self):
        while True:
            counter = 3 - self.member_list.count_member(['JOINED', 'SUSPECTED'])
            print(time.strftime('%Y-%m-%d %H:%M:%S'), "The number of failed member is:", counter)

            time.sleep(float(self.conf['interval']['reading']))

    def run(self):
        thread.start_new_thread(self.gossip,  ())
        thread.start_new_thread(self.listen,  ())
        while True:
            # 命令列表
            cmd = raw_input('----------------\nCommand:\n----------------\nlist (list members)\nself (my id)\nleave\n----------------\n')
            if cmd == 'list':
                print(self.member_list)
            elif cmd == 'self':
                print(self.id)
            elif cmd == 'leave':
                # 发送离开信息
                self.status = 'TO_LEAVE'
                LOGGER.info('Leaving...')
                # 等待离开信息发送完
                while self.status != 'AFTER_LEFT':
                    pass
                LOGGER.info('Left completely.')
                break
            else:
                print('Wrong command.')

if __name__ == '__main__':
    gossiper = Gossiper()
    gossiper.run()




        