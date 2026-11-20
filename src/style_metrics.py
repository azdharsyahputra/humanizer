"""
style_metrics.py
Hitung metrik gaya tulisan Bahasa Indonesia dari sebuah teks.
Dipakai untuk: (1) membangun profil korpus manusia, (2) menilai draft.

Semua metrik murni statistik permukaan — tidak ada model, tidak ada jaringan.
"""
import re
import statistics
from collections import Counter

# ---- leksikon ringkas (bisa diperluas) ----
CONNECTIVES_FORMAL = [
    "namun", "tetapi", "akan tetapi", "oleh karena itu", "oleh sebab itu",
    "dengan demikian", "sehingga", "selain itu", "di samping itu",
    "berdasarkan", "sebagaimana", "adapun", "meskipun", "walaupun",
]
CONNECTIVES_INFORMAL = [
    "tapi", "jadi", "makanya", "soalnya", "terus", "trus", "nah", "lagian",
    "kayak", "gitu", "banget", "nggak", "gak", "ga", "gue", "lu",
]
FIRST_PERSON = ["aku", "gua", "gue", "gw", "saya"]  # 'saya' lebih formal, dipisah di skor
HEDGES = ["mungkin", "sepertinya", "kira-kira", "kurang lebih", "cenderung",
          "diduga", "diperkirakan", "relatif"]
# frasa padding generik — pengisi hampa yang bikin tulisan kebaca templated/AI
PADDING = [
    "memiliki kemampuan yang signifikan", "memiliki kemampuan", "memiliki peran",
    "memegang peranan penting", "berperan penting", "peran penting",
    "menjadi semakin penting", "sangat penting", "yang signifikan",
    "secara signifikan", "diharapkan dapat", "diharapkan mampu",
    "memberikan kontribusi", "tidak dapat dipungkiri", "seiring perkembangan",
    "seiring berkembangnya", "di era modern", "di era digital",
    "dalam kehidupan sehari-hari", "berbagai macam", "pesatnya perkembangan",
    "kemajuan teknologi yang", "salah satu faktor", "menjadi sorotan",
]

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD = re.compile(r"\w+", re.UNICODE)
# kata kerja pasif heuristik: awalan di- diikuti huruf (bukan 'di ' preposisi)
PASSIVE = re.compile(r"\bdi[a-z]{3,}\b", re.IGNORECASE)
# token "spesifik": akronim ALLCAPS, CamelCase, atau mengandung angka (mis. Qwen2.5,
# TF-IDF, CoT, ROC-AUC, 65%, 7-70). Penanda substansi konkret / perplexity sehat.
SPECIFIC = re.compile(r"\b(?:[A-Z]{2,}[\w.-]*|[A-Za-z]+[A-Z][\w.-]*|[\w.-]*\d[\w.,%-]*)\b")
CITATION = re.compile(r"et al\.|\(\s*\d{4}\s*\)|\b\d{4}[a-z]?\)")


_PAT_CACHE = {}


def _count_phrases(low_text, phrases):
    """Hitung kemunculan kata/frasa dengan batas kata (\\b) — bukan substring.
    Jadi 'tapi' tidak ketangkep di dalam 'tetapi'."""
    key = id(phrases)
    pat = _PAT_CACHE.get(key)
    if pat is None:
        alt = "|".join(re.escape(p) for p in sorted(phrases, key=len, reverse=True))
        pat = re.compile(r"\b(?:" + alt + r")\b", re.IGNORECASE)
        _PAT_CACHE[key] = pat
    return len(pat.findall(low_text))


