import re
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

import feedparser
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(*args, **kwargs):
        return 0


BINANCE_BONUS_LINK = "https://www.binance.com/referral/earn-together/refer2earn-usdc/claim?hl=fr&ref=GRO_28502_CSMIX&utm_source=default"
BINANCE_PAY_ID = "536502443"
GTM_ID = "GTM-MF2BVNDS"
GA_MEASUREMENT_ID = "G-RNGVHQ92XF"

TRANSLATIONS = {
    "EN": {
        "title": "Global Geopolitical Market Monitor",
        "language": "Language",
        "autorefresh": "Auto-refresh (60s)",
        "last_updated": "Last Updated",
        "financial_engine": "Financial Engine",
        "charts_title": "Market Trend (7D)",
        "intraday_title": "24H Movement by Asset",
        "news_title": "Live War News",
        "news_empty": "No live headlines available right now.",
        "summary_title": "Market Summary",
        "correlation_title": "Correlation Insight",
        "war_hedge_msg": "Market Sentiment: War Hedging Active",
        "corr_war_hedge": "⚠️ War Hedge Mode: Investors are pricing in a major escalation.",
        "corr_uncertainty": "🔍 Uncertainty Mode: Markets are confused, but safe-haven buying persists.",
        "corr_none": "No strong hedge correlation signal detected at this time.",
        "ai_summary_title": "AI Summary",
        "risk_title": "Global War Risk",
        "clock_title": "Global Clock Bar",
        "share_x": "Share on X",
        "status_live": "Live Data Connection: Active",
        "read_original": "Read original article",
        "article_date": "Published",
        "date_unknown": "Unknown date",
        "developer_support": "Developer Support",
        "binance_pay_id": "Binance Pay ID",
        "copy_id": "Copy ID",
        "copy_done": "Binance Pay ID shown below for copy.",
        "score_label": "Score",
        "hotzone_title": "🎁 LIMITED OFFER: CLAIM YOUR 100 USDC",
        "hotzone_text": "The market is volatile! Secure your assets on Binance and receive a 100 USDC welcome bonus using our official link.",
        "hotzone_button": "START TRADING & CLAIM BONUS",
        "support_pitch": "🚀 **Help us grow this project!**\n\nEvery donation improves features, live data speed, and analysis quality.",
        "clock_tehran": "Tehran",
        "clock_washington": "Washington",
        "clock_algiers": "Algiers",
        "summary_gold_oil": "Gold and oil are rising together, showing broad risk-driven demand.",
        "summary_defense": "Defense names are leading, signaling heightened geopolitical stress.",
        "summary_gold": "Gold remains firm, reflecting safe-haven positioning.",
        "summary_mixed": "Cross-asset signals are mixed for now.",
        "ai_b1_high": "- Security headlines point to elevated conflict risk.",
        "ai_b1_low": "- No dominant military flashpoint in top headlines.",
        "ai_b2_yes": "- Diplomatic language remains present, leaving room for de-escalation.",
        "ai_b2_no": "- Diplomatic progress appears limited in the latest cycle.",
        "ai_b3_yes": "- Market-sensitive geopolitical signals remain active.",
        "ai_b3_no": "- Investors likely stay defensive until clarity improves.",
        "na": "N/A",
        "untitled": "Untitled",
        "footer": "Built by an Independent Developer. Data provided for educational purposes only. Not financial advice.",
        "gold": "Gold",
        "oil": "Brent Oil",
        "lmt": "Lockheed Martin",
        "rtx": "RTX Corporation",
    },
    "FR": {
        "title": "Moniteur Global des Marches Geopolitiques",
        "language": "Langue",
        "autorefresh": "Actualisation auto (60s)",
        "last_updated": "Derniere mise a jour",
        "financial_engine": "Moteur Financier",
        "charts_title": "Tendance du Marche (7J)",
        "intraday_title": "Mouvement 24H par Actif",
        "news_title": "Actualites de Guerre en Direct",
        "news_empty": "Aucun titre en direct disponible pour le moment.",
        "summary_title": "Resume du Marche",
        "correlation_title": "Apercu de Correlation",
        "war_hedge_msg": "Sentiment du Marche: Couverture de Guerre Active",
        "corr_war_hedge": "⚠️ Mode Couverture de Guerre: Les investisseurs anticipent une escalation majeure.",
        "corr_uncertainty": "🔍 Mode Incertitude: Les marches sont confus, mais l'achat de valeurs refuges persiste.",
        "corr_none": "Aucun signal fort de correlation de couverture detecte pour le moment.",
        "ai_summary_title": "Resume IA",
        "risk_title": "Risque Global de Guerre",
        "clock_title": "Barre Horloge Mondiale",
        "share_x": "Partager sur X",
        "status_live": "Connexion Donnees Live: Active",
        "read_original": "Lire l'article original",
        "article_date": "Date",
        "date_unknown": "Date inconnue",
        "developer_support": "Support Developpeur",
        "binance_pay_id": "ID Binance Pay",
        "copy_id": "Copier ID",
        "copy_done": "ID Binance Pay affiche ci-dessous pour copie.",
        "score_label": "Score",
        "hotzone_title": "🎁 OFFRE LIMITEE : RECUPEREZ VOS 100 USDC",
        "hotzone_text": "Le marche est volatil ! Securisez vos actifs sur Binance et recevez un bonus de bienvenue de 100 USDC en utilisant notre lien officiel.",
        "hotzone_button": "COMMENCER A TRADER & RECUPERER LE BONUS",
        "support_pitch": "🚀 **Aidez-nous a faire grandir ce projet !**\n\nChaque don ameliore les fonctionnalites, la vitesse des donnees live et la qualite de l'analyse.",
        "clock_tehran": "Teheran",
        "clock_washington": "Washington",
        "clock_algiers": "Alger",
        "summary_gold_oil": "L'or et le petrole montent ensemble, ce qui montre une demande large liee au risque.",
        "summary_defense": "Les valeurs de defense dominent, signalant une tension geopolitique elevee.",
        "summary_gold": "L'or reste solide, reflet d'un positionnement refuge.",
        "summary_mixed": "Les signaux inter-marches sont mitiges pour le moment.",
        "ai_b1_high": "- Les titres de securite indiquent un risque de conflit eleve.",
        "ai_b1_low": "- Aucun point chaud militaire dominant dans les principaux titres.",
        "ai_b2_yes": "- Le langage diplomatique reste present, laissant une marge de desescalade.",
        "ai_b2_no": "- Les progres diplomatiques semblent limites sur ce cycle.",
        "ai_b3_yes": "- Les signaux geopolitico-economiques sensibles au marche restent actifs.",
        "ai_b3_no": "- Les investisseurs devraient rester defensifs jusqu'a plus de clarte.",
        "na": "N/A",
        "untitled": "Sans titre",
        "footer": "Construit par un developpeur independant. Donnees fournies a des fins educatives uniquement. Pas un conseil financier.",
        "gold": "Or",
        "oil": "Petrole Brent",
        "lmt": "Lockheed Martin",
        "rtx": "RTX Corporation",
    },
    "AR": {
        "title": "لوحة مراقبة السوق الجيوسياسي العالمية",
        "language": "اللغة",
        "autorefresh": "تحديث تلقائي (60 ثانية)",
        "last_updated": "آخر تحديث",
        "financial_engine": "المحرك المالي",
        "charts_title": "اتجاه السوق (7 ايام)",
        "intraday_title": "حركة 24 ساعة لكل اصل",
        "news_title": "اخر اخبار الحرب",
        "news_empty": "لا توجد عناوين مباشرة متاحة حاليا.",
        "summary_title": "ملخص السوق",
        "correlation_title": "رؤية الارتباط",
        "war_hedge_msg": "معنويات السوق: تفعيل التحوط من الحرب",
        "corr_war_hedge": "⚠️ وضع التحوط من الحرب: المستثمرون يسعرون تصعيدا كبيرا.",
        "corr_uncertainty": "🔍 وضع عدم اليقين: الاسواق مرتبكة لكن شراء الملاذات الآمنة مستمر.",
        "corr_none": "لا توجد حاليا اشارة ارتباط قوية للتحوط.",
        "ai_summary_title": "ملخص الذكاء الاصطناعي",
        "risk_title": "مخاطر الحرب العالمية",
        "clock_title": "شريط التوقيت العالمي",
        "share_x": "مشاركة على X",
        "status_live": "اتصال البيانات المباشر: نشط",
        "read_original": "قراءة المقال الاصلي",
        "article_date": "التاريخ",
        "date_unknown": "تاريخ غير متوفر",
        "developer_support": "دعم المطور",
        "binance_pay_id": "معرف Binance Pay",
        "copy_id": "نسخ المعرف",
        "copy_done": "تم عرض معرف Binance Pay بالاسفل للنسخ.",
        "score_label": "النتيجة",
        "hotzone_title": "🎁 عرض محدود: احصل على 100 USDC",
        "hotzone_text": "السوق متقلب! امن اصولك على Binance واحصل على مكافاة ترحيب 100 USDC عبر رابطنا الرسمي.",
        "hotzone_button": "ابدأ التداول واستلم المكافاة",
        "support_pitch": "🚀 **ساعدنا على تطوير هذا المشروع!**\n\nكل تبرع يحسن الميزات وسرعة البيانات المباشرة وجودة التحليل.",
        "clock_tehran": "طهران",
        "clock_washington": "واشنطن",
        "clock_algiers": "الجزائر",
        "summary_gold_oil": "ارتفاع الذهب والنفط معا يعكس طلبا واسعا مدفوعا بالمخاطر.",
        "summary_defense": "اسهم الدفاع تقود السوق، ما يشير الى توتر جيوسياسي مرتفع.",
        "summary_gold": "الذهب متماسك، ما يعكس توجها نحو الملاذات الآمنة.",
        "summary_mixed": "اشارات الاصول متباينة حاليا.",
        "ai_b1_high": "- عناوين الامن تشير الى ارتفاع مخاطر الصراع.",
        "ai_b1_low": "- لا توجد بؤرة عسكرية مهيمنة في ابرز العناوين.",
        "ai_b2_yes": "- الخطاب الدبلوماسي ما زال حاضرا، ما يترك مجالا لخفض التصعيد.",
        "ai_b2_no": "- التقدم الدبلوماسي يبدو محدودا في الدورة الحالية.",
        "ai_b3_yes": "- الاشارات الجيوسياسية الحساسة للسوق ما تزال نشطة.",
        "ai_b3_no": "- من المرجح ان يبقى المستثمرون في وضع دفاعي حتى تتضح الصورة.",
        "na": "غير متاح",
        "untitled": "بدون عنوان",
        "footer": "تم بناء هذا المشروع بواسطة مطور مستقل. البيانات مقدمة لاغراض تعليمية فقط. وليست نصيحة مالية.",
        "gold": "الذهب",
        "oil": "نفط برنت",
        "lmt": "لوكهيد مارتن",
        "rtx": "شركة RTX",
    },
}

