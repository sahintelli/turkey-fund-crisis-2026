# Step 7: builds figures V4, V6, V7, V8, V9, V10, V11, V12 in EN and ZH. Data: ../../data/*.csv (TEFAS exports, investing.com prices). Author: Dr. Telli channel.
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib import font_manager as fm
import sys, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=str(ROOT/'data/interim')+'/'; O=str(ROOT/'figures')+'/'
P1,P2,P3,N1,N2,N3='#534AB7','#26215C','#AFA9EC','#F1EFE8','#888780','#2C2C2A'; ACC='#D85A30'
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
cjk=['Noto Sans CJK JP']  # same .ttc; contains Simplified Chinese glyphs
T={ # bilingual labels
'src':{'en':'Source: TEFAS daily data; author\'s calculations · Dr. Telli','zh':'数据来源：TEFAS每日数据；作者计算 · Dr. Telli'},
'src_px':{'en':'Source: exchange price/volume data; author\'s calculations · Dr. Telli','zh':'数据来源：交易所价格/成交量数据；作者计算 · Dr. Telli'},
'v4t':{'en':'TLY grew 8x in 2026 — mostly from valuation, not new money','zh':'TLY基金2026年规模增长8倍——主要来自估值上涨，而非新资金'},
'v4a':{'en':'Cumulative net inflows','zh':'累计净流入'},'v4b':{'en':'Cumulative valuation change','zh':'累计估值变动'},'v4c':{'en':'Change in fund size since 2 Jan','zh':'自1月2日以来基金规模变化'},
'bnTL':{'en':'billion TL','zh':'十亿里拉'},
'v6t':{'en':'OZATD: block at 212 TL → funds bought at 741–879 TL two weeks later','zh':'OZATD：大宗交易价212里拉 → 两周后基金以741–879里拉买入'},
'v6a':{'en':'27 Apr: 4.3m shares\nsold to TLY','zh':'4月27日：430万股\n出售给TLY'},'v6b':{'en':'30 Apr: 15.6m-share block\n@212 TL (close 373)','zh':'4月30日：1560万股大宗\n@212里拉（收盘373）'},
'v6c':{'en':'14 May: funds buy\n13.04m shares on exchange','zh':'5月14日：基金在交易所\n买入1304万股'},'px':{'en':'Price (TL)','zh':'价格（里拉）'},'vol':{'en':'Volume (m shares)','zh':'成交量（百万股）'},
'v7t':{'en':'Same ~13 million shares, two weeks apart','zh':'同样约1300万股，相隔两周'},'v7a':{'en':'Block trade\n30 Apr @212','zh':'大宗交易\n4月30日 @212'},'v7b':{'en':'Funds\' purchase\n14 May @741–879','zh':'基金买入\n5月14日 @741–879'},
'v8t':{'en':'TPKGY: exchange price vs. manager\'s NAV per unit (≈85x)','zh':'TPKGY：交易所价格 vs 管理人公布的单位净值（约85倍）'},'v8a':{'en':'Exchange price\n24 Jul','zh':'交易所价格\n7月24日'},'v8b':{'en':'Manager\'s NAV\n30 Jun','zh':'管理人净值\n6月30日'},'tl':{'en':'TL per unit (log scale)','zh':'每单位里拉（对数坐标）'},
'v9t':{'en':'TLY exits real-estate fund units days before the 31 July valuation rule','zh':'TLY在7月31日估值新规生效前几天清空房地产基金份额'},'pct':{'en':'% of portfolio','zh':'占投资组合%'},
'v9a':{'en':'Real-estate fund units','zh':'房地产基金份额'},'v9b':{'en':'Equities','zh':'股票'},'v9c':{'en':'Rule effective\nafter 31 Jul','zh':'新规\n7月31日后生效'},
'v10t':{'en':'85.5 bn TL left TLY while its price rose 19.7% (17 Aug–16 Sep)','zh':'8月17日至9月16日：TLY净流出855亿里拉，同期价格上涨19.7%'},'v10a':{'en':'Daily net flow (bn TL)','zh':'每日净流量（十亿里拉）'},'v10b':{'en':'Unit price (TL)','zh':'单位价格（里拉）'},
'v11t':{'en':'Fund price follows YESTERDAY\'s stock moves','zh':'基金价格跟随的是"前一天"的股价变动'},'v11a':{'en':'Same day: corr −0.16','zh':'同日：相关系数 −0.16'},'v11b':{'en':'Previous day: corr 0.75','zh':'前一日：相关系数 0.75'},
'v11x':{'en':'Weighted return of top-6 holdings (%)','zh':'前六大持仓加权收益率（%）'},'v11y':{'en':'TLY daily return (%)','zh':'TLY日收益率（%）'},
'v12t':{'en':'Money market funds: liquid assets gone after closure','zh':'货币市场基金：关闭后流动资产已耗尽'},
'liq':{'en':'Liquid (repo, BIST money mkt, deposits, govt)','zh':'流动资产（回购、交易所货币市场、存款、国债）'},'cp':{'en':'Commercial paper','zh':'商业票据'},'ls':{'en':'Private lease certificates','zh':'私营租赁凭证'},'oth':{'en':'Other','zh':'其他'},
'before':{'en':'1 Sep','zh':'9月1日'},'after':{'en':'18 Sep','zh':'9月18日'},
}
def style(ax):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    for s in ['left','bottom']: ax.spines[s].set_color(N2)
    ax.tick_params(colors=N3,labelsize=9); ax.set_facecolor('white')
