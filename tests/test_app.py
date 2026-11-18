import json, os, subprocess, sys, time, unittest
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DemoTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'app/server.py')],env={**os.environ,'PORT':'18080'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(40):
   try:
    urlopen('http://127.0.0.1:18080/health',timeout=1);return
   except Exception:time.sleep(.1)
  raise RuntimeError('server failed')
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait(timeout=5)
 def test_health(self):
  self.assertEqual(json.load(urlopen('http://127.0.0.1:18080/health'))['status'],'ok')
 def test_restaurants(self):
  self.assertEqual(len(json.load(urlopen('http://127.0.0.1:18080/api/restaurants'))['restaurants']),3)
 def test_order(self):
  r=Request('http://127.0.0.1:18080/api/orders',data=b'{"restaurant_id":1}',headers={'Content-Type':'application/json'})
  self.assertEqual(urlopen(r).status,201)
 def test_bad_order(self):
  r=Request('http://127.0.0.1:18080/api/orders',data=b'{"restaurant_id":999}',headers={'Content-Type':'application/json'})
  with self.assertRaises(HTTPError) as e:urlopen(r)
  self.assertEqual(e.exception.code,400)
if __name__=='__main__':unittest.main()
