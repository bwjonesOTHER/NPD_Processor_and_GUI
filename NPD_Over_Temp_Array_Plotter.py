import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skrf as rf
from glob import glob
from datetime import datetime

def win_long(path):
    if os.name == "nt":
        ap = os.path.abspath(path)
        if not ap.startswith("\\\\?\\"):
            ap = "\\\\?\\" + ap
        return ap
    return path

MAIN = win_long(
    r"C:\Users\brannon.jones\Desktop\Fake Sharepoint\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA ARRAY\Test Hat\SN0001_LMO1157-1-59-7"
)

# NEW: Output directory for all plots
OUTDIR = win_long(os.path.join(MAIN, "ENG_review"))
os.makedirs(OUTDIR, exist_ok=True)

AMBIENT  = win_long(MAIN + r"\Ambient Measurements")
AMBIENT2 = win_long(AMBIENT + r"\AMB 2")
COLD     = win_long(MAIN + r"\Cold Measurements")
COLD2    = win_long(COLD + r"\Cold 2")
HOT      = win_long(MAIN + r"\Hot Measurements")
HOT2     = win_long(HOT + r"\HOT2")
CABLE    = win_long(MAIN + r"\Cable Loss")

# SPECAN calibrates NP/NPD (its chain has an amplifier in line, so its
# figure is net gain and gets subtracted, not added); BASE/HAT calibrate
# S21 only — see plot_npd/overlay_temperature vs. plot_s21.
SPECAN = win_long(os.path.join(CABLE, "20260713_SpecAnBaseCableAssy_pathloss.s2p"))
BASE   = win_long(os.path.join(CABLE, "20260713_BaseCableAssy_pathloss.s2p"))
HAT    = win_long(os.path.join(CABLE, "20260713_HatCableAssy_pathloss.s2p"))

n_avg = 20

freq_min = 2.0
freq_max = 5.0

npd_ylim = (-170, -140)
s21_ylim = (-105, 5)

show_plot = True

# NP/NPD are plotted raw by default (no cable-loss correction). Flip this to
# True to apply the Base + Hat cable-loss cal to NP/NPD too. S21 always
# stays calibrated regardless of this flag.
APPLY_NPD_CAL = False

# Date prefix stamped on every plot title/filename.
DATE_STR = datetime.now().strftime('%Y%m%d')

my_colors = [
    "blue", "orange", "green", "red", "purple",
    "cyan", "magenta", "brown", "gold", "black"
]

def smooth(x):
    if len(x) < n_avg:
        return x
    return np.convolve(x, np.ones(n_avg)/n_avg, mode="valid")

def _dedupe_pri_red(files, limit=2):
    # De-dupe: on case-insensitive filesystems (Windows), "*.csv" and "*.CSV"
    # both match the same file, so combining the two globs returns it twice.
    seen = set()
    deduped = []
    for f in sorted(files):
        key = os.path.normcase(os.path.abspath(f))
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    # Prefer one Pri file + one Red file (the two redundant chains) over
    # picking the first two matches, which could both land on the same chain.
    pri = [f for f in deduped if "pri" in os.path.basename(f).lower()]
    red = [f for f in deduped if "red" in os.path.basename(f).lower()]
    if pri and red:
        return [pri[0], red[0]]
    return deduped[:limit]

def get_csv(folder):
    return _dedupe_pri_red(glob(os.path.join(folder, "*.csv")))

def get_s2p(folder):
    return _dedupe_pri_red(glob(os.path.join(folder, "*.s2p")) + glob(os.path.join(folder, "*.S2P")))

def load_s2p(file):
    net = rf.Network(file)
    freq = net.f / 1e9
    s21  = net.s_db[:, 1, 0]
    return freq, s21

def load_s2p_s12(file):
    # SPECAN has an amplifier inline, so it's non-reciprocal: S21 is its
    # heavily-isolated reverse path (tens of dB of loss, not usable), while
    # S12 is the actual forward path the NP/NPD signal travels through (a
    # real gain figure). Base/Hat are passive and reciprocal (S21 == S12),
    # so only SPECAN needs this S12 read.
    net = rf.Network(file)
    freq = net.f / 1e9
    s12 = net.s_db[:, 0, 1]
    return freq, s12