def fig(): 
    f,ax=plt.subplots(figsize=(10,5.6),dpi=150); f.patch.set_facecolor('white'); style(ax); return f,ax
def finish(f,ax,title,src,name,lang):
    ax.set_title(title,loc='left',fontsize=13,color=P2,fontweight='bold',pad=12)
    f.text(0.01,0.01,src,fontsize=7.5,color=N2)
    f.tight_layout(rect=(0,0.03,1,1))
    for ext in ['png','svg']: f.savefig(f'{O}{name}_{lang}.{ext}',facecolor='white')
    plt.close(f)
g=pd.read_csv(D+'tly_general.csv',parse_dates=['Tarih']).sort_values('Tarih'); g=g[g.Fiyat>0].reset_index(drop=True)
g['flow']=g['Tedavüldeki Pay Sayısı'].diff().fillna(0)*g.Fiyat/1e9; g['size']=g['Fon Toplam Değer']/1e9
g['val']=g['size'].diff().fillna(0)-g['flow']
P=pd.read_csv(D+'prices.csv',index_col=0,parse_dates=True); V=pd.read_csv(D+'volumes.csv',index_col=0,parse_dates=True)
A=pd.read_csv(D+'tly_allocation.csv',parse_dates=['Tarih'],index_col='Tarih'); A=A[~A.index.duplicated()]
for L in ['en','zh']:
    plt.rcParams['font.family']=(cjk[:1]+['DejaVu Sans']) if L=='zh' else ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus']=False
    t=lambda k:T[k][L]
    # V4
    f,ax=fig(); s0=g['size'].iloc[0]
    ax.fill_between(g.Tarih,0,g.flow.cumsum(),color=P3,label=t('v4a'))
    ax.fill_between(g.Tarih,g.flow.cumsum(),g.flow.cumsum()+g.val.cumsum(),color=P1,alpha=.85,label=t('v4b'))
    ax.plot(g.Tarih,g['size']-s0,color=P2,lw=1.2,label=t('v4c'))
    ax.set_ylabel(t('bnTL'),color=N3); ax.legend(frameon=False,fontsize=9,loc='upper left'); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b' if L=='en' else '%-m月'))
    finish(f,ax,t('v4t'),t('src'),'V4_tly_growth_decomposition',L)
    # V6
    o=P.OZATD.loc['2026-04-20':'2026-05-20']; ov=V.OZATD.loc['2026-04-20':'2026-05-20']/1e6
    f,ax=fig(); ax2=ax.twinx(); ax2.bar(ov.index,ov,color=P3,width=.7,alpha=.7); ax2.set_ylabel(t('vol'),color=N2); style(ax2); ax2.spines['right'].set_visible(True)
    ax.set_zorder(ax2.get_zorder()+1); ax.patch.set_visible(False)
    ax.plot(o.index,o,color=P1,lw=2.2,marker='o',ms=3); ax.set_ylabel(t('px'),color=N3)
    for d,k,y in [('2026-04-27','v6a',280.75),('2026-04-30','v6b',373.25),('2026-05-14','v6c',878.5)]:
        ax.annotate(t(k),(pd.Timestamp(d),y),xytext=(0,40),textcoords='offset points',ha='center',fontsize=8,color=P2,arrowprops=dict(arrowstyle='-',color=N2))
    ax.axhline(212,color=ACC,ls='--',lw=1); ax.text(o.index[0],222,'212 TL',color=ACC,fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b' if L=='en' else '%m/%d')); finish(f,ax,t('v6t'),t('src_px'),'V6_ozatd_chain',L)
    # V7
    f,ax=fig(); vals=[13e6*212/1e9,13.036219e6*741.5/1e9,13.036219e6*878.5/1e9]
    ax.bar([0],[vals[0]],color=P3,width=.5); ax.bar([1],[vals[2]],color=P1,width=.5,alpha=.35); ax.bar([1],[vals[1]],color=P1,width=.5)
    ax.set_xticks([0,1]); ax.set_xticklabels([t('v7a'),t('v7b')]); ax.set_ylabel(t('bnTL'),color=N3)
    ax.text(0,vals[0]+.2,f'{vals[0]:.2f}',ha='center',color=P2,fontweight='bold'); ax.text(1,vals[2]+.2,f'{vals[1]:.2f}–{vals[2]:.2f}',ha='center',color=P2,fontweight='bold')
    finish(f,ax,t('v7t'),t('src_px'),'V7_ozatd_block_vs_fund',L)
    # V8
    f,ax=fig(); ax.bar([0,1],[690000,8122.13],color=[P1,P3],width=.5); ax.set_yscale('log'); ax.set_xticks([0,1]); ax.set_xticklabels([t('v8a'),t('v8b')]); ax.set_ylabel(t('tl'),color=N3)
    for i,v in enumerate([690000,8122.13]): ax.text(i,v*1.15,f'{v:,.0f}',ha='center',color=P2,fontweight='bold')
    finish(f,ax,t('v8t'),t('src_px'),'V8_tpkgy_price_vs_nav',L)
    # V9
    a=A.loc['2026-07-16':'2026-08-05']; f,ax=fig()
    ax.plot(a.index,a['Gayrimenkul Yatırım Fonları Katılma Payları (%)'].fillna(0),color=ACC,lw=2.4,marker='o',ms=4,label=t('v9a'))
    ax.plot(a.index,a['Hisse Senedi (%)'],color=P1,lw=2,label=t('v9b')); ax.axvline(pd.Timestamp('2026-07-31'),color=N2,ls='--'); ax.text(pd.Timestamp('2026-07-31'),45,t('v9c'),fontsize=8,color=N3,ha='right')
    ax.set_ylabel(t('pct'),color=N3); ax.legend(frameon=False,fontsize=9); ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b' if L=='en' else '%m/%d'))
    finish(f,ax,t('v9t'),t('src'),'V9_tly_gyf_exit',L)
    # V10
    w=g[(g.Tarih>'2026-08-14')&(g.Tarih<='2026-09-16')]; f,ax=fig(); ax2=ax.twinx(); style(ax2); ax2.spines['right'].set_visible(True)
    ax.bar(w.Tarih,w.flow,color=np.where(w.flow<0,ACC,P3),width=.8); ax.set_ylabel(t('v10a'),color=N3)
    ax2.plot(w.Tarih,w.Fiyat,color=P1,lw=2.2); ax2.set_ylabel(t('v10b'),color=P1); ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b' if L=='en' else '%m/%d'))
    finish(f,ax,t('v10t'),t('src'),'V10_tly_run',L)
    # V11
    W={'2026-07':dict(DSTKF=22.8,OZATD=14.3,TEHOL=7.1,TRHOL=5.6,PEKGY=7.7,ANELE=2.0),'2026-08':dict(DSTKF=12.0,OZATD=34.3,TEHOL=9.2,TRHOL=4.0,PEKGY=8.8,ANELE=2.2),'2026-09':dict(DSTKF=21.1,OZATD=19.4,TEHOL=10.6,TRHOL=6.7,PEKGY=8.9,ANELE=3.0)}
    R=P.drop(columns='TPKGY').pct_change(); gi=g.set_index('Tarih'); tr=gi.Fiyat.pct_change()
    xs0,xs1,ys=[],[],[]
    for d in tr.loc['2026-07-02':'2026-09-16'].index:
        if d not in R.index: continue
        i=R.index.get_loc(d); w_=W[d.strftime('%Y-%m')]
        xs0.append(100*sum(w_[s]/100*R.iloc[i][s] for s in w_)); xs1.append(100*sum(w_[s]/100*R.iloc[i-1][s] for s in w_)); ys.append(100*tr[d])
    f,axs=plt.subplots(1,2,figsize=(10,5),dpi=150,sharey=True); f.patch.set_facecolor('white')
    for ax,x,k,c in [(axs[0],xs0,'v11a',N2),(axs[1],xs1,'v11b',P1)]:
        style(ax); ax.scatter(x,ys,color=c,s=18,alpha=.8); ax.set_title(t(k),fontsize=10,color=P2); ax.set_xlabel(t('v11x'),fontsize=8,color=N3); ax.axhline(0,color=N1); ax.axvline(0,color=N1)
    axs[0].set_ylabel(t('v11y'),color=N3); f.suptitle(t('v11t'),x=.01,ha='left',fontsize=13,color=P2,fontweight='bold'); f.text(.01,.01,t('src')+' · Jul–Sep 2026',fontsize=7.5,color=N2)
    f.tight_layout(rect=(0,.03,1,.95)); [f.savefig(f'{O}V11_stale_pricing_{L}.{e}',facecolor='white') for e in ['png','svg']]; plt.close(f)
    # V12
    def grp(code,day):
        a=pd.read_csv(D+f'{code}_allocation.csv',parse_dates=['Tarih'],index_col='Tarih').fillna(0); r=a.loc[a.index[a.index.get_indexer([pd.Timestamp(day)],method='nearest')[0]]]
        cp=r.filter(like='Finansman Bonosu').sum(); ls=r.filter(like='Özel Sektör Kira').sum()
        liq=sum(r.filter(like=k).sum() for k in ['Ters-Repo','Takasbank Para','BIST Para','Borsa Para','Borsa İstanbul Para','Mevduat','Katılma Hesabı','Devlet Tahvili','Hazine Bonosu','Kamu'])
        return [liq,cp,ls,max(0,100-liq-cp-ls)]
    f,ax=fig(); labels=[]; bars=[]
    for code in ['pry','pse']:
        for day,k in [('2026-09-01','before'),('2026-09-18','after')]: bars.append(grp(code,day)); labels.append(f'{code.upper()}\n{t(k)}')
    bars=np.array(bars); left=np.zeros(len(bars))
    for j,(k,c) in enumerate([('liq',P3),('cp',P1),('ls',P2),('oth',N2)]):
        ax.barh(labels,bars[:,j],left=left,color=c,label=t(k)); left+=bars[:,j]
    ax.invert_yaxis(); ax.set_xlabel(t('pct'),color=N3); ax.legend(frameon=False,fontsize=8,ncol=2,loc='lower center',bbox_to_anchor=(.5,-.32))
    finish(f,ax,t('v12t'),t('src'),'V12_mmf_before_after',L)
print('done')
