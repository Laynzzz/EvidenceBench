"""Reproducible preparation of job-description evidence collected through the UI."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AS_OF = '2026-09-18'

PATTERNS = {
    'Python': r'\bpython\b',
    'PyTorch': r'\bpytorch\b|\btorch\b',
    'TensorFlow / JAX': r'\btensorflow\b|\bjax\b|\bkeras\b',
    'SQL': r'\bsql\b|\bpostgres(?:ql)?\b',
    'Data preparation / pipelines': r'data (?:pipeline|preprocess|processing|curation|cleaning|quality|augmentation)|feature engineering|\betl\b|training data|datasets?',
    'Model training / adaptation': r'(?:train|training|fine.?tun|finetun|adapt)[\w -]{0,35}(?:model|neural|LLM)|(?:model|neural|LLM)[\w -]{0,35}(?:train|fine.?tun)|\bfine.?tuning\b|\bfinetuning\b',
    'Evaluation / experimentation': r'\bevaluat\w*\b|\bbenchmark\w*\b|\bablation\w*\b|\bexperiment\w*\b|A/B test|model performance',
    'Statistics / ML foundations': r'\bstatistic\w*\b|\bprobability\b|linear algebra|machine learning (?:fundamentals|algorithms|principles)|statistical learning|\boptimization\b',
    'Classical ML / scikit-learn': r'scikit.?learn|\bsklearn\b|\bxgboost\b|\blightgbm\b|random forests?|gradient boost|logistic regression',
    'LLMs / generative AI': r'\bLLMs?\b|large language|generative AI|\bGenAI\b|foundation models?',
    'Retrieval / RAG / ranking': r'\bRAG\b|retrieval|rerank|re.?rank|\branking\b|vector (?:database|search|store)|semantic search|recommendation systems?|recommender',
    'Agents / tools': r'\bagentic\b|\bagents?\b|tool.?call|function.?call|\bLangGraph\b',
    'LoRA / PEFT': r'\bLoRA\b|\bQLoRA\b|\bPEFT\b|parameter.efficient',
    'Hugging Face': r'hugging\s?face|\btransformers library\b',
    'API / backend engineering': r'\bAPIs?\b|\bREST\b|\bFastAPI\b|\bbackend\b|\bback.end\b|microservices?',
    'Cloud': r'\bAWS\b|\bAzure\b|\bGCP\b|Google Cloud|cloud infrastructure|cloud platforms?',
    'Docker / Kubernetes': r'\bDocker\b|\bKubernetes\b|\bk8s\b|containerization',
    'Serving / deployment': r'\bdeploy\w*\b|model serving|inference (?:pipeline|service|engine|system)|production (?:ML|AI|models?|systems?)',
    'Monitoring / observability': r'\bmonitor\w*\b|\bobservability\b|\btelemetry\b|\bPrometheus\b|\bGrafana\b',
    'Distributed / performance': r'distributed (?:systems?|training|computing)|\bCUDA\b|\bTriton\b|\bTensorRT\b|\bvLLM\b|\bONNX\b|\blatency\b|\bthroughput\b|\bquantization\b',
    'Experiment tracking tools': r'\bMLflow\b|Weights (?:&|and) Biases|\bwandb\b|\bDVC\b',
    'OpenCV': r'\bOpenCV\b',
    'Computer vision / multimodal': r'computer vision|multimodal|image (?:processing|segmentation|classification)|\bperception\b|vision.language',
    'Software testing / CI': r'unit test|integration test|automated test|\bpytest\b|\bCI/CD\b|continuous integration|software testing|test automation|prompt regression',
    'Algorithms / data structures': r'data structures?|\balgorithms?\b',
    'JavaScript / TypeScript / React': r'\bJavaScript\b|\bTypeScript\b|\bReact\b',
}

def normalize(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()

def prepare(record, index):
    hs = record['platform'] == 'Handshake'
    text = record.get('text', '')
    desc = text.split('Job description\n', 1)[-1] if hs else record.get('description', '')
    if hs:
        desc = re.split(r'\nLess\n|\nWhat they\x27re looking for\n|\nAbout the employer\n|\nSimilar Jobs\n', desc, maxsplit=1)[0]
    header = text.split('Job description\n', 1)[0] if hs else record.get('header', '')
    company = record.get('company') or header.split('\n')[0]
    title = record['title'].strip()
    date_match = re.search(r'(?:Reposted\s+|Posted\s+)?(?:\d+\s+(?:minute|hour|day|week|month)s?\s+ago|today|yesterday)', header, re.I)
    date_text = date_match.group(0) if date_match else ''
    age_match = re.search(r'(\d+)\s+(minute|hour|day|week|month)', date_text, re.I)
    age = None
    if age_match:
        age = int(age_match[1]) * {'minute': 1/1440, 'hour': 1/24, 'day': 1, 'week': 7, 'month': 30}[age_match[2].lower()]
    if date_text.lower() == 'today': age = 0
    if date_text.lower() == 'yesterday': age = 1
    recent = age is not None and age <= 30 and 'month' not in date_text.lower()
    internship = bool(re.search(r'\bintern(?:ship)?\b|\bco.op\b|student researcher', title, re.I)) or (hs and bool(re.search(r'\nInternship\n', header)))
    employment = 'Internship' if internship else 'Full-time'
    req = re.search(r'Job Code:\s*([A-Za-z0-9]+)', desc)
    degree = 'PhD restricted' if re.search(r'\bPh\.?D\.?\b|\bdoctoral\b', title, re.I) else 'Review description'
    entry = bool(re.search(r'graduate|new grad|entry.level|\bjunior\b|\bengineer I\b', title, re.I))
    years = re.findall(r'\b\d+\+?(?:\s*[-–]\s*\d+)?\s+years?[^.\n]{0,100}', desc, re.I)
    matched = {}
    for name, pattern in PATTERNS.items():
        matches = list(re.finditer(pattern, desc, re.I))
        if matches:
            m = matches[0]
            matched[name] = re.sub(r'\s+', ' ', desc[max(0,m.start()-100):min(len(desc),m.end()+160)]).strip()
    return {
        'raw_index': index, 'platform': record['platform'], 'company': company, 'title': title,
        'employment': employment, 'source_url': record['url'], 'observed_posting_age': date_text,
        'age_days_approx': age, 'recent': recent, 'reposted': 'reposted' in date_text.lower(),
        'retrieved_at': record['retrievedAt'], 'entry_level_title': entry, 'degree_flag': degree,
        'experience_excerpts': years, 'requisition': req[1] if req else '',
        'header': header, 'description': desc, 'skill_mentions': matched,
        'description_complete': not bool(re.search(r'\n(?:\.\.\.|…)\nMore\n', desc)),
        'dedup_key': normalize(company.replace(' Inc.', '').replace(', Inc.', ''))+'|'+normalize(title),
    }

def main():
    raw = json.loads((ROOT/'raw-evidence.json').read_text(encoding='utf-8'))
    records = [prepare(r,i) for i,r in enumerate(raw)]
    (ROOT/'prepared-evidence.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'captured':len(records),'platforms':Counter(r['platform'] for r in records),'employment':Counter(r['employment'] for r in records),'recent':sum(r['recent'] for r in records),'reposted':sum(r['reposted'] for r in records)},indent=2))
    for r in records:
        print(f"{r['raw_index']:03d} | {r['employment']:10s} | {r['observed_posting_age']:22s} | {r['company']} | {r['title']}")

if __name__ == '__main__':
    main()
