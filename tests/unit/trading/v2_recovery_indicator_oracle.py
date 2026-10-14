"""Independent exact geometric-polynomial oracle, for invented tick-grid inputs only.

W(x,a,b)=sum(x[j]*a**(n-1-j)*b**j). Divide and conquer evaluates W without
following the candidate's shared-denominator state recurrence. The signal uses
the exact filter identity 11/3*EMA12 - 25/17*EMA26 - 112/51*EMA9(close), whose
seed is zero and whose recurrence is Signal'=4/5*Signal+1/5*(EMA12'-EMA26').
"""

from __future__ import annotations

from fractions import Fraction


def _weighted(values, start, stop, a, b):
    length = stop - start
    if length == 0:
        return 0
    if length == 1:
        return values[start]
    middle = start + length // 2
    return (_weighted(values, start, middle, a, b) * a ** (stop - middle)
            + _weighted(values, middle, stop, a, b) * b ** (middle - start))


def _ema(ticks, count, a, b, alpha_numerator):
    q = count - 1
    return Fraction(ticks[0] * a ** q + alpha_numerator * _weighted(
        ticks, 1, count, a, b), 4 * b ** q)


def _macd(ticks, count):
    fast = _ema(ticks, count, 11, 13, 2)
    slow = _ema(ticks, count, 25, 27, 2)
    price_signal = _ema(ticks, count, 4, 5, 1)
    signal = Fraction(11, 3) * fast - Fraction(25, 17) * slow - Fraction(112, 51) * price_signal
    line = fast - slow
    return fast, slow, line, signal, line - signal


def exact_indicator_polynomial_oracle(bars):
    """Return exact full current/previous values; no strategy, real loader or float."""
    ticks = []
    for bar in bars:
        price = Fraction(bar.close) * 4
        if price.denominator != 1:
            raise ValueError("oracle requires invented exact tick-grid prices")
        ticks.append(price.numerator)
    count = len(ticks)
    if not count:
        raise ValueError("oracle requires at least one observation")
    ema = None
    if count >= 20:
        steps = count - 20
        ema = Fraction(sum(ticks[:20]) * 19 ** steps + 40 * _weighted(
            ticks, 20, count, 19, 21), 80 * 21 ** steps)
    fast, slow, line, signal, histogram = _macd(ticks, count)
    previous_line = previous_hist = None
    if count > 1:
        _, _, previous_line, _, previous_hist = _macd(ticks, count - 1)
    return {"ema20": ema, "ema12": fast, "ema26": slow, "macd": line,
            "signal": signal, "histogram": histogram, "previous_macd": previous_line,
            "previous_histogram": previous_hist}
