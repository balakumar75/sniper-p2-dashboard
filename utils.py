import math
from datetime import date
from math import log, sqrt, exp
from scipy.stats import norm

# ── 8) Black‑Scholes Greeks ────────────────────────────────────────────────

def _bs_d1(S, K, r, sigma, T):
    return (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))

def _bs_d2(d1, sigma, T):
    return d1 - sigma*math.sqrt(T)

def bs_delta(S, K, r, sigma, expiry, is_call=True):
    """
    Returns Δ for a European option.
    expiry: "YYYY-MM-DD"
    """
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    if T <= 0 or sigma<=0: return 0.0
    d1 = _bs_d1(S, K, r, sigma, T)
    return norm.cdf(d1) if is_call else (norm.cdf(d1)-1)

def bs_gamma(S, K, r, sigma, expiry):
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    if T <= 0 or sigma<=0: return 0.0
    d1 = _bs_d1(S, K, r, sigma, T)
    return norm.pdf(d1)/(S*sigma*math.sqrt(T))

def bs_vega(S, K, r, sigma, expiry):
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    if T <= 0 or sigma<=0: return 0.0
    d1 = _bs_d1(S, K, r, sigma, T)
    return S * norm.pdf(d1) * math.sqrt(T) / 100

def bs_theta(S, K, r, sigma, expiry, is_call=True):
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    if T <= 0 or sigma<=0: return 0.0
    d1 = _bs_d1(S, K, r, sigma, T)
    d2 = _bs_d2(d1, sigma, T)
    pdf = norm.pdf(d1)
    term1 = - (S*pdf*sigma)/(2*math.sqrt(T))
    if is_call:
        term2 = r*K*math.exp(-r*T)*norm.cdf(d2)
        return (term1 - term2)/365
    else:
        term2 = r*K*math.exp(-r*T)*norm.cdf(-d2)
        return (term1 + term2)/365

def bs_rho(S, K, r, sigma, expiry, is_call=True):
    T = (date.fromisoformat(expiry) - date.today()).days / 365
    if T <= 0 or sigma<=0: return 0.0
    d2 = _bs_d2(_bs_d1(S,K,r,sigma,T), sigma, T)
    if is_call:
        return K*T*math.exp(-r*T)*norm.cdf(d2)/100
    else:
        return -K*T*math.exp(-r*T)*norm.cdf(-d2)/100