ASSETS = {
    "GC=F": "gold",
    "BZ=F": "oil",
    "LMT": "lmt",
    "RTX": "rtx",
}


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

st.set_page_config(page_title="Global War Economy Dashboard", layout="wide")

components.html(
    f"""
    <!-- Google Tag Manager -->
    <script>
    (function() {{
      var GTM_ID = "{GTM_ID}";
      var w = window.parent || window;
      var d = w.document;
      var l = "dataLayer";

      w[l] = w[l] || [];
      w[l].push({{ "gtm.start": new Date().getTime(), event: "gtm.js" }});

      if (!d.getElementById("gtm-loader-" + GTM_ID)) {{
        var j = d.createElement("script");
        j.id = "gtm-loader-" + GTM_ID;
        j.async = true;
        j.src = "https://www.googletagmanager.com/gtm.js?id=" + GTM_ID;
        (d.head || d.documentElement).appendChild(j);
      }}

      // Optional helper for tools expecting gtag on parent window.
      if (!w.gtag) {{
        w.gtag = function() {{ w[l].push(arguments); }};
      }}
      w.gtag("js", new Date());
    }})();
    </script>
    <!-- End Google Tag Manager -->
    """,
    height=0,
)

components.html(
    f"""
    <!-- Google tag (gtag.js) -->
    <script>
    (function() {{
      var GA_ID = "{GA_MEASUREMENT_ID}";
      var w = window.parent || window;
      var d = w.document;

      if (!d.getElementById("ga-gtag-src-" + GA_ID)) {{
        var s = d.createElement("script");
        s.id = "ga-gtag-src-" + GA_ID;
        s.async = true;
        s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
        (d.head || d.documentElement).appendChild(s);
      }}

      w.dataLayer = w.dataLayer || [];
      w.gtag = w.gtag || function() {{ w.dataLayer.push(arguments); }};
      w.gtag("js", new Date());
      w.gtag("config", GA_ID);
    }})();
    </script>
    <!-- End Google tag (gtag.js) -->
    """,
    height=0,
)

