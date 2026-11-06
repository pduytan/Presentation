from pathlib import Path
import sys,json,textwrap
ROOT=Path(__file__).resolve().parent
PROJECT_ROOT=ROOT.parents[1]
vendor=PROJECT_ROOT/'tmp'/'fpgrowth_vendor'
if vendor.exists():sys.path.insert(0,str(vendor))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties, fontManager

RESULT_DIR=PROJECT_ROOT/'outputs'/'Ungdung1'/'results'
OUT=PROJECT_ROOT/'outputs'/'Ungdung1'/'figures';OUT.mkdir(parents=True,exist_ok=True)
S=json.loads((RESULT_DIR/'stats.json').read_text(encoding='utf-8'))
for f in ['arial.ttf','arialbd.ttf']:
    fontManager.addfont(str(Path('C:/Windows/Fonts')/f))
plt.rcParams.update({'font.family':'Arial','font.size':11,'axes.spines.top':False,
 'axes.spines.right':False,'axes.labelcolor':'#334155','text.color':'#17283D',
 'axes.titleweight':'bold','axes.titlesize':14,'figure.facecolor':'white',
 'savefig.facecolor':'white','svg.fonttype':'none'})
NAVY='#173B5E';TEAL='#0C817F';ORANGE='#D87533';GRAY='#CAD5DE'
def save(fig,name):
    fig.savefig(OUT/f'{name}.png',dpi=240,bbox_inches='tight',pad_inches=.17)
    fig.savefig(OUT/f'{name}.svg',bbox_inches='tight',pad_inches=.17)
    plt.close(fig)

top=pd.read_csv(RESULT_DIR/'product_support.csv').head(8).iloc[::-1]
fig,ax=plt.subplots(figsize=(10.8,4.4))
labs=['\n'.join(textwrap.wrap(x,38)) for x in top.name]
bars=ax.barh(labs,top.support,color=NAVY,height=.62)
ax.set_xlim(0,top.support.max()*1.32)
ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0))
ax.set_xlabel('Tỷ lệ hóa đơn có sản phẩm')
ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True)
for b,c,s in zip(bars,top['count'],top.support):
    label=f'{s:.1%}'.replace('.',',')+'  |  '+f'{c:,}'.replace(',','.')+' HĐ'
    ax.text(s+.002,b.get_y()+b.get_height()/2,label,va='center',fontsize=10)
fig.tight_layout();save(fig,'01_san_pham_pho_bien')

rules=S['report_rules']
x=np.arange(len(rules));w=.34
fig,ax=plt.subplots(figsize=(9.8,4.0))
base=[r['n_b']/S['n_baskets'] for r in rules]
conf=[r['confidence'] for r in rules]
a=ax.bar(x-w/2,base,w,label='Tỷ lệ mua B trên toàn bộ hóa đơn',color=GRAY)
b=ax.bar(x+w/2,conf,w,label='Tỷ lệ mua B trong các hóa đơn có A',color=TEAL)
ax.set_xticks(x,[f'R{i+1}: {r["a"]} → {r["b"]}' for i,r in enumerate(rules)])
ax.set_ylim(0,1.04);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
ax.set_ylabel('Tỷ lệ hóa đơn');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=1,frameon=False)
for group in [a,b]:
    for bar in group:
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.018,f'{bar.get_height():.1%}'.replace('.',','),ha='center',fontsize=11)
fig.tight_layout();save(fig,'02_confidence_va_muc_nen')

v=pd.DataFrame(S['sensitivity'])
v=v.loc[v.minsup.ge(.01)]
fig,ax=plt.subplots(figsize=(9.8,3.8))
ax.plot(v.minsup*100,v.itemsets,'o-',color=NAVY,label='Tập mục thường xuyên',lw=2)
ax.plot(v.minsup*100,v.rules,'s-',color=ORANGE,label='Luật đạt confidence ≥ 60% và lift ≥ 1,5',lw=2)
ax.set_xticks(v.minsup*100);ax.set_xlabel('Minimum support (%)');ax.set_ylabel('Số lượng')
ax.grid(alpha=.15);ax.legend(frameon=False)
for _,r in v.iterrows():
    ax.annotate(f'{int(r.itemsets):,}'.replace(',','.'),(r.minsup*100,r.itemsets),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
fig.tight_layout();save(fig,'03_do_nhay_minsup')

t=S['temporal']['rules'];x=np.arange(len(t))
fig,ax=plt.subplots(figsize=(9.8,3.8))
for shift,key,color,label in [(-w/2,'train_confidence',NAVY,'Trước 01/10/2011'),(w/2,'test_confidence',TEAL,'Từ 01/10 đến 09/12/2011')]:
    bars=ax.bar(x+shift,[r[key] or 0 for r in t],w,color=color,label=label)
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.016,f'{bar.get_height():.1%}'.replace('.',','),ha='center',fontsize=10)
ax.set_xticks(x,[f'T{i+1}: {r["a"]} → {r["b"]}' for i,r in enumerate(t)])
ax.set_ylim(0,1.03);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
ax.set_ylabel('Confidence');ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2)
ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.tight_layout();save(fig,'04_doi_chieu_thoi_gian')

fig,ax=plt.subplots(figsize=(11,2.0));ax.axis('off')
boxes=[('Hóa đơn','Một giỏ hàng / mã hóa đơn'),('FP-Growth','Tập sản phẩm thường xuyên'),('Luật kết hợp','Support · confidence · lift'),('Quyết định','Thử gợi ý mua kèm / combo')]
for i,(title,sub) in enumerate(boxes):
    xx=.015+i*.25
    ax.add_patch(FancyBboxPatch((xx,.27),.22,.57,boxstyle='round,pad=0.012,rounding_size=0.025',transform=ax.transAxes,fc='#F1F5F9',ec='#CAD5DE'))
    ax.text(xx+.11,.62,title,ha='center',va='center',weight='bold',fontsize=13,transform=ax.transAxes)
    ax.text(xx+.11,.43,sub,ha='center',va='center',fontsize=8.5,transform=ax.transAxes)
    if i<3:ax.annotate('',xy=(xx+.247,.55),xytext=(xx+.225,.55),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':TEAL,'lw':2})
save(fig,'05_so_do_ung_dung')

equations={
 'support':r'\mathrm{support}(X)=\frac{n(X)}{N}',
 'confidence':r'\mathrm{confidence}(A\rightarrow B)=\frac{n(A\cup B)}{n(A)}',
 'lift':r'\mathrm{lift}(A\rightarrow B)=\frac{\mathrm{confidence}(A\rightarrow B)}{\mathrm{support}(B)}=\frac{N\,n(A\cup B)}{n(A)\,n(B)}',
}
for name,tex in equations.items():
    fig=plt.figure(figsize=(10,0.7));fig.text(.5,.5,f'${tex}$',ha='center',va='center',fontsize=19)
    save(fig,f'formula_{name}')
print('Figures saved to',OUT)
