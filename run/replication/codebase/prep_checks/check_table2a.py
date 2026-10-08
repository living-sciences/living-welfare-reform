# Phase-0 prep sanity check (NOT original author code). Re-implements eqs (15),(16),(18),(19) on the
# cached 1998 EUROMOD cell inputs in ../EUROMOD.xls; reproduces Table 2(a) and Table 7 cols (1)-(2) for all 15 countries.
# Run: python check_table2a.py  (needs xlrd, numpy). Written 2026-10-05.
import xlrd, numpy as np
b=xlrd.open_workbook(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','EUROMOD.xls'))
eta_d=np.array([.4,.4,.3,.3,.2,.2,.1,.1,0,0]); eps=0.1
def blk(s,r0): return np.array([[s.cell_value(r,c) or 0.0 for c in range(3,13)] for r in range(r0,r0+10)])
for cc in ['AT','BE','DK','FI','FR','GE','GR','IR','IT','LU','NL','PT','SP','SW','UK']:
    s=b.sheet_by_name(cc); P=next(v for v in s.row_values(6) if isinstance(v,float))
    sh=blk(s,12); em=blk(s,30); tau=blk(s,48); a=blk(s,66)
    eta=np.tile(eta_d,(10,1))
    Dd=((tau/(1-tau)*eps + a/(1-a)*eta)*sh).sum()
    Dw=1-(1-Dd)/(1-(a/(1-a)*eta*em).sum())
    m=em>0
    gd=m&(sh/np.where(m,em,1)<(1-Dd)*P); pg=(em[gd].sum()*P+(1-P)); sg=sh[gd].sum()
    Pd=1+Dd/(pg*(1-Dd)-sg)
    gw=m&(sh/np.where(m,em,1)<(1-Dw)); eg=em[gw].sum(); sgw=sh[gw].sum()
    Pw=1+Dw/(eg*(1-Dw)-sgw)
    print(cc, round(-Dd,2), round(Pd,2), round(-Dw,2), round(Pw,2), 'shares', round(pg,2), round(eg,2))
