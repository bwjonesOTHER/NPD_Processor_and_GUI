import os
import re
import traceback
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skrf as rf
from glob import glob
from datetime import datetime

def win_long(path):
    if path is None:
        return None
    if os.name == "nt":
        ap = os.path.abspath(path)
        if not ap.startswith("\\\\?\\"):
            ap = "\\\\?\\" + ap
        return ap
    return path

def folder_label(path):
    # Basename that tolerates mixed \ and / separators (win_long can prefix
    # \\?\ on Windows), so plot titles reflect the actual folder found.
    return re.split(r"[\\/]+", path.rstrip("\\/"))[-1] or path

def find_group_folder(root, keyword, group_num):
    # Group 1/2 data sometimes lives in its own subfolder (e.g. "AMB 1",
    # "Cold 2", "HOT2") and sometimes group 1's files just sit directly in
    # the parent temperature folder with no "1" subfolder at all. Search for
    # a child folder whose name contains the keyword and the group number as
    # its own token (so "1" doesn't match inside "10"); fall back to the
    # parent so group 1 keeps working when there's no dedicated subfolder.
    if not os.path.isdir(root):
        return root
    digit_re = re.compile(rf"(?<!\d){group_num}(?!\d)")
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full) and keyword in name.lower() and digit_re.search(name):
            return full
    return root

def find_folder_by_keyword(root, keyword):
    # For one-off subfolders (e.g. "Anomaly AMB") that don't fit the
    # group-1/group-2 pattern — matched by keyword only, no digit required.
    if not os.path.isdir(root):
        return None
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full) and keyword in name.lower():
            return full
    return None

def find_cable_file(folder, include_kw, exclude_kw=None):
    # Cable-loss filenames are date-stamped (e.g. "20260713_..."), so match
    # on the descriptive part of the name instead of hardcoding the date.
    candidates = glob(os.path.join(folder, "*.s2p")) + glob(os.path.join(folder, "*.S2P"))
    matches = [
        f for f in candidates
        if include_kw in os.path.basename(f).lower()
        and (exclude_kw is None or exclude_kw not in os.path.basename(f).lower())
    ]
    if not matches:
        raise FileNotFoundError(f"No cable-loss file containing '{include_kw}' found in {folder}")
    return sorted(matches)[0]

MAIN = win_long(
    r"C:\Users\brannon.jones\Desktop\Fake Sharepoint\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA ARRAY\Test Hat\SN0001_LMO1157-1-59-7"
)

# NEW: Output directory for all plots
OUTDIR = win_long(os.path.join(MAIN, "ENG_review"))
os.makedirs(OUTDIR, exist_ok=True)

AMBIENT_ROOT = win_long(MAIN + r"\Ambient Measurements")
COLD_ROOT    = win_long(MAIN + r"\Cold Measurements")
HOT_ROOT     = win_long(MAIN + r"\Hot Measurements")
CABLE        = win_long(MAIN + r"\Cable Loss")

# AMB 1/Cold 1/Hot 1 are their own group, kept separate from AMB 2/Cold
# 2/Hot2 — resolved dynamically so each points at whichever subfolder
# actually holds that group's data (see find_group_folder above).
AMBIENT  = win_long(find_group_folder(AMBIENT_ROOT, "amb", 1))
AMBIENT2 = win_long(find_group_folder(AMBIENT_ROOT, "amb", 2))
COLD     = win_long(find_group_folder(COLD_ROOT, "cold", 1))
COLD2    = win_long(find_group_folder(COLD_ROOT, "cold", 2))
HOT      = win_long(find_group_folder(HOT_ROOT, "hot", 1))
HOT2     = win_long(find_group_folder(HOT_ROOT, "hot", 2))

# Third, ungrouped ambient run (fault/anomaly capture) — plotted on its own,
# not paired into the AMB1/AMB2 group overlay.
AMBIENT_ANOMALY = win_long(find_folder_by_keyword(AMBIENT_ROOT, "anomaly"))

# SPECAN calibrates NP/NPD (its chain has an amplifier in line, so its
# figure is net gain and gets subtracted, not added); BASE/HAT calibrate
# S21 only — see plot_npd/overlay_temperature vs. plot_s21.
SPECAN = win_long(find_cable_file(CABLE, "specan"))
BASE   = win_long(find_cable_file(CABLE, "base", exclude_kw="specan"))
HAT    = win_long(find_cable_file(CABLE, "hat"))

n_avg = 20

freq_min = 2.6
freq_max = 4.2

npd_ylim = (-160, -140)
s21_ylim = (-20, 0)

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

def smooth(x, n_avg=n_avg):
    if len(x) < n_avg:
        return x
    return np.convolve(x, np.ones(n_avg)/n_avg, mode="valid")

# NPD CSV smoothing window depends on the sweep's actual frequency step -
# a finer step (more points over the same span) needs a wider window to
# get comparable smoothing; a coarse step needs none. Computed per-file
# since different files/folders can use different steps.
_NPD_STEP_TO_NAVG = [(0.3, 83), (1.0, 25), (25.0, 1)]

