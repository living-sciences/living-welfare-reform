"""EUROMOD hypothetical-household engine for the living-update follow-up.

Builds the paper's 10 demographic groups x earnings deciles x 5-point grid, in
EUROMOD hhot input format, and computes per-cell effective marginal tax rate tau,
participation tax rates a_noUB and a_UB (paper definitions, labour-cost basis),
using one Model per country reused across years.

Rate definitions (paper, ratio-of-sums over the 5-point grid; §3.3):
  tau     = 1 - sum_k d(dispy)/sum_k d(earns+sicer)            [d = (+3% run) - base]
  a_noUB  = 1 - sum_k (dispy_base - dispy_zeroNoUB)/sum_k (earns+sicer)_base
  a_UB    = 1 - sum_k (dispy_base - dispy_zeroUB)/sum_k (earns+sicer)_base

a_UB route: direct construction (ref person unemployed full period with prior
earnings + contribution history; identical to the HHoT_un switch). Only the
reference person is made unemployed; a working spouse keeps earnings.
"""
import os, io, contextlib
import numpy as np, pandas as pd
import fixed_inputs as fi

GRID = [0.8, 0.9, 1.0, 1.1, 1.2]

# group -> (ref_sex, children, married, spouse_working)   sex 1=M 2=F
# group 1 handled specially (evaluated M and F, averaged)
GROUPS = {
    1:  (None, False, False, None),
    2:  (2,    True,  False, None),
    3:  (1,    False, True,  True),
    4:  (1,    False, True,  False),
    5:  (1,    True,  True,  True),
    6:  (1,    True,  True,  False),
    7:  (2,    False, True,  True),
    8:  (2,    False, True,  False),
    9:  (2,    True,  True,  True),
    10: (2,    True,  True,  False),
}
# spouse relative-earnings source group for working-spouse groups (§3.1)
SPOUSE_SRC = {3: 7, 5: 9, 7: 3, 9: 5}

EARNVAR = {'FR': 'yem00'}  # default 'yem'; probe-overridable


@contextlib.contextmanager
def _suppress():
    n = os.open(os.devnull, os.O_WRONLY); o = os.dup(1); e = os.dup(2)
    os.dup2(n, 1); os.dup2(n, 2)
    try:
        yield
    finally:
        os.dup2(o, 1); os.dup2(e, 2); os.close(n); os.close(o); os.close(e)


def rbar(cells, g):
    """group-level mean relative earnings r̄_g = sum_d s / sum_d e."""
    s = cells['s'][g-1]; e = cells['e'][g-1]
    se = e.sum()
    return (s.sum() / se) if se > 0 else 0.0


def hours(y, aw):
    if y <= 0:
        return 0
    return int(round(min(max(40.0 * y / (0.5 * aw), 8.0), 40.0)))


