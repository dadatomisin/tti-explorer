import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import gamma
from itertools import product, starmap
from collections import namedtuple

def bool_bernoulli(p, rng):
    return bool(rng.binomial(1, p))


def categorical(pvals, rng, n=1):
    outputs = np.argmax(rng.multinomial(1, pvals, size=n), axis=-1)
    return outputs.item() if n == 1 else outputs
# BE, weird to have different output types but also weird to return
# a 1 item array


def he_infection_profile(period, gamma_params):
    inf_days = np.arange(period)
    mass = gamma.cdf(inf_days + 1, **gamma_params) - gamma.cdf(inf_days, **gamma_params)
    return mass / np.sum(mass)

def home_daily_infectivity(base_mass):
    fail_prod = np.cumprod(1 - base_mass)
    fail_prod = np.roll(fail_prod, 1)
    np.put(fail_prod, 0, 1.)
    skewed_mass = fail_prod * base_mass
    return skewed_mass / np.sum(skewed_mass)


def named_product(**items):
    Product = namedtuple('Product', items.keys())
    return starmap(Product, product(*items.values()))


class Registry:
    "Case insensitive registry"
    def __init__(self):
        self._register = dict()

    def __getitem__(self, key):
        return self._register[key.lower()]

    def __call__(self, name):
        def add(thing):
            self._register[name.lower()] = thing
            return thing
        return add

class PdfDeck:
    def __init__(self, figs=None):
        self.figs = figs or []

    @classmethod
    def save_as_pdf(cls, figs, fpath):
        return cls(figs).make(fpath)

    def add_figure(self, fig, position=None):
        if position is None:
            self.figs.append(fig)
        else:
            self.figs.insert(position, fig)

    def make(self, fpath):
        with PdfPages(fpath) as pdf:
            for fig in self.figs:
                pdf.savefig(fig)


def swaplevel(dct_of_dct):
    keys = next(iter(dct_of_dct.values())).keys()
    return {in_k: {out_k: v[in_k] for out_k, v in dct_of_dct.items()} for in_k in keys}


