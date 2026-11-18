"""Small bounded HTTP load test. Use only on infrastructure you own."""
import argparse, concurrent.futures, csv, statistics, time
from urllib.request import urlopen
p=argparse.ArgumentParser()
p.add_argument('--url',required=True,help='Your own ALB URL')
p.add_argument('--requests',type=int,default=100)
p.add_argument('--workers',type=int,default=5)
p.add_argument('--output',default='evidence/load-results.csv')
a=p.parse_args()
if not (1<=a.requests<=2000 and 1<=a.workers<=20):p.error('Safety limit: <=2000 requests, <=20 workers')
def hit(_):
 t=time.perf_counter()
 try:
  with urlopen(a.url.rstrip('/')+'/api/cpu',timeout=10) as r:r.read();code=r.status
 except Exception:code=0
 return (time.perf_counter()-t)*1000,code
start=time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex: results=list(ex.map(hit,range(a.requests)))
lat=[v for v,c in results if c==200]
if not lat:raise SystemExit('No successful requests; check ALB and targets')
lat.sort()
from pathlib import Path
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['requests','workers','success','failed','mean_ms','p95_ms','duration_s','instance_count_observed_manually'])
 w.writerow([a.requests,a.workers,len(lat),len(results)-len(lat),round(statistics.mean(lat),2),round(lat[max(0,int(.95*len(lat))-1)],2),round(time.perf_counter()-start,2),'FILL_FROM_CLOUDWATCH'])
print('Saved',out,'; success',len(lat),'/',len(results),'mean ms',round(statistics.mean(lat),2))