class CY:
    """One country-year run context."""
    def __init__(self, CC, root, model=None):
        self.CC = CC; self.root = root
        from euromod import Model
        self.m = model or Model(root)
        self.c = self.m.countries[CC]
        self.cols = list(pd.read_csv(f'{root}/Input/{CC}_training_data.txt',
                                     sep='\t', nrows=2).columns)
        self.earnvar = EARNVAR.get(CC, 'yem')
        self.earnvar_probe = None  # (var, ils_earns_out) logged by probe_earnvar

    def probe_earnvar(self, year):
        """Pick the earnings input variable whose value flows to ils_earns.
        Tries the configured default then yem, yem00, yemre; picks the best match."""
        import numpy as _np
        cands = [self.earnvar] + [v for v in ['yem', 'yem00', 'yemre'] if v != self.earnvar]
        best = None
        for var in cands:
            if var not in self.cols:
                continue
            r = {c: 0 for c in self.cols}
            r.update(idhh=1, idperson=101, dag=40, dgn=1, dwt=1, dms=1, dcz=1, deh=3,
                     les=3, lhw=40, liwmy=12, yemmy=12, liwwh=240)
            r[var] = 1000.0
            df = pd.DataFrame([r])
            try:
                o = self.run_df(year, df)
                ie = float(o['ils_earns'].sum())
            except Exception:
                ie = 0.0
            if best is None or abs(ie - 1000.0) < abs(best[1] - 1000.0):
                best = (var, ie)
            if abs(ie - 1000.0) < 1.0:
                break
        if best:
            self.earnvar = best[0]
            self.earnvar_probe = best
        return best

    # -------- person construction --------
    def _person(self, idhh, idp, age, sex, yem=0.0, state='emp', partner=0,
                mother=0, father=0, lhw=0, prev=0.0):
        """state in {emp, inactive, unemp}."""
        r = {c: 0 for c in self.cols}
        adult = age >= 18
        if not adult:
            les = 2
        elif state == 'emp':
            les = 3
        elif state == 'unemp':
            les = 5
        else:
            les = 4
        emp = (state == 'emp' and yem > 0)
        r.update(idhh=idhh, idperson=idp, idpartner=partner, idmother=mother,
                 idfather=father, dag=age, dgn=sex, dwt=1,
                 dms=2 if partner else 1, dcz=1,
                 deh=3 if adult else 0, dec=0 if adult else 2,
                 les=les, lhw=lhw if emp else 0,
                 liwmy=12 if emp else 0, yemmy=12 if emp else 0,
                 yempv=prev, lunmy=12 if state == 'unemp' else 0,
                 liwwh=240 if (emp or state == 'unemp') else 0,
                 liwwh12_h=12, liwwh24_h=24, liwwhny10_h=120, liwwhny15_h=180,
                 lim_h=1)
        r[self.earnvar] = yem
        if self.earnvar != 'yem':
            r['yem'] = 0
        r['xhcrt'] = 0
        return r

    def _household(self, idhh, g, ref_sex, ref_y, aw, scenario, cells, rent=0.0,
                   one_child=False):
        """Build one scenario household. scenario in {base,plus3,zeroNoUB,zeroUB}."""
        _, children, married, spouse_working = GROUPS[g]
        kids_ages = [6] if one_child else [6, 4]
        h = idhh * 100 + 1
        if scenario == 'base':
            y = ref_y; state = 'emp'; prev = 0.0
        elif scenario == 'plus3':
            y = ref_y * 1.03; state = 'emp'; prev = 0.0
        elif scenario == 'zeroNoUB':
            y = 0.0; state = 'inactive'; prev = 0.0
        else:  # zeroUB
            y = 0.0; state = 'unemp'; prev = ref_y
        lhw = hours(y, aw)
        ppl = []
        if not married:
            ref = self._person(idhh, h, 40, ref_sex, yem=y, state=state, lhw=lhw, prev=prev)
            ppl.append(ref)
            if children:
                for i, a in enumerate(kids_ages):
                    ppl.append(self._person(idhh, h + 10 + i, a, 1 if i == 0 else 2,
                                            mother=h, father=0))
        else:
            sp = idhh * 100 + 2
            ref = self._person(idhh, h, 40, ref_sex, yem=y, state=state, partner=sp,
                               lhw=lhw, prev=prev)
            # spouse
            sp_sex = 2 if ref_sex == 1 else 1
            if spouse_working:
                sp_r = rbar(cells, SPOUSE_SRC[g])
                sp_y = sp_r * aw
                sp_person = self._person(idhh, sp, 38, sp_sex, yem=sp_y, state='emp',
                                         partner=h, lhw=hours(sp_y, aw))
            else:
                sp_person = self._person(idhh, sp, 38, sp_sex, yem=0.0, state='inactive',
                                         partner=h)
            ppl += [ref, sp_person]
            if children:
                for i, a in enumerate(kids_ages):
                    ppl.append(self._person(idhh, idhh * 100 + 3 + i, a,
                                            1 if i == 0 else 2, mother=sp, father=h))
        return ppl

    # -------- full country-year cell build + run --------
    def build_df(self, year, cells, aw, rent=0.0, one_child=False, lhw40=False):
        """Return (df, index) where index maps idhh -> (g, d, k, scenario, refsex)."""
        rows = []; idx = {}; idhh = 1
        r = cells['r']; e = cells['e']
        for g in range(1, 11):
            ref_sexes = [1, 2] if g == 1 else [GROUPS[g][0]]
            for d in range(10):
                for sx in ref_sexes:
                    if not (e[g-1, d] > 0 and np.isfinite(r[g-1, d])):
                        continue
                    for k in GRID:
                        y = r[g-1, d] * aw * k
                        for sc in ['base', 'plus3', 'zeroNoUB', 'zeroUB']:
                            hh = self._household(idhh, g, sx, y, aw, sc, cells,
                                                 rent=rent, one_child=one_child)
                            if lhw40:
                                for p in hh:
                                    if p['les'] == 3 and p[self.earnvar] > 0:
                                        p['lhw'] = 40
                            rows += hh
                            idx[idhh] = (g, d + 1, k, sc, sx)
                            idhh += 1
        return pd.DataFrame(rows), idx

    def run_df(self, year, df):
        sysname = f'{self.CC}_{year}'
        ds = f'{self.CC}_{year}_hhot'
        with _suppress():
            out = self.c.systems[sysname].run(df, ds, verbose=False, nowarnings=True)
        o = out.outputs[0]
        return o

    def cell_rates(self, year, cells, aw, rent=0.0, one_child=False, lhw40=False):
        """Return DataFrame: g,d,tau,a_noUB,a_UB,sicer_ratio + per-sex handling."""
        df, idx = self.build_df(year, cells, aw, rent, one_child, lhw40)
        o = self.run_df(year, df)
        g_sum = o.groupby('idhh')[['ils_dispy', 'ils_earns', 'ils_sicer']].sum()
        # organize by (g,d) -> grid/scenario sums; group 1 pools both sexes
        # (ratio of sums) per spec §3.1.
        from collections import defaultdict
        acc = defaultdict(lambda: dict(dtau=0.0, ltau=0.0, nnoub=0.0, nub=0.0,
                                       dena=0.0, earns=0.0, sicer=0.0,
                                       cells=defaultdict(dict)))
        for idhh, (g, d, k, sc, sx) in idx.items():
            if idhh not in g_sum.index:
                continue
            row = g_sum.loc[idhh]
            lc = row['ils_earns'] + row['ils_sicer']
            key = (g, d, sx)  # keep sex to validate completeness per grid point
            acc[(g, d)]['cells'][(sx, k)][sc] = (row['ils_dispy'], row['ils_earns'],
                                                 row['ils_sicer'], lc)
        recs = []
        for (g, d), A in acc.items():
            dtau = ltau = nnoub = nub = den_noub = den_ub = earns = sicer = 0.0
            nok = 0
            for (sx, k), sc in A['cells'].items():
                if not all(s in sc for s in ['base', 'plus3', 'zeroNoUB', 'zeroUB']):
                    continue
                db, eb, sib, lcb = sc['base']
                dp, ep, sip, lcp = sc['plus3']
                dn, en, sin, lcn = sc['zeroNoUB']
                du, eu, siu, lcu = sc['zeroUB']
                dtau += (dp - db); ltau += (lcp - lcb)
                nnoub += (db - dn); nub += (db - du)
                # denominator = CHANGE in labour cost = reference person's earns+sicer
                # (a working spouse keeps earnings in both scenarios, so it cancels).
                den_noub += (lcb - lcn); den_ub += (lcb - lcu)
                earns += (eb - en); sicer += (sib - sin); nok += 1
            if nok == 0:
                continue
            tau = 1 - dtau / ltau if ltau != 0 else np.nan
            a_noub = 1 - nnoub / den_noub if den_noub != 0 else np.nan
            a_ub = 1 - nub / den_ub if den_ub != 0 else np.nan
            sicer_ratio = sicer / earns if earns != 0 else np.nan
            recs.append(dict(g=g, d=d, tau=tau, a_noUB=a_noub, a_UB=a_ub,
                             sicer_ratio=sicer_ratio))
        return pd.DataFrame(recs)
