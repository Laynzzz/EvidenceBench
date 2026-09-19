"""Build a compact, auditable 200-posting sample from observed job pages."""
import json,re
from collections import Counter
from pathlib import Path
from screen import get_records,ROOT
from analyze import PATTERNS

DECISIONS=json.loads((ROOT/'decisions.json').read_text(encoding='utf-8'))
INFRA={2,3,18,29,50,52,61,62,69,81,99,107,136,151,165,166,172,173,178,181,184,189,192,193,201,205}
PHD_REQUIRED={6,49,58,73,101,102,103,106,113,119,182,192,193,217}
EXPERIENCED={17,72,75,79,90,105,144,174,179}
EARLY_YEARS={84,142,171,196,201,206,207,219,227}
EXPLICIT_EARLY={43,81,110,135,146,148,152,155,156,157,158,159,161,163,164,176,177,178,186,197,199,203,204,208,221,222,226,228,229}
RESERVE={72:'7+ years required; reserve to prioritize earlier-career roles',75:'5+ years required; reserve to prioritize earlier-career roles'}

def family(r):
 if r['raw_index'] in INFRA:return 'ML infrastructure'
 if re.search(r'machine learning|deep learning|research scientist|researcher|computer vision|perception|image processing',r['title'],re.I):return 'MLE / modeling'
 return 'AI application / SWE'

def seniority(r):
 i=r['raw_index']
 if r['employment']=='Internship':return 'Internship / co-op'
 if i in EXPERIENCED:return 'Experienced comparison'
 if i in EARLY_YEARS:return 'Early career; 1–2+ years stated'
 if i in EXPLICIT_EARLY or re.search(r'graduate|new grad|entry.level|early.career|junior',r['title'],re.I):return 'Explicit graduate / entry-level'
 if i==96:return '3+ years academic or industry'
 return 'Level not explicit'

def location(r):
 if r['platform']=='LinkedIn':
  return next((x.split(' · ')[0].strip() for x in r['header'].splitlines() if ' · ' in x and 'ago' in x),'')
 h=r['header'].split('At a glance\n')[-1]
 loc=next((x for x in h.splitlines() if 'based in' in x),'')
 if not loc and r['raw_index']==19:return 'United States (remote; corroborated on LinkedIn)'
 return loc

def annotate(r):
 i=r['raw_index'];r['family']=family(r);r['seniority']=seniority(r);r['location']=location(r)
 r['degree_flag']='PhD required' if i in PHD_REQUIRED else ('PhD or equivalent experience' if i==200 else 'No PhD-only restriction identified')
 r['notes']=DECISIONS['notes'].get(str(i),'')
 if i==50:r['notes']+=' Currently pursuing a bachelor’s degree is specified.'
 if i==222:r['notes']+=' Graduate program despite AVP title; graduation window Dec 2026–Jun 2027 does not match Dec 2027.'
 if i==96:r['notes']+=' Three years can include academic experience.'
 if i==107:r['notes']+=' Very short employer description; qualifications not specified.'
 if i==219:r['notes']+=' Top Secret clearance role; 1+ years is the basic requirement, 6+ appears in preferred qualifications.'
 if re.search(r'\bunpaid\b',r['header'],re.I):r['notes']+=' Unpaid internship.'
 if re.search(r'(?:U\.?S\.? citizens?|United States citizens?|security clearance|Top Secret)',r['description'],re.I):r['notes']+=' Citizenship/clearance language present; check source eligibility.'
 # Exclude obvious recruiting-process false positives from the broad evaluation category.
 if i in {1,26,36,175}:r['skill_mentions'].pop('Evaluation / experimentation',None)
 if i==208:r['skill_mentions']['Evaluation / experimentation']='Prompt regression, output validation, and behavioral consistency checks.'
 return r

