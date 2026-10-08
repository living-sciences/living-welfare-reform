"""Fixed (1998) inputs and policy-year scalars for the living-update follow-up.

- 1998 cell structure (s_j, e_j, P, r_j=s/e) read from EUROMOD.xls via welfare_core.
- AW_t (average wage, monthly, national currency) from Eurostat earn_nt_net JSON-stat.
- CTR_t = CTR_1998_xls + (F_t - F_1998), F = Mendoza consumption-tax ratio.
- q (Table A3 col 2, 1998 UB-receipt weights) and CTR_1998 workbook values: paper
  table constants given explicitly in the spec (allowed; not tax parameters).

Country codes
  workbook (paper) : AT BE DK FI FR GE GR IR IT LU NL PT SP SW   (UK excluded here)
  EUROMOD/Eurostat : AT BE DK FI FR DE EL IE IT LU NL PT ES SE
"""
import json, os
import numpy as np
import welfare_core as wc

SHARED = os.environ.get('SHARED',
    '/workspace/eval/followup_staging/shared-data')

# workbook code -> EUROMOD/Eurostat code
WB2EM = {'AT':'AT','BE':'BE','DK':'DK','FI':'FI','FR':'FR','GE':'DE','GR':'EL',
         'IR':'IE','IT':'IT','LU':'LU','NL':'NL','PT':'PT','SP':'ES','SW':'SE'}
EM2WB = {v:k for k,v in WB2EM.items()}
# 14 in-scope countries, workbook order
WB_COUNTRIES = ['AT','BE','DK','FI','FR','GE','GR','IR','IT','LU','NL','PT','SP','SW']
EM_COUNTRIES = [WB2EM[c] for c in WB_COUNTRIES]

# q = Table A3 col 2 (1998), keyed by EUROMOD code, in percent
Q_TABLE_A3 = {'AT':9.0,'BE':21.1,'DK':21.4,'FI':28.1,'FR':31.4,'DE':13.8,'EL':9.7,
              'IE':8.8,'IT':7.3,'LU':4.3,'NL':12.7,'PT':14.1,'ES':23.1,'SE':19.0}
# CTR_1998 workbook consumption-tax rate (percent), keyed by EUROMOD code
CTR_1998_XLS = {'AT':20.12,'BE':17.35,'DK':35.96,'FI':29.90,'FR':19.90,'DE':15.61,
                'EL':16.31,'IE':26.12,'IT':15.42,'LU':23.74,'NL':19.39,'PT':22.70,
                'ES':14.66,'SE':20.53}