def n_avg_for_freq_step(freq):
    if len(freq) < 2:
        return 1
    step_mhz = abs(np.median(np.diff(freq))) * 1000.0  # freq is in GHz
    return min(_NPD_STEP_TO_NAVG, key=lambda pair: abs(pair[0] - step_mhz))[1]

def smooth_npd(freq, values):
    npd_n_avg = n_avg_for_freq_step(freq)
    values_smooth = smooth(values, npd_n_avg)
    freq_smooth = freq[: len(values_smooth)]
    return freq_smooth, values_smooth

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
        freq_smooth, npd_smooth = smooth_npd(freq, npd_raw)
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
    plt.close()
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
    plt.close()
    print("Saved:", out)

# ============================================================
# OVERLAY PLOTS
# ============================================================
def overlay_temperature(folders):
    folders = [f for f in folders if f]
    labels = [folder_label(f) for f in folders]
    combined_label = " & ".join(labels)
    file_tag = "_".join(labels)

    for folder, label in zip(folders, labels):
        n_csv = len(get_csv(folder))
        n_s2p = len(get_s2p(folder))
        print(f"  overlay input {label:16s} -> {folder}  [csv={n_csv}, s2p={n_s2p}]")

    files = [f for folder in folders for f in get_csv(folder)]
    if not files:
        print(f"No NPD files for overlay {combined_label} — skipping NPD overlay")
    else:
        _plot_npd_overlay(files, combined_label, file_tag)

    files_s2p = [f for folder in folders for f in get_s2p(folder)]
    if not files_s2p:
        print(f"No S21 files for overlay {combined_label} — skipping S21 overlay")
    else:
        _plot_s21_overlay(files_s2p, combined_label, file_tag)

def _plot_npd_overlay(files, combined_label, file_tag):
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
        freq_smooth, npd_smooth = smooth_npd(freq, npd_raw)
        corrected = npd_smooth
        if APPLY_NPD_CAL:
            corrected = corrected - np.abs(np.interp(freq_smooth, specan_freq, specan_s12))
        plt.plot(freq_smooth, corrected, label=os.path.basename(f), color=next(color_cycle))

    plt.grid(True)
    plt.title(f"{DATE_STR} NPD OVERLAY — {combined_label} ({'Calibrated' if APPLY_NPD_CAL else 'Raw'})")
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

    out = win_long(os.path.join(OUTDIR, f"{DATE_STR}_NPD_OVERLAY_{file_tag}.png"))
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", out)

def _plot_s21_overlay(files_s2p, combined_label, file_tag):
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
    plt.title(f"{DATE_STR} S21 OVERLAY — {combined_label}")
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

    out = win_long(os.path.join(OUTDIR, f"{DATE_STR}_S21_OVERLAY_{file_tag}.png"))
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved:", out)

# ============================================================
# MAIN DRIVER
# ============================================================
def _describe_folder(name, folder):
    if not folder:
        print(f"  {name:14s} -> NOT FOUND")
        return
    exists = os.path.isdir(folder)
    n_csv = len(get_csv(folder)) if exists else 0
    n_s2p = len(get_s2p(folder)) if exists else 0
    print(f"  {name:14s} -> {folder}  [exists={exists}, csv={n_csv}, s2p={n_s2p}]")

def _describe_cal_file(name, path):
    print(f"  {name:14s} -> {path}  [exists={bool(path) and os.path.isfile(path)}]")

def process_all():
    named_folders = [
        ("AMB1", AMBIENT),
        ("AMB2", AMBIENT2),
        ("Anomaly AMB", AMBIENT_ANOMALY),
        ("COLD1", COLD),
        ("COLD2", COLD2),
        ("HOT1", HOT),
        ("HOT2", HOT2),
    ]

    print("=== Resolved paths ===")
    for name, folder in named_folders:
        _describe_folder(name, folder)
    _describe_cal_file("SPECAN", SPECAN)
    _describe_cal_file("BASE", BASE)
    _describe_cal_file("HAT", HAT)

    succeeded, skipped, failed = [], [], []

    for name, folder in named_folders:
        if not folder:
            print(f"\n=== Skipping {name}: folder not found ===")
            skipped.append(name)
            continue
        label = folder_label(folder)
        print(f"\n=== Processing: {label} ===")
        try:
            plot_npd(get_csv(folder), label)
            plot_s21(get_s2p(folder), label)
            succeeded.append(label)
        except Exception:
            print(f"!!! ERROR processing {label} — continuing with remaining folders !!!")
            traceback.print_exc()
            failed.append(label)

    overlay_groups = [
        ("Ambient overlay", [AMBIENT, AMBIENT2, AMBIENT_ANOMALY]),
        ("Cold overlay", [COLD, COLD2]),
        ("Hot overlay", [HOT, HOT2]),
    ]
    for name, group in overlay_groups:
        print(f"\n=== Processing: {name} ===")
        try:
            overlay_temperature(group)
            succeeded.append(name)
        except Exception:
            print(f"!!! ERROR processing {name} — continuing !!!")
            traceback.print_exc()
            failed.append(name)

    print("\n=== Summary ===")
    print("Succeeded:", succeeded or "(none)")
    print("Skipped (folder not found):", skipped or "(none)")
    print("Failed (see traceback above):", failed or "(none)")


if __name__ == "__main__":
    process_all()
