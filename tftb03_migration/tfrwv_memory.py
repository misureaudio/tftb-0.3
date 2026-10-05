#!/usr/bin/env python3
"""
tfrwv_memory.py
===============

Estimate the MATLAB memory footprint of a call to ``tfrwv`` (Wigner-Ville
time-frequency distribution) from the Time-Frequency Toolbox (TFTB, Flandrin)
for a signal of **arbitrary, user-defined length**.

The model follows the actual algorithm in ``tftb/mfiles/tfrwv.m``:

    1.  tfr = zeros(N, T)            real double matrix,  N x T
    2.  per-time loop filling lag columns (small O(N) temporaries each)
    3.  tfr = fft(tfr)               matrix becomes complex double, N x T
    4.  tfr = real(tfr)  (auto-WV)   back to real double
    5.  f = (0.5*(0:N-1)/N)'         frequency axis, N doubles (nargout==3)

Peak memory occurs in step 3: the real matrix, the complex FFT result and
FFTM's internal workspace coexist (the right-hand side of ``tfr = fft(tfr)``
is fully computed before the old real matrix is released).

NOTES
-----
* N is the number of frequency bins (default: the signal length), T the
  number of time instants in ``t`` (default: the signal length).  They are
  independent parameters of tfrwv and both are user-definable here.
* int16 input: the estimate takes the input dtype at face value, but passing
  raw int16 data to tfrwv is a *numerical* mistake -- MATLAB integer
  arithmetic saturates in the lag products ``x(ti+tau).*conj(x(ti-tau))``.
  Convert first, e.g. ``x = double(raw) / 32768``.
* nargout == 0 makes tfrwv open a figure (tfrqview); GUI rendering memory
  is not modeled (it is dominated by the TFR matrix anyway).

CLI usage
---------
    python tfrwv_memory.py 2048
    python tfrwv_memory.py 2048 --dtype float64
    python tfrwv_memory.py 4096 --N 2048 --times 1024 --cross
    python tfrwv_memory.py 2048 --nargout 0

Module usage
------------
    from tfrwv_memory import estimate_tfrwv_memory
    est = estimate_tfrwv_memory(2048, dtype="int16")
    print(est.summary())
    print(est.peak_bytes)   # machine-readable
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

# MATLAB scalar storage sizes in bytes (numpy-style names accepted too).
_DTYPE_SIZES = {
    "int8": 1, "uint8": 1,
    "int16": 2, "uint16": 2,
    "int32": 4, "uint32": 4, "single": 4, "float32": 4,
    "int64": 8, "uint64": 8, "double": 8, "float64": 8,
    "complex64": 8, "single-complex": 8,
    "complex128": 16, "double-complex": 16,
}

_COMPLEX_INPUTS = {"complex64", "single-complex", "complex128", "double-complex"}

_DOUBLE = 8   # MATLAB double
_INT32 = 4    # MATLAB int32 (vector indices)


def _human(n: float) -> str:
    """Format a byte count as a human-readable string."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024 or unit == "TiB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:,.2f} {unit}"
        n /= 1024.0
    return f"{n:,.2f} TiB"  # unreachable


@dataclass(frozen=True)
class MemoryEstimate:
    """Itemized memory estimate for one tfrwv call."""

    # parameters
    n_samples: int          # length of the input signal
    n_freq: int             # N: number of frequency bins
    n_times: int            # T: number of time instants (length of t)
    cross_wv: bool          # True -> x has 2 columns (cross-WV)
    dtype: str              # input dtype name
    nargout: int            # 0 -> figure, 3 -> also return f

    # item sizes (bytes)
    input_bytes: int        # the signal itself
    t_vector_bytes: int     # t (double row vector)
    tfr_real_bytes: int     # N x T real double (steady state)
    tfr_complex_bytes: int  # N x T complex double (during/after fft)
    fft_workspace_bytes: int  # FFTM internal buffers (estimate)
    temp_bytes: int         # worst per-iteration temporaries
    f_vector_bytes: int     # frequency axis (nargout == 3 only)

    # totals
    steady_bytes: int       # after the call returns
    peak_bytes: int         # during the fft step


