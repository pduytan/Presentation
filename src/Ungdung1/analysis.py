"""Reproduce the business case study from the original UCI workbook.

Install pandas, numpy, openpyxl, mlxtend and matplotlib in your environment.
Run: python analysis.py
"""
from pathlib import Path
import sys
import json
import math
import hashlib
import platform
from collections import Counter

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parents[1]
VENDOR = PROJECT_ROOT / 'tmp' / 'fpgrowth_vendor'
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))
import numpy as np
import pandas as pd
import mlxtend
from mlxtend.frequent_patterns import fpgrowth, association_rules

sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = PROJECT_ROOT / 'data'
RESULT = PROJECT_ROOT / 'outputs' / 'Ungdung1' / 'results'
RESULT.mkdir(parents=True, exist_ok=True)
source = DATA_DIR / 'Online Retail.xlsx'
cache = DATA_DIR / 'online_retail_raw.pkl'
if cache.exists():
    raw = pd.read_pickle(cache)
else:
    raw = pd.read_excel(source, engine='openpyxl', dtype={'InvoiceNo': str, 'StockCode': str})
    raw.to_pickle(cache)
raw['InvoiceNo'] = raw['InvoiceNo'].astype(str).str.strip().str.upper()
raw['StockCode'] = raw['StockCode'].astype(str).str.strip().str.upper()
raw['InvoiceDate'] = pd.to_datetime(raw['InvoiceDate'])
stats = {'source_rows': len(raw), 'source_columns': list(raw.columns),
         'source_date_min': str(raw.InvoiceDate.min()), 'source_date_max': str(raw.InvoiceDate.max()),
         'workbook_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
         'run_date': '2026-11-03', 'python': platform.python_version(),
         'pandas': pd.__version__, 'numpy': np.__version__, 'mlxtend': mlxtend.__version__}
stages = [{'step': 'Dữ liệu gốc toàn bộ quốc gia', 'rows': len(raw)}]
d = raw.loc[raw.Country.eq('United Kingdom')].copy()
stages.append({'step': 'Chỉ thị trường United Kingdom', 'rows': len(d)})
d = d.loc[~d.InvoiceNo.str.startswith('C')].copy()
stages.append({'step': 'Loại hóa đơn hủy', 'rows': len(d)})
d = d.loc[d.Quantity.gt(0)].copy()
stages.append({'step': 'Giữ số lượng dương', 'rows': len(d)})
d = d.loc[d.UnitPrice.gt(0)].copy()
stages.append({'step': 'Giữ đơn giá dương', 'rows': len(d)})
is_product = d.StockCode.str.fullmatch(r'\d{5}[A-Z]{0,2}', na=False)
stats['excluded_codes'] = d.loc[~is_product, 'StockCode'].value_counts().to_dict()
d = d.loc[is_product].copy()
stages.append({'step': 'Giữ mã hàng hóa năm chữ số và tối đa hai chữ cái', 'rows': len(d)})
label = d.dropna(subset=['Description']).copy()
label['Description'] = label.Description.str.strip()
label = label.groupby('StockCode').Description.agg(lambda s: s.value_counts().index[0]).to_dict()
dates = d.groupby('InvoiceNo').InvoiceDate.min()
pairs = d[['InvoiceNo', 'StockCode']].drop_duplicates()
stages.append({'step': 'Một lần hiện diện cho mỗi sản phẩm trong mỗi hóa đơn', 'rows': len(pairs)})
baskets = pairs.groupby('InvoiceNo').StockCode.agg(list)
n = len(baskets)
freq = Counter(x for row in baskets for x in row)
top = pd.DataFrame([{'code': k, 'name': label.get(k, k), 'count': v, 'support': v/n} for k,v in freq.items()])
top = top.sort_values(['count','code'], ascending=[False,True]).reset_index(drop=True)
top.to_csv(RESULT/'product_support.csv', index=False, encoding='utf-8-sig')
stats.update({'stages': stages, 'clean_line_rows': len(d), 'basket_item_pairs': len(pairs),
              'n_baskets': n, 'n_products': len(freq), 'missing_customer_rows_kept': int(d.CustomerID.isna().sum()),
              'basket_size_median': float(baskets.map(len).median()),
              'basket_size_mean': float(baskets.map(len).mean()),
              'n_single_item_baskets': int(baskets.map(len).eq(1).sum()),
              'date_min': str(d.InvoiceDate.min()), 'date_max': str(d.InvoiceDate.max()),
              'main_minsup': .02, 'main_minconf': .60, 'main_minlift': 1.5, 'max_len': 3,
              'min_count_main': math.ceil(.02*n)})
# Only globally infrequent items below the smallest tested threshold are removed.
# Retain ALL invoices, including those left without selected items, in the denominator.
codes = sorted(k for k,v in freq.items() if v/n >= .005)
idx = {k:i for i,k in enumerate(codes)}
arr = np.zeros((n,len(codes)), dtype=bool)
for i,row in enumerate(baskets):
    for x in row:
        if x in idx:
            arr[i,idx[x]] = True
frame = pd.DataFrame(arr, index=baskets.index, columns=codes)

def serialize_rules(rules, name):
    out = rules.copy()
    out['antecedents'] = out.antecedents.map(lambda s: '|'.join(sorted(s)))
    out['consequents'] = out.consequents.map(lambda s: '|'.join(sorted(s)))
    out.to_csv(RESULT/name, index=False, encoding='utf-8-sig')