def compute_metrics(text):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    low = text.lower()

    sents = [s.strip() for s in SENT_SPLIT.split(text) if len(s.strip()) > 1]
    if len(sents) < 3:
        return None
    wc = [len(WORD.findall(s)) for s in sents]
    wc = [w for w in wc if w > 0]
    n_sent = len(wc)
    n_word = sum(wc)

    # distribusi panjang kalimat
    buckets = {"s1_5": 0, "s6_10": 0, "s11_18": 0, "s19_30": 0, "s31p": 0}
    for w in wc:
        if w <= 5: buckets["s1_5"] += 1
        elif w <= 10: buckets["s6_10"] += 1
        elif w <= 18: buckets["s11_18"] += 1
        elif w <= 30: buckets["s19_30"] += 1
        else: buckets["s31p"] += 1
    dist = {k: round(v / n_sent, 4) for k, v in buckets.items()}

    # burstiness: rata-rata beda panjang antar kalimat berurutan / rata panjang
    diffs = [abs(wc[i] - wc[i - 1]) for i in range(1, len(wc))]
    burstiness = round((statistics.mean(diffs) / statistics.mean(wc)), 4) if diffs else 0.0

    # pembuka kalimat berulang (konsentrasi: makin tinggi makin monoton)
    openers = Counter()
    for s in sents:
        m = re.match(r"[^\wÀ-ÿ]*([A-Za-zÀ-ÿ]+)", s)
        if m:
            openers[m.group(1).lower()] += 1
    top_opener_share = round(openers.most_common(1)[0][1] / n_sent, 4) if openers else 0.0

    # leksikal diversity (type-token ratio ternormalisasi per 1000 kata)
    toks = WORD.findall(low)
    ttr = round(len(set(toks[:4000])) / min(len(toks), 4000), 4) if toks else 0.0

    per_sent = lambda x: round(x / n_sent, 4)
    mean_wc = statistics.mean(wc)
    # coefficient of variation: ukuran keseragaman irama, tak bergantung panjang teks
    len_cv = round(statistics.pstdev(wc) / mean_wc, 4) if mean_wc else 0.0
    return {
        "n_sent": n_sent,
        "n_word": n_word,
        "words_per_sent_mean": round(mean_wc, 2),
        "words_per_sent_median": statistics.median(wc),
        "words_per_sent_stdev": round(statistics.pstdev(wc), 2),
        "len_cv": len_cv,
        "padding_per_sent": per_sent(_count_phrases(low, PADDING)),
        "specificity_per_sent": per_sent(len(SPECIFIC.findall(text)) + len(CITATION.findall(text))),
        "len_dist": dist,
        "burstiness": burstiness,
        "commas_per_sent": per_sent(text.count(",")),
        "top_opener_share": top_opener_share,
        "ttr": ttr,
        "formal_conn_per_sent": per_sent(_count_phrases(low, CONNECTIVES_FORMAL)),
        "informal_conn_per_sent": per_sent(_count_phrases(low, CONNECTIVES_INFORMAL)),
        "first_person_per_sent": per_sent(_count_phrases(low, FIRST_PERSON)),
        "passive_per_sent": per_sent(len(PASSIVE.findall(text))),
        "hedge_per_sent": per_sent(_count_phrases(low, HEDGES)),
        "fragment_rate": dist["s1_5"],
    }


# ---- agregasi beberapa dokumen jadi profil ----
AGG_KEYS = [
    "words_per_sent_mean", "words_per_sent_median", "words_per_sent_stdev",
    "len_cv", "burstiness", "commas_per_sent", "top_opener_share", "ttr",
    "formal_conn_per_sent", "informal_conn_per_sent", "first_person_per_sent",
    "passive_per_sent", "hedge_per_sent", "fragment_rate", "padding_per_sent",
    "specificity_per_sent",
]
DIST_KEYS = ["s1_5", "s6_10", "s11_18", "s19_30", "s31p"]


def build_profile(metric_list):
    """Dari list hasil compute_metrics -> profil (mean + stdev tiap metrik)."""
    metric_list = [m for m in metric_list if m]
    if not metric_list:
        return None
    prof = {"n_docs": len(metric_list),
            "total_sent": sum(m["n_sent"] for m in metric_list),
            "total_word": sum(m["n_word"] for m in metric_list)}
    for k in AGG_KEYS:
        vals = [m[k] for m in metric_list]
        prof[k] = {"mean": round(statistics.mean(vals), 4),
                   "stdev": round(statistics.pstdev(vals), 4)}
    dist = {}
    for dk in DIST_KEYS:
        vals = [m["len_dist"][dk] for m in metric_list]
        dist[dk] = {"mean": round(statistics.mean(vals), 4),
                    "stdev": round(statistics.pstdev(vals), 4)}
    prof["len_dist"] = dist
    return prof