components.html(
    f"""
    <!-- Google Tag Manager (noscript) -->
    <script>
    (function() {{
      var GTM_ID = "{GTM_ID}";
      var w = window.parent || window;
      var d = w.document;
      if (!d.getElementById("gtm-noscript-" + GTM_ID)) {{
        var iframe = d.createElement("iframe");
        iframe.id = "gtm-noscript-" + GTM_ID;
        iframe.src = "https://www.googletagmanager.com/ns.html?id=" + GTM_ID;
        iframe.height = "0";
        iframe.width = "0";
        iframe.style.display = "none";
        iframe.style.visibility = "hidden";
        (d.body || d.documentElement).appendChild(iframe);
      }}
    }})();
    </script>
    <!-- End Google Tag Manager (noscript) -->
    """,
    height=0,
)

st.markdown(
    """
    <style>
      .bonus-card {
        background: linear-gradient(135deg, #2f2400 0%, #8a6b00 100%);
        border: 1px solid #f4c430;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0 14px 0;
      }
      .support-card {
        background: #151515;
        border: 1px solid #3b3b3b;
        border-radius: 12px;
        padding: 12px;
      }
      .binance-main-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background: #f0b90b;
        color: #1a1a1a !important;
        font-weight: 800;
        font-size: 1rem;
        padding: 14px 16px;
        border-radius: 10px;
        text-decoration: none;
        margin-top: 8px;
      }
      .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ff3b30;
        display: inline-block;
        margin-right: 6px;
        animation: blink-red 1s infinite;
      }
      @keyframes blink-red {
        0% { opacity: 1; }
        50% { opacity: 0.25; }
        100% { opacity: 1; }
      }
      .alert-card {
        background: #2b0f13;
        border-left: 4px solid #ff4d4f;
        border-radius: 10px;
        padding: 10px 12px;
      }
      .update-chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 8px;
        background: #1d1d1d;
        border: 1px solid #3d3d3d;
        font-size: 0.9rem;
        margin-bottom: 10px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

lang_code = st.sidebar.selectbox("Language / Langue / اللغة", ["EN", "FR", "AR"])
t = TRANSLATIONS[lang_code]

auto_refresh = st.sidebar.toggle(t["autorefresh"], value=True)
if auto_refresh:
    st_autorefresh(interval=60_000, key="refresh")
st.sidebar.markdown(
    f'<span style="color:#22c55e;font-weight:700;">●</span> {t["status_live"]}',
    unsafe_allow_html=True,
)

last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f'<div class="update-chip">{t["last_updated"]}: {last_updated}</div>', unsafe_allow_html=True)
st.title(t["title"])


@st.cache_data(ttl=15)
def fetch_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)

        # First try fast quote fields (lowest latency path in yfinance).
        fast_info = {}
        try:
            fast_info = ticker.fast_info or {}
        except Exception:
            fast_info = {}

        current = _safe_float(fast_info.get("lastPrice") or fast_info.get("regularMarketPrice"))
        prev_close = _safe_float(fast_info.get("previousClose"))

        # Fallback to intraday candles for current price.
        if current is None:
            intraday = ticker.history(period="1d", interval="1m")
            if not intraday.empty:
                close = intraday["Close"].dropna()
                if not close.empty:
                    current = _safe_float(close.iloc[-1])

        # Fallback to daily candles for previous close.
        if prev_close is None:
            daily = ticker.history(period="7d", interval="1d")
            if not daily.empty:
                close = daily["Close"].dropna()
                if len(close) > 1:
                    prev_close = _safe_float(close.iloc[-2])
                elif len(close) == 1:
                    prev_close = _safe_float(close.iloc[-1])
                    if current is None:
                        current = _safe_float(close.iloc[-1])

        if current is None or prev_close in (None, 0):
            return None, None

        change = ((current - prev_close) / prev_close) * 100
        return current, float(change)
    except Exception:
        return None, None


@st.cache_data(ttl=120)
def fetch_trend_7d():
    data = {}
    for symbol, _ in ASSETS.items():
        series = yf.Ticker(symbol).history(period="7d", interval="1d")["Close"].dropna()
        data[symbol] = series
    return pd.DataFrame(data).dropna(how="all")


@st.cache_data(ttl=120)
def fetch_intraday_24h():
    data = {}
    for symbol in ASSETS.keys():
        series = yf.Ticker(symbol).history(period="1d", interval="60m")["Close"].dropna()
        if not series.empty:
            try:
                series.index = series.index.tz_localize(None)
            except TypeError:
                pass
        data[symbol] = series
    return data


@st.cache_data(ttl=180)
def fetch_live_news(limit: int = 5):
    def parse_entry_date(entry):
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if parsed:
            return datetime(*parsed[:6]).strftime("%Y-%m-%d %H:%M")
        text = entry.get("published") or entry.get("updated") or ""
        return text.strip() if text else None

    items = []
    seen = set()
    reuters = feedparser.parse("https://feeds.reuters.com/Reuters/worldNews")

    for entry in reuters.entries:
        title = entry.get("title", "")
        summary = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()
        link = entry.get("link", "")
        text = f"{title} {summary}".lower()
        if not link or link in seen:
            continue
        if "iran" not in text and "conflict" not in text:
            continue
        items.append(
            {"title": title, "summary": summary[:180], "link": link, "date": parse_entry_date(entry)}
        )
        seen.add(link)
        if len(items) >= limit:
            return items

    gnews = feedparser.parse("https://news.google.com/rss/search?q=Iran+Conflict&hl=en-US&gl=US&ceid=US:en")
    for entry in gnews.entries:
        link = entry.get("link", "")
        if not link or link in seen:
            continue
        title = entry.get("title", t["untitled"])
        summary = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()
        items.append(
            {"title": title, "summary": summary[:180], "link": link, "date": parse_entry_date(entry)}
        )
        seen.add(link)
        if len(items) >= limit:
            break

    return items


def build_market_summary(changes):
    gold_up = (changes.get("GC=F") or 0) > 0
    oil_up = (changes.get("BZ=F") or 0) > 0
    lmt_up = (changes.get("LMT") or 0) > 0
    rtx_up = (changes.get("RTX") or 0) > 0
    if gold_up and lmt_up and rtx_up:
        return t["war_hedge_msg"]
    if gold_up and oil_up:
        return t["summary_gold_oil"]
    if lmt_up or rtx_up:
        return t["summary_defense"]
    if gold_up:
        return t["summary_gold"]
    return t["summary_mixed"]


def build_correlation(changes):
    oil_up = (changes.get("BZ=F") or 0) > 0
    oil_down = (changes.get("BZ=F") or 0) < 0
    gold_up = (changes.get("GC=F") or 0) > 0
    lmt_up = (changes.get("LMT") or 0) > 0
    if oil_up and lmt_up:
        return t["corr_war_hedge"]
    if oil_down and gold_up:
        return t["corr_uncertainty"]
    return t["corr_none"]


def build_ai_summary(news_items):
    joined = " ".join((x.get("title", "") for x in news_items[:5])).lower()
    bullets = []
    if any(w in joined for w in ["attack", "explosion", "missile", "closure"]):
        bullets.append(t["ai_b1_high"])
    else:
        bullets.append(t["ai_b1_low"])
    if any(w in joined for w in ["talks", "ceasefire", "diplomat", "negotiation"]):
        bullets.append(t["ai_b2_yes"])
    else:
        bullets.append(t["ai_b2_no"])
    if any(w in joined for w in ["oil", "market", "sanction", "shipping"]):
        bullets.append(t["ai_b3_yes"])
    else:
        bullets.append(t["ai_b3_no"])
    return bullets


def war_risk_score(changes):
    def clamp_pct(value, cap=5.0):
        return max(0.0, min((value or 0.0), cap)) / cap

    def clamp_abs(value, cap=5.0):
        return min(abs(value or 0.0), cap) / cap

    # Up-moves in hedging assets drive the risk signal.
    hedge_signal = (
        0.35 * clamp_pct(changes.get("GC=F"))
        + 0.30 * clamp_pct(changes.get("BZ=F"))
        + 0.20 * clamp_pct(changes.get("LMT"))
        + 0.15 * clamp_pct(changes.get("RTX"))
    )

    # Absolute movement keeps signal responsive during mixed sessions.
    volatility_signal = (
        clamp_abs(changes.get("GC=F"))
        + clamp_abs(changes.get("BZ=F"))
        + clamp_abs(changes.get("LMT"))
        + clamp_abs(changes.get("RTX"))
    ) / 4

    score = ((0.8 * hedge_signal) + (0.2 * volatility_signal)) * 100
    return max(0, min(100, round(score, 1)))


st.subheader(t["financial_engine"])
metric_cols = st.columns(4)
changes = {}
unavailable_assets = []

for col, (symbol, name_key) in zip(metric_cols, ASSETS.items()):
    price, change = fetch_price(symbol)
    changes[symbol] = change or 0.0
    if price is None:
        col.metric(t[name_key], t["na"], t["na"])
        unavailable_assets.append(symbol)
    else:
        col.metric(t[name_key], f"{price:,.2f}", f"{change:+.2f}%")

if unavailable_assets:
    st.warning(
        "Live market feed is temporarily unavailable for: "
        + ", ".join(unavailable_assets)
        + "."
    )

with st.container():
    st.markdown(
        f"""
        <div class="bonus-card">
          <h3 style="margin:0 0 8px 0; color:#ffd24d;">{t["hotzone_title"]}</h3>
          <p style="margin:0 0 6px 0; color:#f7f7f7;">
            {t["hotzone_text"]}
          </p>
          <a class="binance-main-btn" href="{BINANCE_BONUS_LINK}" target="_blank">
            {t["hotzone_button"]}
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

if (changes.get("GC=F", 0) > 0) and (changes.get("LMT", 0) > 0) and (changes.get("RTX", 0) > 0):
    st.markdown(f'<div class="alert-card">{t["war_hedge_msg"]}</div>', unsafe_allow_html=True)

st.subheader(t["clock_title"])
clock_cols = st.columns(3)
clock_cols[0].metric(t["clock_tehran"], datetime.now(ZoneInfo("Asia/Tehran")).strftime("%H:%M:%S"))
clock_cols[1].metric(t["clock_washington"], datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M:%S"))
clock_cols[2].metric(t["clock_algiers"], datetime.now(ZoneInfo("Africa/Algiers")).strftime("%H:%M:%S"))

score = war_risk_score(changes)
st.subheader(t["risk_title"])
if go is not None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#f4c430"},
                "steps": [
                    {"range": [0, 35], "color": "#123524"},
                    {"range": [35, 70], "color": "#5f4500"},
                    {"range": [70, 100], "color": "#5c1010"},
                ],
            },
        )
    )
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.progress(int(score))
    st.caption(f"{score}/100")

