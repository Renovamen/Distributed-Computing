import unittest
from client import createThread

class MyTest(unittest.TestCase):
    # 频繁出现的内容
    def test_frequent(self):
        frequent = '2019-01-01'
        res = createThread('machine.log', frequent)
        length = len(res)
        for i in range(length):
            if 'is shut down' in res[i]:
                res[i] = ''
        res = ''.join(res)
        res = res.strip().split('\n')
        self.assertEqual(len(res), 270)
        self.assertTrue(res[0].startswith(frequent))

    # 一般出现的内容
    def test_infrequent(self):
        infrequent = 'xxxx-xx-xx'
        res = createThread('machine.log', infrequent)
        length = len(res)
        for i in range(length):
            if 'is shut down' in res[i]:
                res[i] = ''
        res = ''.join(res)
        res = res.strip().split('\n')
        self.assertEqual(len(res), 30)
        self.assertTrue(res[0].startswith(infrequent))

    # 很少出现的内容
    def test_rare(self):
        rare ='ZouXiaohanissocool'
        res = createThread('machine.log', rare)
        length = len(res)
        for i in range(length):
            if 'is shut down' in res[i]:
                res[i] = ''
        res = ''.join(res)
        res = res.strip().split('\n')
        self.assertEqual(len(res), 3)
        self.assertTrue(res[0].startswith(rare))

if __name__ == '__main__':
    unittest.main()