def estimate_tfrwv_memory(
    n_samples: int,
    dtype: str = "int16",
    n_freq: int | None = None,
    n_times: int | None = None,
    cross_wv: bool = False,
    nargout: int = 3,
    fft_workspace_factor: float = 1.0,
) -> MemoryEstimate:
    """Estimate the memory required by ``tfrwv(x, t, N)`` in MATLAB.

    Parameters
    ----------
    n_samples : int
        Length of the input signal (any positive integer).
    dtype : str
        MATLAB dtype of the input signal (see _DTYPE_SIZES).  Default
        "int16" (16-bit signed PCM samples).
    n_freq : int, optional
        N, the number of frequency bins.  Default: n_samples (the call
        ``tfrwv(x)`` uses N = length(x)).
    n_times : int, optional
        T, the number of time instants in ``t``.  Default: n_samples
        (``t = 1:length(x)``).
    cross_wv : bool
        True if x has two columns (cross-Wigner-Ville).  Doubles the
        input size; the TFR matrix size is unchanged.
    nargout : int
        0 (figure only), 1, 2 or 3 (also return the f axis).  Affects the
        f vector allocation.
    fft_workspace_factor : float
        FFTM internal workspace, expressed in complex-matrix multiples.
        1.0 = one full complex N x T buffer (conservative default).

    Returns
    -------
    MemoryEstimate
        Itemized breakdown plus steady-state and peak totals.
    """
    if n_samples <= 0:
        raise ValueError(f"n_samples must be > 0, got {n_samples}")
    if not 0 <= nargout <= 3:
        raise ValueError(f"nargout must be 0..3, got {nargout}")
    if fft_workspace_factor < 0:
        raise ValueError("fft_workspace_factor must be >= 0")

    key = dtype.lower()
    if key not in _DTYPE_SIZES:
        raise ValueError(
            f"unknown dtype {dtype!r}; choose from {sorted(_DTYPE_SIZES)}"
        )
    itemsize = _DTYPE_SIZES[key]

    N = n_freq if n_freq is not None else n_samples
    T = n_times if n_times is not None else n_samples
    if N <= 0 or T <= 0:
        raise ValueError("n_freq and n_times must be > 0")

    # 1) input signal (x has 1 or 2 columns)
    cols = 2 if cross_wv else 1
    input_bytes = n_samples * itemsize * cols

    # 2) t vector: double row vector of length T
    t_vector_bytes = T * _DOUBLE

    # 3) the TFR matrix, real then complex
    tfr_real_bytes = N * T * _DOUBLE
    tfr_complex_bytes = N * T * 2 * _DOUBLE
    fft_workspace_bytes = int(fft_workspace_factor * tfr_complex_bytes)

    # 4) per-iteration temporaries, worst case (signal midpoint):
    #    tau (double), indices (int32), and the lag-product vector
    #    (complex only if x is complex)
    taumax = min(n_samples // 2 - 1, N // 2 - 1)
    m = max(2 * taumax + 1, 1)
    prod_item = 2 * _DOUBLE if key in _COMPLEX_INPUTS else _DOUBLE
    temp_bytes = m * (_DOUBLE + _INT32 + prod_item)

    # 5) frequency axis
    f_vector_bytes = N * _DOUBLE if nargout == 3 else 0

    steady_bytes = input_bytes + t_vector_bytes + tfr_real_bytes + f_vector_bytes
    peak_bytes = (
        input_bytes + t_vector_bytes + tfr_real_bytes
        + tfr_complex_bytes + fft_workspace_bytes + temp_bytes
    )

    return MemoryEstimate(
        n_samples=n_samples,
        n_freq=N,
        n_times=T,
        cross_wv=cross_wv,
        dtype=key,
        nargout=nargout,
        input_bytes=input_bytes,
        t_vector_bytes=t_vector_bytes,
        tfr_real_bytes=tfr_real_bytes,
        tfr_complex_bytes=tfr_complex_bytes,
        fft_workspace_bytes=fft_workspace_bytes,
        temp_bytes=temp_bytes,
        f_vector_bytes=f_vector_bytes,
        steady_bytes=steady_bytes,
        peak_bytes=peak_bytes,
    )


def _summary(est: MemoryEstimate) -> str:
    wv = "cross-WV (2 columns)" if est.cross_wv else "auto-WV"
    lines = [
        "tfrwv memory estimate (MATLAB, tftb mfiles/tfrwv.m)",
        f"  signal length  = {est.n_samples:,} samples, dtype = {est.dtype} ({wv})",
        f"  frequency bins N = {est.n_freq:,}",
        f"  time instants  T = {est.n_times:,}",
        "",
        f"  input signal               {_human(est.input_bytes)}",
        f"  t vector (double)          {_human(est.t_vector_bytes)}",
        f"  tfr real   N x T           {_human(est.tfr_real_bytes)}   <- steady state",
        f"  tfr complex (during fft)   {_human(est.tfr_complex_bytes)}   <- peak",
        f"  fft workspace (estimate)   {_human(est.fft_workspace_bytes)}   <- peak",
        f"  per-iteration temporaries  {_human(est.temp_bytes)}   <- peak",
    ]
    if est.f_vector_bytes:
        lines.append(f"  f vector (nargout=3)       {_human(est.f_vector_bytes)}")
    if est.nargout == 0:
        lines.append("  (nargout=0: tfrqview opens a figure; GUI memory not modeled)")
    lines += [
        "",
        f"  STEADY-STATE TOTAL         {_human(est.steady_bytes)}  ({est.steady_bytes:,} B)",
        f"  PEAK TOTAL (during fft)    {_human(est.peak_bytes)}  ({est.peak_bytes:,} B)",
    ]
    return "\n".join(lines)


def _cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Estimate MATLAB memory for a tfrwv (Wigner-Ville) call "
                    "on a signal of arbitrary length."
    )
    p.add_argument("n_samples", type=int,
                   help="signal length in samples (any positive integer)")
    p.add_argument("--dtype", default="int16",
                   help=f"input dtype (default: int16); one of {sorted(_DTYPE_SIZES)}")
    p.add_argument("--N", dest="n_freq", type=int, default=None,
                   help="number of frequency bins (default: signal length)")
    p.add_argument("--times", dest="n_times", type=int, default=None,
                   help="number of time instants in t (default: signal length)")
    p.add_argument("--cross", action="store_true",
                   help="cross-WV: x has two columns")
    p.add_argument("--nargout", type=int, choices=(0, 1, 2, 3), default=3,
                   help="0 = figure only, 3 = also return f axis (default: 3)")
    p.add_argument("--fft-workspace-factor", type=float, default=1.0,
                   help="FFTM workspace in complex-matrix multiples (default: 1.0)")
    a = p.parse_args(argv)

    est = estimate_tfrwv_memory(
        n_samples=a.n_samples,
        dtype=a.dtype,
        n_freq=a.n_freq,
        n_times=a.n_times,
        cross_wv=a.cross,
        nargout=a.nargout,
        fft_workspace_factor=a.fft_workspace_factor,
    )
    print(_summary(est))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
