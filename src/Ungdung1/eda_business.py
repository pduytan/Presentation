"""Explore the source data and the exact transaction population used in the report."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent
PROJECT_ROOT=ROOT.parents[1]
DATA_DIR=PROJECT_ROOT/'data'
RESULT_DIR=PROJECT_ROOT/'outputs'/'Ungdung1'/'results'
FIG_DIR=PROJECT_ROOT/'outputs'/'Ungdung1'/'figures'
RESULT_DIR.mkdir(parents=True,exist_ok=True)
FIG_DIR.mkdir(parents=True,exist_ok=True)
vendor=PROJECT_ROOT/'tmp'/'fpgrowth_vendor'
if vendor.exists():sys.path.insert(0,str(vendor))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
from matplotlib.ticker import FuncFormatter
sys.stdout.reconfigure(encoding='utf-8')
stats=json.loads((RESULT_DIR/'stats.json').read_text(encoding='utf-8'))
cache=DATA_DIR/'online_retail_raw.pkl'
raw=pd.read_pickle(cache) if cache.exists() else pd.read_excel(DATA_DIR/'Online Retail.xlsx',dtype={'InvoiceNo':str,'StockCode':str})
raw['InvoiceNo']=raw.InvoiceNo.astype(str).str.strip().str.upper()
raw['StockCode']=raw.StockCode.astype(str).str.strip().str.upper()
raw['InvoiceDate']=pd.to_datetime(raw.InvoiceDate)
d=raw.loc[raw.Country.eq('United Kingdom') & ~raw.InvoiceNo.str.startswith('C') & raw.Quantity.gt(0) & raw.UnitPrice.gt(0) & raw.StockCode.str.fullmatch(r'\d{5}[A-Z]{0,2}',na=False)].copy()
pairs=d[['InvoiceNo','StockCode']].drop_duplicates()
sizes=pairs.groupby('InvoiceNo').size()
dates=d.groupby('InvoiceNo').InvoiceDate.min().loc[sizes.index]
monthly=dates.dt.to_period('M').value_counts().sort_index()
cuts=[0,1,5,10,20,50,100,np.inf]
names=['1','2–5','6–10','11–20','21–50','51–100','Trên 100']
grouped=pd.cut(sizes,bins=cuts,labels=names).value_counts().reindex(names)
assert len(sizes)==stats['n_baskets']
assert sizes.sum()==stats['basket_item_pairs']
assert monthly.sum()==len(sizes)
assert grouped.sum()==len(sizes)
eda={
 'run_date':'2026-11-05',
 'raw_rows':len(raw),'raw_missing_by_column':{k:int(v) for k,v in raw.isna().sum().items()},
 'uk_rows_before_filter':int(raw.Country.eq('United Kingdom').sum()),
 'n_baskets':len(sizes),'n_products':int(pairs.StockCode.nunique()),
 'basket_size_mean':float(sizes.mean()),'basket_size_median':float(sizes.median()),
 'basket_size_p95':float(sizes.quantile(.95)),'basket_size_max':int(sizes.max()),
 'single_item_baskets':int(sizes.eq(1).sum()),'single_item_share':float(sizes.eq(1).mean()),
 'over100_baskets':int(sizes.gt(100).sum()),'over100_share':float(sizes.gt(100).mean()),
 'presence_density':float(len(pairs)/(len(sizes)*pairs.StockCode.nunique())),
 'monthly':{str(k):int(v) for k,v in monthly.items()},
 'size_groups':{str(k):int(v) for k,v in grouped.items()},
 'peak_month':str(monthly.idxmax()),'peak_month_invoices':int(monthly.max()),
 'partial_month':'2011-12','partial_month_last_date':str(d.InvoiceDate.max().date()),
}
(RESULT_DIR/'eda_stats.json').write_text(json.dumps(eda,ensure_ascii=False,indent=2),encoding='utf-8')
pd.DataFrame({'month':monthly.index.astype(str),'invoices':monthly.values}).to_csv(RESULT_DIR/'eda_monthly.csv',index=False,encoding='utf-8-sig')
pd.DataFrame({'size_group':names,'invoices':grouped.values,'share':grouped.values/len(sizes)}).to_csv(RESULT_DIR/'eda_basket_sizes.csv',index=False,encoding='utf-8-sig')
for f in ['arial.ttf','arialbd.ttf']:fontManager.addfont(str(Path('C:/Windows/Fonts')/f))
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white','svg.fonttype':'none','text.color':'#17283D','axes.labelcolor':'#334155'})
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10.6,6.7),gridspec_kw={'height_ratios':[1,1.12]})
bars=ax1.bar(names,grouped.values,color='#173B5E',width=.64)
ax1.set_title('Số sản phẩm khác nhau trong mỗi hóa đơn',loc='left',fontweight='bold',pad=13)
ax1.set_ylabel('Số hóa đơn');ax1.set_xlabel('Số mã hàng khác nhau')
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:,.0f}'.replace(',','.')))
ax1.set_ylim(0,grouped.max()*1.24);ax1.grid(axis='y',alpha=.13);ax1.set_axisbelow(True)
for b in bars:
 ax1.text(b.get_x()+b.get_width()/2,b.get_height()+grouped.max()*.025,f'{int(b.get_height()):,}'.replace(',','.'),ha='center',fontsize=9)
colors=['#173B5E']*len(monthly);colors[-1]='#D87533'
bars=ax2.bar(range(len(monthly)),monthly.values,color=colors,width=.65)
ax2.set_title('Số hóa đơn hợp lệ theo tháng',loc='left',fontweight='bold',pad=13)
ax2.set_xticks(range(len(monthly)),[f'{p.month:02}/{str(p.year)[2:]}' for p in monthly.index],rotation=35,ha='right')
ax2.set_ylabel('Số hóa đơn');ax2.set_xlabel('Tháng / năm')
ax2.set_ylim(0,monthly.max()*1.24);ax2.grid(axis='y',alpha=.13);ax2.set_axisbelow(True)
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:,.0f}'.replace(',','.')))
for b in bars:ax2.text(b.get_x()+b.get_width()/2,b.get_height()+monthly.max()*.02,f'{int(b.get_height()):,}'.replace(',','.'),ha='center',fontsize=8.5)
fig.tight_layout(h_pad=2.8)
for ext in ['png','svg']:fig.savefig(FIG_DIR/f'06_eda_gio_hang_va_thoi_gian.{ext}',dpi=240,bbox_inches='tight',pad_inches=.16)
plt.close(fig)
print(json.dumps(eda,ensure_ascii=False,indent=2))