sensitivity = []
main_fi = main_rules = None
for minsup in [.005,.01,.02,.03,.05]:
    fi = fpgrowth(frame, min_support=minsup, use_colnames=True, max_len=3)
    rules = association_rules(fi, num_itemsets=n, metric='confidence', min_threshold=.6)
    good = rules.loc[rules.lift.ge(1.5)].copy()
    counts = fi.itemsets.map(len).value_counts().to_dict()
    sensitivity.append({'minsup':minsup, 'min_count':math.ceil(minsup*n),
                        'itemsets':len(fi), 'singletons':counts.get(1,0), 'pairs':counts.get(2,0),
                        'triples':counts.get(3,0), 'rules':len(good)})
    print('THRESHOLD', sensitivity[-1], flush=True)
    if minsup == .02:
        main_fi, main_rules = fi.copy(), good.copy()
        serialize_rules(rules, 'rules_confidence60_before_lift_filter.csv')
assert main_fi is not None
pd.DataFrame(sensitivity).to_csv(RESULT/'sensitivity.csv',index=False,encoding='utf-8-sig')
stats['sensitivity'] = sensitivity
stats['n_itemsets'] = len(main_fi)
stats['n_rules'] = len(main_rules)
fi_out = main_fi.copy()
fi_out['itemsets'] = fi_out.itemsets.map(lambda s:'|'.join(sorted(s)))
fi_out['count'] = np.rint(fi_out.support*n).astype(int)
fi_out.to_csv(RESULT/'frequent_itemsets.csv',index=False,encoding='utf-8-sig')
main_rules = main_rules.sort_values(['support','confidence','lift'], ascending=False).reset_index(drop=True)
serialize_rules(main_rules, 'association_rules.csv')

# Select single-product rules with substantial joint support. Keep one direction
# per unordered pair to avoid presenting reversed copies as independent findings.
single_rules = main_rules.loc[main_rules.antecedents.map(len).eq(1)&main_rules.consequents.map(len).eq(1)]
selected = []
used_pairs = set()
for _,r in single_rules.iterrows():
    a,b=next(iter(r.antecedents)),next(iter(r.consequents))
    key=tuple(sorted([a,b]))
    if key in used_pairs:
        continue
    used_pairs.add(key)
    # Direct independent recount from original transaction sets.
    na=sum(a in row for row in baskets)
    nb=sum(b in row for row in baskets)
    nab=sum(a in row and b in row for row in baskets)
    assert abs(nab/n-float(r.support))<1e-12
    assert abs(nab/na-float(r.confidence))<1e-12
    assert abs((nab*n)/(na*nb)-float(r.lift))<1e-10
    selected.append({'a':a,'b':b,'a_name':label[a],'b_name':label[b],
                     'n_a':na,'n_b':nb,'n_ab':nab,'support':nab/n,'confidence':nab/na,
                     'reverse_confidence':nab/nb,'lift':(nab*n)/(na*nb)})
    if len(selected)==8:
        break
stats['selected_rules']=selected
stats['report_rules']=[selected[i] for i in [0,1,5]]

# Temporal check: discover candidates only before October, then recount them on
# October-December invoices. Test rules are never used to fit the train FP-tree.
cutoff=pd.Timestamp('2011-10-01')
train_ids=dates[dates.lt(cutoff)].index.intersection(frame.index)
test_ids=dates[dates.ge(cutoff)].index.intersection(frame.index)
assert len(train_ids.intersection(test_ids)) == 0
assert len(train_ids)+len(test_ids)==n
tr=frame.loc[train_ids]
te=frame.loc[test_ids]
train_fi=fpgrowth(tr,min_support=.02,use_colnames=True,max_len=3)
train_rules=association_rules(train_fi,num_itemsets=len(tr),metric='confidence',min_threshold=.6)
train_rules=train_rules.loc[train_rules.lift.ge(1.5)]
train_rules=train_rules.loc[train_rules.antecedents.map(len).eq(1)&train_rules.consequents.map(len).eq(1)]
train_rules=train_rules.sort_values(['support','confidence'],ascending=False)
temporal=[]
seen=set()
for _,r in train_rules.iterrows():
    a,b=next(iter(r.antecedents)),next(iter(r.consequents))
    key=tuple(sorted([a,b]))
    if key in seen: continue
    seen.add(key)
    va=te[a].to_numpy() if a in te else np.zeros(len(te),dtype=bool)
    vb=te[b].to_numpy() if b in te else np.zeros(len(te),dtype=bool)
    na,nb,nab=int(va.sum()),int(vb.sum()),int((va&vb).sum())
    temporal.append({'a':a,'b':b,'a_name':label[a],'b_name':label[b],
                     'train_support':float(r.support),'train_confidence':float(r.confidence),'train_lift':float(r.lift),
                     'test_support':nab/len(te),'test_confidence':nab/na if na else None,
                     'test_lift':nab*len(te)/(na*nb) if na*nb else None,
                     'test_n_a':na,'test_n_b':nb,'test_n_ab':nab})
    if len(temporal)==3:break
stats['temporal']={'cutoff':'2011-10-01','n_train':len(tr),'n_test':len(te),'rules':temporal}
stats['labels']=label
(RESULT/'stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
pairs.to_csv(RESULT/'basket_items.csv',index=False,encoding='utf-8-sig')
print(json.dumps({k:v for k,v in stats.items() if k not in ['labels','excluded_codes']},ensure_ascii=False,indent=2))