def main():
 rows=[annotate(r) for r in get_records()]
 excluded=[];selected=[]
 for r in rows:
  i=r['raw_index'];reason=DECISIONS['exclude'].get(str(i))
  if not reason and not r['recent']:reason='Date not verified within window'
  if not reason and not r['description_complete']:reason='Incomplete description'
  if not reason and i in RESERVE:reason=RESERVE[i]
  if reason:excluded.append({'raw_index':i,'company':r['company'],'title':r['title'],'source_url':r['source_url'],'reason':reason})
  else:selected.append(r)
 counts=Counter(r['employment'] for r in selected)
 assert counts=={'Internship':100,'Full-time':100},counts
 assert len({r['source_url'] for r in selected})==200
 assert all(r['recent'] and r['location'] and len(r['description'])>100 for r in selected)
 assert all('Full-time' in r['header'] for r in selected if r['employment']=='Full-time')
 reqs=[(r['employer_group'],r['requisition']) for r in selected if r['requisition']]
 assert len(reqs)==len(set(reqs)), 'Duplicate requisition'
 selected.sort(key=lambda r:(r['employment']!='Internship',r['raw_index']))
 counters=Counter();public=[]
 for r in selected:
  counters[r['employment']]+=1;r['id']=('I' if r['employment']=='Internship' else 'F')+f"{counters[r['employment']]:03d}"
  p={k:r[k] for k in ['id','raw_index','company','title','employment','platform','source_url','location','observed_posting_age','reposted','retrieved_at','family','seniority','degree_flag','requisition','notes']}
  p['skill_mentions']=list(r['skill_mentions']);public.append(p)
 (ROOT/'job-sample-200.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'screening-log.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf-8')
 subsets={'All':selected,'Internships':[r for r in selected if r['employment']=='Internship'],'Full-time':[r for r in selected if r['employment']=='Full-time'],'Without TikTok/ByteDance':[r for r in selected if r['employer_group']!='ByteDance / TikTok']}
 for f in ['MLE / modeling','AI application / SWE','ML infrastructure']:subsets[f]=[r for r in selected if r['family']==f]
 subsets['Internships without PhD requirement']=[r for r in subsets['Internships'] if r['degree_flag']!='PhD required']
 subsets['Explicit entry-level, without PhD restriction']=[r for r in subsets['Full-time'] if r['seniority']=='Explicit graduate / entry-level' and not r['degree_flag'].startswith('PhD')]
 stats={'raw_collected':len(rows),'selected':len(selected),'excluded_or_reserve':len(excluded),'employment':dict(counts),'platform':dict(Counter(r['platform'] for r in selected)),'employer_groups':len(set(r['employer_group'] for r in selected)),'employers':Counter(r['employer_group'] for r in selected).most_common(),'reposted':sum(r['reposted'] for r in selected),'seniority_full_time':dict(Counter(r['seniority'] for r in subsets['Full-time'])),'degree_by_employment':{e:dict(Counter(r['degree_flag'] for r in selected if r['employment']==e)) for e in counts},'families':{e:dict(Counter(r['family'] for r in selected if r['employment']==e)) for e in counts},'subsets':{name:{'n':len(rs),'skills':{s:sum(s in r['skill_mentions'] for r in rs) for s in PATTERNS}} for name,rs in subsets.items()}}
 (ROOT/'statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
 table=['# 200 recent U.S. MLE and AI engineering postings','', 'Observed September 18, 2026. Window: August 19–September 18, using the latest displayed post/repost date. Exactly 100 internships and 100 permanent full-time roles. Relative ages are preserved rather than converted to invented exact dates. Reposted = yes only when the platform explicitly displayed that label.','', 'This is a purposive search sample. Role families and seniority are researcher classifications. Skill columns record mentions, not necessarily mandatory requirements. A role appearing here is not a statement that the applicant meets its degree, graduation-date, or work-authorization conditions. Sources may require sign-in.','']
 for e in ['Internship','Full-time']:
  table+=['## '+e+' (100)','', '| ID | Employer and role | Location | Source | Observed age | Reposted | Family | Level | Degree restriction | Skill mentions | Notes |','|---|---|---|---|---|---|---|---|---|---|---|']
  for r in public:
   if r['employment']!=e:continue
   fields=[r['id'],r['company']+' — '+r['title'],r['location'],f"[{r['platform']}]({r['source_url']})",r['observed_posting_age'],'Yes' if r['reposted'] else 'Not labeled',r['family'],r['seniority'],r['degree_flag'],', '.join(r['skill_mentions']),r['notes']]
   table.append('| '+' | '.join(str(x).replace('|','/').replace('\n',' ') for x in fields)+' |')
  table.append('')
 (ROOT/'job-sample-200.md').write_text('\n'.join(table),encoding='utf-8')
 print(json.dumps({k:v for k,v in stats.items() if k not in ['subsets','employers']},indent=2))
 print('TOP EMPLOYERS',stats['employers'][:8])
 print('SKILL COUNTS: all / intern / full-time / without ByteDance')
 for s in PATTERNS:print(s,*[stats['subsets'][g]['skills'][s] for g in ['All','Internships','Full-time','Without TikTok/ByteDance']])

if __name__=='__main__':main()