st.subheader(t["summary_title"])
st.info(build_market_summary(changes))

st.subheader(t["correlation_title"])
st.warning(build_correlation(changes))

st.subheader(t["charts_title"])
trend_df = fetch_trend_7d()
if not trend_df.empty:
    st.line_chart(trend_df)

st.subheader(t["intraday_title"])
intraday = fetch_intraday_24h()
row_cols = st.columns(2)
for i, (symbol, name_key) in enumerate(ASSETS.items()):
    with row_cols[i % 2]:
        st.markdown(f"**{t[name_key]} ({symbol})**")
        series = intraday.get(symbol)
        if series is not None and not series.empty:
            st.line_chart(series)

st.markdown(
    f'<h3 style="margin-top:0.5rem;"><span class="live-dot"></span>{t["news_title"]}</h3>',
    unsafe_allow_html=True,
)
news = fetch_live_news(limit=5)
if not news:
    st.info(t["news_empty"])
else:
    st.subheader(t["ai_summary_title"])
    for line in build_ai_summary(news):
        st.markdown(line)
    st.divider()
    for item in news:
        st.markdown(f"**[{item['title']}]({item['link']})**")
        st.caption(f"{t['article_date']}: {item.get('date') or t['date_unknown']}")
        st.caption(item["summary"])
        st.markdown(f"[{t['read_original']}]({item['link']})")

tweet_text = f"{t['title']} | {t['score_label']} {score}/100 | {build_correlation(changes)} | {t['last_updated']}: {last_updated}"
tweet_url = f"https://x.com/intent/tweet?text={quote(tweet_text)}"
st.link_button(t["share_x"], tweet_url)

st.sidebar.markdown('<div class="support-card">', unsafe_allow_html=True)
st.sidebar.markdown(f"**{t['developer_support']}**")
st.sidebar.markdown(t["support_pitch"])
st.sidebar.write(f"**{t['binance_pay_id']}:** `{BINANCE_PAY_ID}`")
if st.sidebar.button(t["copy_id"], use_container_width=True):
    st.sidebar.success(t["copy_done"])
st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div style="margin-top: 24px; font-size: 0.82rem; opacity: 0.8; border-top: 1px solid #303030; padding-top: 12px;">
      {t['footer']}
    </div>
    """,
    unsafe_allow_html=True,
)
