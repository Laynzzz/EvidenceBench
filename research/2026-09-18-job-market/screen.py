import json,re
from pathlib import Path
from collections import Counter
from difflib import SequenceMatcher
from analyze import prepare,normalize
ROOT=Path(__file__).resolve().parent
def company_key(s):
 s=normalize(s)
 for tail in [' inc',' llc',' corporation',' incorporated',' co']:
  if s.endswith(tail):s=s[:-len(tail)]
 if s.startswith('tiktok') or s=='bytedance':return 'ByteDance / TikTok'
 return s
def get_records():
 raw=json.loads((ROOT/'raw-evidence.json').read_text(encoding='utf-8'))
 rows=[prepare(r,i) for i,r in enumerate(raw)]
 for r in rows:
  r['employer_group']=company_key(r['company'])
  if r['raw_index']==87:r['employment']='Internship'
 return rows
if __name__=='__main__':
 rows=get_records()
 print('TOTAL',len(rows),Counter(r['employment'] for r in rows))
 for r in rows:
  if r['employment']=='Full-time':
   print(r['raw_index'],r['company'],'|',r['title'],'|',r['observed_posting_age'],'|',r['experience_excerpts'])
 print('INCOMPLETE',[(r['raw_index'],r['title']) for r in rows if not r['description_complete'] or len(r['description'])<400])
 print('POTENTIAL DUPLICATES')
 for i,a in enumerate(rows):
  for b in rows[:i]:
   if a['employer_group']!=b['employer_group'] or a['employment']!=b['employment']:continue
   title_sim=SequenceMatcher(None,normalize(a['title']),normalize(b['title'])).ratio()
   sim=SequenceMatcher(None,a['description'][:10000],b['description'][:10000],autojunk=True).ratio()
   if title_sim>.87 or sim>.84:
    print(a['raw_index'],b['raw_index'],round(title_sim,2),round(sim,2),a['title'],'|',b['title'])