def enforce_equal_length(freq, s21):
    min_len = min(len(freq), len(s21))
    return freq[:min_len], s21[:min_len]

# ============================================================
# NPD PLOT
# ============================================================
def plot_npd(files, title_suffix):
    if not files:
        print(f"No NPD files for {title_suffix}")
        return

    # NP/NPD only needs the SpecAn cal file — Base/Hat don't apply to it
    # (they calibrate S21 instead; see plot_s21). SpecAn's assembly had an
    # amplifier inline when its pathloss file was made — so it's
    # non-reciprocal: its real signal-path figure (S12, not S21 — see
    # load_s2p_s12) is net GAIN and gets subtracted back out.
    specan_freq, specan_s12 = load_s2p_s12(SPECAN)
    specan_s12 = smooth(specan_s12)
    specan_freq, specan_s12 = enforce_equal_length(specan_freq, specan_s12)

    plt.figure(figsize=(8, 4), dpi=150)
    color_cycle = iter(my_colors)

    for f in files:
        df = pd.read_csv(f).apply(pd.to_numeric, errors="coerce")
        freq = df.iloc[:, 0].values
        npd_raw = df.iloc[:, 1].values
        freq = freq[np.isfinite(freq)]
        npd_raw = npd_raw[np.isfinite(npd_raw)]
        npd_smooth = smooth(npd_raw)
        freq_smooth = freq[:len(npd_smooth)]
        corrected = npd_smooth
        if APPLY_NPD_CAL:
            corrected = corrected - np.abs(np.interp(freq_smooth, specan_freq, specan_s12))
        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))

    plt.grid(True)
    plt.title(f"{DATE_STR} NPD {title_suffix} ({'Calibrated' if APPLY_NPD_CAL else 'Raw'})")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Noise Power (dBm)")
    plt.xlim(freq_min, freq_max)
    plt.ylim(npd_ylim)

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=1,
        fontsize="8"
    )

    plt.subplots_adjust(bottom=0.45)

    out = win_long(os.path.join(OUTDIR, f"{DATE_STR}_NPD_{title_suffix}.png"))
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print("Saved:", out)


# ============================================================
# S21 PLOT
# ============================================================
def plot_s21(files, title_suffix):
    if not files:
        print(f"No S21 files for {title_suffix}")
        return

    base_freq, base_s21 = load_s2p(BASE)
    hat_freq,  hat_s21  = load_s2p(HAT)

    base_s21 = smooth(base_s21)
    hat_s21  = smooth(hat_s21)

    base_freq, base_s21 = enforce_equal_length(base_freq, base_s21)
    hat_freq,  hat_s21  = enforce_equal_length(hat_freq, hat_s21)

    plt.figure(figsize=(8, 4), dpi=150)
    color_cycle = iter(my_colors)

    for f in files:
        freq, s21 = load_s2p(f)
        s21_smooth = smooth(s21)
        freq_smooth = freq[:len(s21_smooth)]
        corrected = s21_smooth + np.abs(np.interp(freq_smooth, base_freq, base_s21)) + np.abs(np.interp(freq_smooth, hat_freq, hat_s21))
        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))

    plt.grid(True)
    plt.title(f"{DATE_STR} S21 {title_suffix}")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("S21 (dB)")
    plt.xlim(freq_min, freq_max)
    plt.ylim(s21_ylim)

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=1,
        fontsize="8"
    )

    plt.subplots_adjust(bottom=0.45)

    out = win_long(os.path.join(OUTDIR, f"{DATE_STR}_S21_{title_suffix}.png"))
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print("Saved:", out)

