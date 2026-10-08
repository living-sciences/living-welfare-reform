"""Core computation for Immervoll, Kleven, Kreiner, Saez (EJ 2007),
"Welfare Reform in European Countries: A Microsimulation Analysis".

Re-implements the closed-form welfare/efficiency/trade-off expressions
eqs (15),(16),(18),(19) on the cached 1998 EUROMOD cell inputs in
EUROMOD.xls. NOT original author code; written for replication 2026-10-05.

Country sheet layout (each a 10 demographic-group x 10 earnings-decile grid,
cols D..M = xlrd cols 3..12):
  row 6  : Participation Rate P (first float in the row)
  rows 12-21 : Wage/earnings shares s_j  (group x decile)   -> block at 12
  rows 30-39 : Employment shares (E_j / E_total)            -> block at 30
  rows 48-57 : Effective marginal tax rate tau_j            -> block at 48
  rows 66-75 : Effective participation tax rate a_j         -> block at 66

Notation mapping (paper -> code):
  tau = marginal tax rate (paper 's_j'),  eps = intensive/hours elasticity (paper 'e')
  a   = participation tax rate,           eta = extensive/participation elasticity (paper 'g')
  sh  = wage/income share s_j,            em  = employment share e_j = E_j/E
  P   = aggregate participation rate E/N
"""
import os
import numpy as np
import xlrd

COUNTRIES = ['AT', 'BE', 'DK', 'FI', 'FR', 'GE', 'GR', 'IR',
             'IT', 'LU', 'NL', 'PT', 'SP', 'SW', 'UK']

# Benchmark participation-elasticity decile profile (average 0.2) and hours elasticity.
ETA_BENCHMARK = np.array([.4, .4, .3, .3, .2, .2, .1, .1, 0., 0.])
EPS_BENCHMARK = 0.1

_HERE = os.path.dirname(os.path.abspath(__file__))
XLS_PATH = os.path.join(_HERE, 'EUROMOD.xls')


def _block(sheet, r0):
    """Read a 10x10 (group x decile) float block starting at row r0, cols 3..12."""
    return np.array([[sheet.cell_value(r, c) or 0.0 for c in range(3, 13)]
                     for r in range(r0, r0 + 10)])


def load_country(cc, workbook=None):
    """Return dict of arrays for country code cc: sh, em, tau, a (10x10), P (scalar)."""
    b = workbook or xlrd.open_workbook(XLS_PATH)
    s = b.sheet_by_name(cc)
    P = next(v for v in s.row_values(6) if isinstance(v, float))
    return dict(cc=cc, P=P,
                sh=_block(s, 12), em=_block(s, 30),
                tau=_block(s, 48), a=_block(s, 66))


def compute(data, eta, eps):
    """Compute efficiency effects and trade-offs for a country.

    Parameters
    ----------
    data : dict from load_country
    eta  : 10x10 array (group x decile) of participation elasticities,
           OR a length-10 decile profile (broadcast across all groups).
    eps  : scalar hours-of-work elasticity (constant across cells).

    Returns dict with:
      Dd, Dw            : efficiency loss fractions (eqs 15, 18)
      eff_demogrant     = -Dd   (paper 'Efficiency' col, negative = loss)
      eff_workingpoor   = -Dw
      tradeoff_demogrant = Psi_d (eq 16)
      tradeoff_workingpoor = Psi_w (eq 19)
      share_pop_gaining_demogrant     = pg  (Table 7 col 1)
      share_emp_gaining_workingpoor   = eg  (Table 7 col 2)
      demogrant_has_gainers, workingpoor_has_gainers : bool denominators > 0
    """
    sh, em, tau, a, P = data['sh'], data['em'], data['tau'], data['a'], data['P']
    eta = np.asarray(eta, dtype=float)
    if eta.ndim == 1:
        eta = np.tile(eta, (10, 1))

    # eq (15): demogrant efficiency loss fraction
    Dd = ((tau / (1 - tau) * eps + a / (1 - a) * eta) * sh).sum()
    # eq (18): working-poor efficiency loss fraction
    denom_w = 1 - (a / (1 - a) * eta * em).sum()
    Dw = 1 - (1 - Dd) / denom_w

    m = em > 0  # cells with employed people
    emp_safe = np.where(m, em, 1.0)

    # Gainers under demogrant: s_j/e_j < (1-Dd)/N  <=> sh/em < (1-Dd)*P
    gd = m & (sh / emp_safe < (1 - Dd) * P)
    pg = em[gd].sum() * P + (1 - P)       # population share gaining (unemployed always gain)
    sg_d = sh[gd].sum()
    den_d = pg * (1 - Dd) - sg_d
    Psi_d = 1 + Dd / den_d if den_d != 0 else float('nan')

    # Gainers under working poor: s_j/e_j < (1-Dw)  <=> sh/em < (1-Dw)
    gw = m & (sh / emp_safe < (1 - Dw))
    eg = em[gw].sum()                     # share of employed gaining
    sg_w = sh[gw].sum()
    den_w = eg * (1 - Dw) - sg_w
    Psi_w = 1 + Dw / den_w if den_w != 0 else float('nan')

    return dict(
        Dd=Dd, Dw=Dw,
        eff_demogrant=-Dd, eff_workingpoor=-Dw,
        tradeoff_demogrant=Psi_d, tradeoff_workingpoor=Psi_w,
        share_pop_gaining_demogrant=pg, share_emp_gaining_workingpoor=eg,
        demogrant_has_gainers=bool(den_d > 0),
        workingpoor_has_gainers=bool(den_w > 0),
    )


def eta_table3_profile(eta_avg):
    """Table 3 profile shape scaled by average level eta_avg:
    2*avg (dec 1-2), 1.5*avg (3-4), avg (5-6), 0.5*avg (7-8), 0 (9-10)."""
    return eta_avg * np.array([2, 2, 1.5, 1.5, 1, 1, .5, .5, 0, 0.])


# Table 6 panel (b): extensive response concentrated on married women / lone parents.
# Groups are 1-indexed in the sheet; female groups = 2,4,6,8,10 (0-indexed 1,3,5,7,9).
ETA_FEMALE_HETERO = np.array([.9, .9, .6, .6, .4, .4, .2, .2, 0., 0.])
FEMALE_GROUPS_0IDX = [1, 3, 5, 7, 9]


def eta_table6_hetero():
    """10x10 (group x decile) eta: female profile on female groups, 0 elsewhere."""
    eta = np.zeros((10, 10))
    for g in FEMALE_GROUPS_0IDX:
        eta[g, :] = ETA_FEMALE_HETERO
    return eta