# ---------------------------------------------------------------- JSON-stat ---
def load_jsonstat(path):
    """Return (values dict keyed by tuple of dim-category-ids, dim order list,
    dict dim->list of category ids in index order)."""
    d = json.load(open(path))
    dims = d['id']; size = d['size']
    cats = {}
    for dim in dims:
        idx = d['dimension'][dim]['category']['index']
        # idx maps id->position; invert to position-ordered list
        ordered = [None]*len(idx)
        for cid, pos in idx.items():
            ordered[pos] = cid
        cats[dim] = ordered
    val = d['value']  # dict str(flatindex)->number  OR list
    # build strides
    strides = [1]*len(size)
    for i in range(len(size)-2, -1, -1):
        strides[i] = strides[i+1]*size[i+1]
    out = {}
    if isinstance(val, dict):
        items = val.items()
    else:
        items = enumerate(val)
    for k, v in items:
        if v is None:
            continue
        fi = int(k)
        key = []
        for i, dim in enumerate(dims):
            pos = (fi // strides[i]) % size[i]
            key.append(cats[dim][pos])
        out[tuple(key)] = v
    return out, dims, cats


# ------------------------------------------------------------- 1998 cells ---
_WB = None
def cells_1998(cc_wb):
    """Return dict with s,e (10x10 group x decile), P, r (=s/e, nan where e=0)."""
    global _WB
    if _WB is None:
        import xlrd
        _WB = xlrd.open_workbook(wc.XLS_PATH)
    d = wc.load_country(cc_wb, _WB)
    s, e = d['sh'], d['em']
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(e > 0, s/e, np.nan)
    return dict(cc_wb=cc_wb, cc_em=WB2EM[cc_wb], s=s, e=e, P=d['P'], r=r)


# --------------------------------------------------------------- AW_t ---
_AW = None
def _aw_table():
    global _AW
    if _AW is None:
        vals, dims, cats = load_jsonstat(f'{SHARED}/earnings/earn_nt_net_AW100_GRS_NAC.json')
        # key dims: freq,currency,estruct,ecase,geo,time
        _AW = {}
        for k, v in vals.items():
            d = dict(zip(dims, k))
            _AW[(d['geo'], d['time'])] = v  # annual
    return _AW

def aw_month(cc_em, year):
    """Monthly average wage (national currency) for year t (int). 2026 handled by caller.

    Data-units fix: in the staged earn_nt_net file the 2024 observation is stored
    already on a MONTHLY basis for every country (it equals ~1/12 of the annual
    trend and sits exactly between 2023 and 2025 monthly values), whereas all other
    years are annual. Verified across all 14 geos 2026-10-05. So 2024 is returned
    as-is; every other year is annual/12.
    """
    t = _aw_table()
    v = t.get((cc_em, str(year)))
    if v is None:
        return None
    return v if year == 2024 else v / 12.0


# --------------------------------------------------------------- CTR_t ---
def _mendoza_F():
    """F_t = (D211+D214)/(P31_S14 + P3_S13 - D1PAY_S13 - D211 - D214) per geo,year.
    Returns dict (geo,year)->F (fraction, not percent)."""
    d211_214,_,_ = load_jsonstat(f'{SHARED}/ctr/gov_10a_taxag_D211_D214.json')
    nama,_,_ = load_jsonstat(f'{SHARED}/ctr/nama_10_gdp_P31S14_P3S13.json')
    d1pay,_,_ = load_jsonstat(f'{SHARED}/ctr/gov_10a_main_D1PAY.json')
    # Reindex by (geo,time,na_item/tax)
    def reidx(vals, dims):
        out={}
        for k,v in vals.items():
            dd=dict(zip(dims,k)); out[(dd['geo'],dd['time'],dd.get('na_item') or dd.get('tax') )]=v
        return out
    # need dims; reload with dims
    v1,dim1,_=load_jsonstat(f'{SHARED}/ctr/gov_10a_taxag_D211_D214.json')
    v2,dim2,_=load_jsonstat(f'{SHARED}/ctr/nama_10_gdp_P31S14_P3S13.json')
    v3,dim3,_=load_jsonstat(f'{SHARED}/ctr/gov_10a_main_D1PAY.json')
    a=reidx(v1,dim1); b=reidx(v2,dim2); c=reidx(v3,dim3)
    geos=set(k[0] for k in a); years=set(k[1] for k in a)
    F={}
    for g in geos:
        for y in years:
            try:
                D211=a[(g,y,'D211')]; D214=a[(g,y,'D214')]
                P31=b[(g,y,'P31_S14')]; P3=b[(g,y,'P3_S13')]
                D1=c[(g,y,'D1PAY')]
            except KeyError:
                continue
            denom=P31+P3-D1-D211-D214
            if denom:
                F[(g,y)]=(D211+D214)/denom
    return F

_F=None
def ctr_t(cc_em, year):
    """CTR_t in percent = CTR_1998_xls + 100*(F_t - F_1998), carry-forward if year missing.
    Returns (ctr_percent, flag) flag='' or 'ctr_carryforward'."""
    global _F
    if _F is None:
        _F=_mendoza_F()
    f1998=_F.get((cc_em,'1998'))
    flag=''
    yy=year
    fy=_F.get((cc_em,str(yy)))
    if fy is None:
        # carry forward from last available <= year
        avail=sorted(int(y) for (g,y) in _F if g==cc_em and int(y)<=year)
        if avail:
            yy=avail[-1]; fy=_F.get((cc_em,str(yy))); flag='ctr_carryforward'
    if f1998 is None or fy is None:
        return None, 'ctr_missing'
    return CTR_1998_XLS[cc_em] + 100.0*(fy-f1998), flag


if __name__=='__main__':
    print("=== country map ==="); print(WB2EM)
    at=cells_1998('AT')
    print("AT P=",round(at['P'],4)," r decile means (grp-avg where e>0):")
    r=at['r']
    print("  decile r (nanmean over groups):", np.round(np.nanmean(r,axis=0),3))
    for cc in ['AT','FR','DK','SE']:
        em=WB2EM[cc] if cc in WB2EM else cc
    for em in ['AT','DE','EL','SE','ES']:
        print(f"AW_month {em}: 2009={aw_month(em,2009)}, 2025={aw_month(em,2025)}")
        c09=ctr_t(em,2009); c25=ctr_t(em,2025); c26=ctr_t(em,2026)
        print(f"   CTR {em}: 1998xls={CTR_1998_XLS[em]} 2009={c09} 2025={c25} 2026={c26}")