# ============================================================
# OVERLAY PLOTS
# ============================================================
def overlay_temperature(temp_name, folder1, folder2):

    files = get_csv(folder1) + get_csv(folder2)

    # NP/NPD only needs the SpecAn cal file — Base/Hat don't apply to it
    # (they calibrate S21 instead; see the S21 overlay below). SpecAn's real
    # signal-path figure (S12, not S21 — see load_s2p_s12) is net GAIN and
    # gets subtracted back out.
    specan_freq, specan_s12 = load_s2p_s12(SPECAN)
    specan_s12 = smooth(specan_s12)
    specan_freq, specan_s12 = enforce_equal_length(specan_freq, specan_s12)

    plt.figure(figsize=(8, 4), dpi=150)
    color_cycle = iter(my_colors)

    for f in files:
        df = pd.read_csv(f).apply(pd.to_numeric, errors="coerce")
        freq = df.iloc[:, 0].values
        npd_raw = df.iloc[:, 1].values
        freq = freq[np.isfinite(freq)]
        npd_raw = npd_raw[np.isfinite(npd_raw)]
        npd_smooth = smooth(npd_raw)
        freq_smooth = freq[:len(npd_smooth)]
        corrected = npd_smooth
        if APPLY_NPD_CAL:
            corrected = corrected - np.abs(np.interp(freq_smooth, specan_freq, specan_s12))
        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))

    plt.grid(True)
    plt.title(f"{DATE_STR} NPD OVERLAY — {temp_name} & {temp_name}2 ({'Calibrated' if APPLY_NPD_CAL else 'Raw'})")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Noise Power (dBm)")
    plt.xlim(freq_min, freq_max)
    plt.ylim(npd_ylim)

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=1,
        fontsize="8"
    )

    plt.subplots_adjust(bottom=0.45)

    out = win_long(os.path.join(OUTDIR, f"{DATE_STR}_NPD_OVERLAY_{temp_name}.png"))
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print("Saved:", out)

    # ---------------------
    # S21 overlay
    # ---------------------
    files_s2p = get_s2p(folder1) + get_s2p(folder2)

    base_freq, base_s21 = load_s2p(BASE)
    hat_freq, hat_s21 = load_s2p(HAT)

    base_s21 = smooth(base_s21)
    hat_s21 = smooth(hat_s21)

    base_freq, base_s21 = enforce_equal_length(base_freq, base_s21)
    hat_freq, hat_s21 = enforce_equal_length(hat_freq, hat_s21)

    plt.figure(figsize=(8, 4), dpi=150)
    color_cycle = iter(my_colors)

    for f in files_s2p:
        freq, s21 = load_s2p(f)
        s21_smooth = smooth(s21)
        freq_smooth = freq[:len(s21_smooth)]
        corrected = s21_smooth + np.abs(np.interp(freq_smooth, base_freq, base_s21)) + np.abs(np.interp(freq_smooth, hat_freq, hat_s21))
        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))

    plt.grid(True)
    plt.title(f"{DATE_STR} S21 OVERLAY — {temp_name} & {temp_name}2")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("S21 (dB)")
    plt.xlim(freq_min, freq_max)
    plt.ylim(s21_ylim)

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=1,
        fontsize="8"
    )

    plt.subplots_adjust(bottom=0.45)

    out = win_long(os.path.join(OUTDIR, f"{DATE_STR}_S21_OVERLAY_{temp_name}.png"))
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print("Saved:", out)

# ============================================================
# MAIN DRIVER
# ============================================================
def process_all():
    folders = [
        ("Ambient", AMBIENT),
        ("Ambient2", AMBIENT2),
        ("Cold", COLD),
        ("Cold2", COLD2),
        ("Hot", HOT),
        ("Hot2", HOT2)
    ]

    for label, folder in folders:
        print(f"\n=== Processing: {label} ===")
        plot_npd(get_csv(folder), label)
        plot_s21(get_s2p(folder), label)

    overlay_temperature("Ambient", AMBIENT, AMBIENT2)
    overlay_temperature("Cold", COLD, COLD2)
    overlay_temperature("Hot", HOT, HOT2)


if __name__ == "__main__":
    process_all()
