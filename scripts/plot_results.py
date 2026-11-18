"""Plot real measured CSV rows after filling instance counts from AWS evidence."""
import csv,sys
import matplotlib.pyplot as plt
if len(sys.argv)!=3:raise SystemExit('Usage: python scripts/plot_results.py evidence/combined.csv evidence/latency.png')
rows=list(csv.DictReader(open(sys.argv[1],newline='')))
try:pts=[(int(r['instance_count_observed_manually']),float(r['mean_ms'])) for r in rows]
except ValueError:raise SystemExit('Replace FILL_FROM_CLOUDWATCH with measured instance counts first')
if len(pts)<2:raise SystemExit('Collect at least two experimental rows')
plt.plot([x for x,y in pts],[y for x,y in pts],marker='o');plt.xlabel('Observed healthy EC2 instance count');plt.ylabel('Mean response time (ms)');plt.title('Measured response time vs instance count');plt.grid(True);plt.savefig(sys.argv[2],dpi=160,bbox_inches='tight');print(sys.argv[2])
