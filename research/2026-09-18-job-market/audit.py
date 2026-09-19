import json,re,sys
from pathlib import Path
from analyze import prepare
root=Path(__file__).resolve().parent
raw=json.loads((root/'raw-evidence.json').read_text(encoding='utf-8'))
ids=[int(i) for i in sys.argv[1:]]
for i in ids:
 r=prepare(raw[i],i)
 print('\n###',i,r['company'],r['title'])
 print(r['header'])
 print(r['description'])
