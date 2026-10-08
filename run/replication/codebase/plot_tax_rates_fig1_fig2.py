#!/usr/bin/env python3
"""Step 7: Figures 1 & 2 - effective marginal tax rates and participation tax rates
by earnings decile for the 15 countries, from the 'Tax-Benefit Data_1998' sheet
('Without Consumption Taxes' columns). Three stacked panels:
  (a) Nordic: DK, FI, SW
  (b) Continental: AT, BE, FR, GE, LU, NL
  (c) Anglo-Saxon & Southern: GR, IR, IT, PT, SP, UK
Also dumps tax_rates_by_decile.csv (150 country-decile rows)."""
import argparse, csv, os
import numpy as np, xlrd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Full name in sheet -> two-letter code.
NAME2CC = {'Austria': 'AT', 'Belgium': 'BE', 'Denmark': 'DK', 'Finland': 'FI',
           'France': 'FR', 'Germany': 'GE', 'Greece': 'GR', 'Ireland': 'IR',
           'Italy': 'IT', 'Luxembourg': 'LU', 'Netherlands': 'NL', 'Portugal': 'PT',
           'Spain': 'SP', 'Sweden': 'SW', 'United Kingdom': 'UK'}

PANELS = [('(a) Nordic', ['DK', 'FI', 'SW']),
          ('(b) Continental', ['AT', 'BE', 'FR', 'GE', 'LU', 'NL']),
          ('(c) Anglo-Saxon & Southern', ['GR', 'IR', 'IT', 'PT', 'SP', 'UK'])]


def read_tax_benefit(wb):
    """Return {cc: {'mtr': [10], 'ptr': [10]}} reading Without-Consumption-Tax columns."""
    s = wb.sheet_by_name('Tax-Benefit Data_1998')
    out = {}
    for r in range(s.nrows):
        v = s.cell_value(r, 1)
        if isinstance(v, str) and v.strip() in NAME2CC:
            cc = NAME2CC[v.strip()]
            mtr, ptr = [], []
            # decile rows begin a few rows below the header; collect the 10 rows whose col1 is 1..10
            rr = r + 1
            while rr < s.nrows and len(mtr) < 10:
                c1 = s.cell_value(rr, 1)
                if isinstance(c1, float) and 1 <= c1 <= 10 and abs(c1 - round(c1)) < 1e-9:
                    mtr.append(s.cell_value(rr, 3))   # Marginal Tax (Without Consumption Taxes)
                    ptr.append(s.cell_value(rr, 4))   # Participation Tax (Without Consumption Taxes)
                rr += 1
            assert len(mtr) == 10, f"{cc}: expected 10 deciles, got {len(mtr)}"
            out[cc] = {'mtr': np.array(mtr), 'ptr': np.array(ptr)}
    return out


def make_figure(data, key, ylabel, title, path):
    fig, axes = plt.subplots(3, 1, figsize=(7, 11), sharex=True)
    deciles = np.arange(1, 11)
    for ax, (ptitle, ccs) in zip(axes, PANELS):
        for cc in ccs:
            ax.plot(deciles, data[cc][key], marker='o', ms=4, label=cc)
        ax.set_title(ptitle, fontsize=11, loc='left')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend(ncol=3, fontsize=8, loc='best')
    axes[-1].set_xlabel('Earnings decile')
    axes[-1].set_xticks(deciles)
    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(path)
    plt.close(fig)
    print(f"Wrote {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--outdir', default='figures')
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    wb = xlrd.open_workbook(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EUROMOD.xls'))
    data = read_tax_benefit(wb)

    make_figure(data, 'mtr', 'Marginal tax rate (%)',
                'Figure 1. Effective Marginal Tax Rates',
                os.path.join(args.outdir, 'figure1_marginal_tax_rates.pdf'))
    make_figure(data, 'ptr', 'Participation tax rate (%)',
                'Figure 2. Participation Tax Rates',
                os.path.join(args.outdir, 'figure2_participation_tax_rates.pdf'))

    csv_path = os.path.join(args.outdir, 'tax_rates_by_decile.csv')
    order = [cc for _, ccs in PANELS for cc in ccs]
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['country', 'decile', 'marginal_tax_rate', 'participation_tax_rate'])
        for cc in order:
            for d in range(10):
                w.writerow([cc, d + 1, data[cc]['mtr'][d], data[cc]['ptr'][d]])
    print(f"Wrote {csv_path} ({len(order)*10} rows)")


if __name__ == '__main__':
    main()
