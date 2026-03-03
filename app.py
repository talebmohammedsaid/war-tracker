import re
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
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
        "tab_live": "Live Dashboard",
        "tab_intel": "Risk Intelligence",
        "tab_hotspots": "Hotspots",
        "tab_scenarios": "Scenarios",
        "tab_growth": "Growth",
        "alerts_title": "Realtime Alerts",
        "alerts_enable": "Enable threshold alerts",
        "alerts_threshold": "Risk threshold",
        "alerts_inapp": "In-app alert",
        "alerts_telegram": "Telegram alert",
        "alerts_email": "Email alert",
        "alerts_bot_token": "Telegram bot token",
        "alerts_chat_id": "Telegram chat id",
        "alerts_email_target": "Email target",
        "alerts_email_help": "For email alerts, add SMTP secrets in .streamlit/secrets.toml.",
        "alert_telegram_sent": "Telegram alert sent.",
        "alert_email_sent": "Email alert sent.",
        "data_feed_warn": "Live market feed is temporarily unavailable for:",
        "risk_history_title": "Risk Score History",
        "risk_window": "Window",
        "risk_history_unavailable": "Historical score is unavailable right now.",
        "score_explainability": "Score Explainability",
        "current_score": "Current score",
        "data_reliability": "Data Reliability",
        "hotspots_title": "Geopolitical Hotspots",
        "scenario_comparison": "Scenario Comparison",
        "scenario_label": "Scenario",
        "projected_score": "Projected Score",
        "scenario_escalation": "Escalation",
        "scenario_status_quo": "Status Quo",
        "scenario_deescalation": "De-escalation",
        "custom_scenario": "Custom Scenario",
        "gold_shift": "Gold shift %",
        "oil_shift": "Oil shift %",
        "lmt_shift": "LMT shift %",
        "rtx_shift": "RTX shift %",
        "projected_global_risk": "Projected Global War Risk",
        "growth_title": "Growth & Conversion",
        "premium_signals": "Premium Signals",
        "premium_free": "- Free: live dashboard + daily score",
        "premium_pro": "- Pro: realtime Telegram/Email alerts + scenario exports",
        "premium_enterprise": "- Enterprise: API access + custom watchlists",
        "join_waitlist": "Join Premium Waitlist",
        "newsletter": "Newsletter",
        "subscribe": "Subscribe",
        "invalid_email": "Please enter a valid email.",
        "subscribed_ok": "Subscribed successfully.",
        "col_asset": "Asset",
        "col_name": "Name",
        "col_price": "Price",
        "col_change": "Change %",
        "col_source": "Source",
        "col_market_time": "Market Time",
        "col_freshness": "Freshness",
        "col_status": "Status",
        "status_ok": "OK",
        "status_unavailable": "Unavailable",
        "contrib_gold": "Gold impact",
        "contrib_oil": "Oil impact",
        "contrib_lmt": "LMT impact",
        "contrib_rtx": "RTX impact",
        "contrib_volatility": "Volatility impact",
        "contrib_label": "Contribution",
        "points_label": "Points",
        "hotspot_label": "Hotspot",
        "intensity_label": "Intensity",
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
        "tab_live": "Tableau en Direct",
        "tab_intel": "Intelligence du Risque",
        "tab_hotspots": "Points Chauds",
        "tab_scenarios": "Scenarios",
        "tab_growth": "Croissance",
        "alerts_title": "Alertes Temps Reel",
        "alerts_enable": "Activer les alertes de seuil",
        "alerts_threshold": "Seuil de risque",
        "alerts_inapp": "Alerte dans l'application",
        "alerts_telegram": "Alerte Telegram",
        "alerts_email": "Alerte Email",
        "alerts_bot_token": "Token bot Telegram",
        "alerts_chat_id": "ID chat Telegram",
        "alerts_email_target": "Email cible",
        "alerts_email_help": "Pour les alertes email, ajoutez les secrets SMTP dans .streamlit/secrets.toml.",
        "alert_telegram_sent": "Alerte Telegram envoyee.",
        "alert_email_sent": "Alerte email envoyee.",
        "data_feed_warn": "Flux marche live temporairement indisponible pour :",
        "risk_history_title": "Historique du Score de Risque",
        "risk_window": "Fenetre",
        "risk_history_unavailable": "L'historique du score est indisponible pour le moment.",
        "score_explainability": "Explication du Score",
        "current_score": "Score actuel",
        "data_reliability": "Fiabilite des Donnees",
        "hotspots_title": "Points Chauds Geopolitiques",
        "scenario_comparison": "Comparaison des Scenarios",
        "scenario_label": "Scenario",
        "projected_score": "Score projete",
        "scenario_escalation": "Escalade",
        "scenario_status_quo": "Statu Quo",
        "scenario_deescalation": "Desescalade",
        "custom_scenario": "Scenario Personnalise",
        "gold_shift": "Variation Or %",
        "oil_shift": "Variation Petrole %",
        "lmt_shift": "Variation LMT %",
        "rtx_shift": "Variation RTX %",
        "projected_global_risk": "Risque Global projete",
        "growth_title": "Croissance & Conversion",
        "premium_signals": "Signaux Premium",
        "premium_free": "- Gratuit : tableau live + score quotidien",
        "premium_pro": "- Pro : alertes Telegram/Email en temps reel + exports scenarios",
        "premium_enterprise": "- Entreprise : acces API + listes personnalisees",
        "join_waitlist": "Rejoindre la Liste Premium",
        "newsletter": "Newsletter",
        "subscribe": "S'abonner",
        "invalid_email": "Veuillez saisir un email valide.",
        "subscribed_ok": "Inscription reussie.",
        "col_asset": "Actif",
        "col_name": "Nom",
        "col_price": "Prix",
        "col_change": "Variation %",
        "col_source": "Source",
        "col_market_time": "Heure Marche",
        "col_freshness": "Fraicheur",
        "col_status": "Statut",
        "status_ok": "OK",
        "status_unavailable": "Indisponible",
        "contrib_gold": "Impact Or",
        "contrib_oil": "Impact Petrole",
        "contrib_lmt": "Impact LMT",
        "contrib_rtx": "Impact RTX",
        "contrib_volatility": "Impact Volatilite",
        "contrib_label": "Contribution",
        "points_label": "Points",
        "hotspot_label": "Point Chaud",
        "intensity_label": "Intensite",
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
        "tab_live": "لوحة مباشرة",
        "tab_intel": "تحليل المخاطر",
        "tab_hotspots": "النقاط الساخنة",
        "tab_scenarios": "السيناريوهات",
        "tab_growth": "النمو",
        "alerts_title": "تنبيهات فورية",
        "alerts_enable": "تفعيل تنبيهات العتبة",
        "alerts_threshold": "عتبة المخاطر",
        "alerts_inapp": "تنبيه داخل التطبيق",
        "alerts_telegram": "تنبيه تيليغرام",
        "alerts_email": "تنبيه البريد",
        "alerts_bot_token": "رمز بوت تيليغرام",
        "alerts_chat_id": "معرف محادثة تيليغرام",
        "alerts_email_target": "البريد المستهدف",
        "alerts_email_help": "لتنبيهات البريد اضف اعدادات SMTP داخل .streamlit/secrets.toml.",
        "alert_telegram_sent": "تم ارسال تنبيه تيليغرام.",
        "alert_email_sent": "تم ارسال تنبيه البريد.",
        "data_feed_warn": "تغذية السوق المباشرة غير متاحة مؤقتا لـ:",
        "risk_history_title": "سجل درجة المخاطر",
        "risk_window": "الفترة",
        "risk_history_unavailable": "سجل الدرجات غير متاح حاليا.",
        "score_explainability": "شرح الدرجة",
        "current_score": "الدرجة الحالية",
        "data_reliability": "موثوقية البيانات",
        "hotspots_title": "النقاط الجيوسياسية الساخنة",
        "scenario_comparison": "مقارنة السيناريوهات",
        "scenario_label": "السيناريو",
        "projected_score": "الدرجة المتوقعة",
        "scenario_escalation": "تصعيد",
        "scenario_status_quo": "استقرار",
        "scenario_deescalation": "خفض التصعيد",
        "custom_scenario": "سيناريو مخصص",
        "gold_shift": "تغير الذهب %",
        "oil_shift": "تغير النفط %",
        "lmt_shift": "تغير LMT %",
        "rtx_shift": "تغير RTX %",
        "projected_global_risk": "مخاطر الحرب المتوقعة",
        "growth_title": "النمو والتحويل",
        "premium_signals": "اشارات بريميوم",
        "premium_free": "- مجاني: لوحة مباشرة + درجة يومية",
        "premium_pro": "- برو: تنبيهات فورية Telegram/Email + تصدير السيناريوهات",
        "premium_enterprise": "- مؤسسة: API + قوائم مراقبة مخصصة",
        "join_waitlist": "الانضمام لقائمة بريميوم",
        "newsletter": "النشرة البريدية",
        "subscribe": "اشتراك",
        "invalid_email": "يرجى ادخال بريد صحيح.",
        "subscribed_ok": "تم الاشتراك بنجاح.",
        "col_asset": "الاصل",
        "col_name": "الاسم",
        "col_price": "السعر",
        "col_change": "التغير %",
        "col_source": "المصدر",
        "col_market_time": "وقت السوق",
        "col_freshness": "الحداثة",
        "col_status": "الحالة",
        "status_ok": "متاح",
        "status_unavailable": "غير متاح",
        "contrib_gold": "تأثير الذهب",
        "contrib_oil": "تأثير النفط",
        "contrib_lmt": "تأثير LMT",
        "contrib_rtx": "تأثير RTX",
        "contrib_volatility": "تأثير التقلب",
        "contrib_label": "المساهمة",
        "points_label": "النقاط",
        "hotspot_label": "النقطة الساخنة",
        "intensity_label": "الشدة",
    },
}

ASSETS = {
    "GC=F": "gold",
    "BZ=F": "oil",
    "LMT": "lmt",
    "RTX": "rtx",
}

HOTSPOTS = [
    {"name": "Tehran", "lat": 35.6892, "lon": 51.3890, "keywords": ["iran", "tehran", "israel"]},
    {"name": "Red Sea", "lat": 19.5000, "lon": 40.0000, "keywords": ["red sea", "shipping", "houthi"]},
    {"name": "Strait of Hormuz", "lat": 26.5667, "lon": 56.2500, "keywords": ["hormuz", "gulf", "oil tanker"]},
    {"name": "Washington", "lat": 38.9072, "lon": -77.0369, "keywords": ["sanctions", "pentagon", "white house"]},
]


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def inject_seo_meta(title: str, description: str):
    escaped_title = title.replace('"', "")
    escaped_desc = description.replace('"', "")
    components.html(
        f"""
        <script>
        (function() {{
          var d = (window.parent || window).document;
          d.title = "{escaped_title}";
          function setMeta(attr, key, value) {{
            var selector = "meta[" + attr + "='" + key + "']";
            var el = d.querySelector(selector);
            if (!el) {{
              el = d.createElement("meta");
              el.setAttribute(attr, key);
              d.head.appendChild(el);
            }}
            el.setAttribute("content", value);
          }}
          setMeta("name", "description", "{escaped_desc}");
          setMeta("property", "og:title", "{escaped_title}");
          setMeta("property", "og:description", "{escaped_desc}");
          setMeta("property", "og:type", "website");
        }})();
        </script>
        """,
        height=0,
    )


def send_telegram_alert(bot_token: str, chat_id: str, message: str):
    try:
        url = (
            f"https://api.telegram.org/bot{bot_token}/sendMessage"
            f"?chat_id={quote(chat_id)}&text={quote(message)}"
        )
        urlopen(url, timeout=8).read()
        return True, "Telegram alert sent."
    except URLError as exc:
        return False, f"Telegram error: {exc.reason}"
    except Exception as exc:
        return False, f"Telegram error: {exc}"


def send_email_alert(recipient: str, subject: str, message: str):
    try:
        smtp_host = st.secrets.get("smtp_host", "")
        smtp_port = int(st.secrets.get("smtp_port", 587))
        smtp_user = st.secrets.get("smtp_user", "")
        smtp_pass = st.secrets.get("smtp_pass", "")
        smtp_from = st.secrets.get("smtp_from", smtp_user)
    except Exception:
        smtp_host = ""
        smtp_port = 587
        smtp_user = ""
        smtp_pass = ""
        smtp_from = ""
    if not smtp_host or not smtp_user or not smtp_pass:
        return False, "SMTP secrets missing (smtp_host/smtp_user/smtp_pass)."

    try:
        mail = EmailMessage()
        mail["From"] = smtp_from
        mail["To"] = recipient
        mail["Subject"] = subject
        mail.set_content(message)
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(mail)
        return True, "Email alert sent."
    except Exception as exc:
        return False, f"Email error: {exc}"

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

st.sidebar.markdown(
    f'<span style="color:#22c55e;font-weight:700;">●</span> {t["status_live"]}',
    unsafe_allow_html=True,
)
st.sidebar.caption("Live dashboard updates every 15s without refreshing the full page.")

last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        market_ts = _safe_float(fast_info.get("regularMarketTime"))
        source = "fast_info"

        # Fallback to intraday candles for current price.
        if current is None:
            intraday = ticker.history(period="1d", interval="1m")
            if not intraday.empty:
                close = intraday["Close"].dropna()
                if not close.empty:
                    current = _safe_float(close.iloc[-1])
                    market_ts = datetime.now(timezone.utc).timestamp()
                    source = "intraday_1m"

        # Fallback to daily candles for previous close.
        if prev_close is None:
            daily = ticker.history(period="7d", interval="1d")
            if not daily.empty:
                close = daily["Close"].dropna()
                if len(close) > 1:
                    prev_close = _safe_float(close.iloc[-2])
                    source = "daily_fallback"
                elif len(close) == 1:
                    prev_close = _safe_float(close.iloc[-1])
                    if current is None:
                        current = _safe_float(close.iloc[-1])
                    source = "daily_fallback"

        if current is None or prev_close in (None, 0):
            return None, None, "unavailable", None

        change = ((current - prev_close) / prev_close) * 100
        return current, float(change), source, market_ts
    except Exception:
        return None, None, "error", None


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


def war_risk_breakdown(changes):
    gold = 0.35 * max(0.0, min((changes.get("GC=F") or 0.0), 5.0)) / 5.0
    oil = 0.30 * max(0.0, min((changes.get("BZ=F") or 0.0), 5.0)) / 5.0
    lmt = 0.20 * max(0.0, min((changes.get("LMT") or 0.0), 5.0)) / 5.0
    rtx = 0.15 * max(0.0, min((changes.get("RTX") or 0.0), 5.0)) / 5.0
    vol = 0.2 * (
        min(abs(changes.get("GC=F") or 0.0), 5.0)
        + min(abs(changes.get("BZ=F") or 0.0), 5.0)
        + min(abs(changes.get("LMT") or 0.0), 5.0)
        + min(abs(changes.get("RTX") or 0.0), 5.0)
    ) / (4 * 5.0)
    rows = {
        t["contrib_gold"]: round(gold * 100, 2),
        t["contrib_oil"]: round(oil * 100, 2),
        t["contrib_lmt"]: round(lmt * 100, 2),
        t["contrib_rtx"]: round(rtx * 100, 2),
        t["contrib_volatility"]: round(vol * 100, 2),
    }
    return pd.DataFrame({t["contrib_label"]: list(rows.keys()), t["points_label"]: list(rows.values())})


@st.cache_data(ttl=300)
def fetch_score_history(days: int = 90):
    closes = {}
    for symbol in ASSETS:
        series = yf.Ticker(symbol).history(period=f"{max(days, 30) + 20}d", interval="1d")["Close"].dropna()
        closes[symbol] = series
    close_df = pd.DataFrame(closes).dropna(how="all")
    if close_df.empty:
        return pd.DataFrame(columns=["Date", "Score"])
    change_df = close_df.pct_change() * 100
    change_df = change_df.fillna(0.0)
    scores = change_df.apply(lambda row: war_risk_score(row.to_dict()), axis=1)
    score_df = pd.DataFrame({"Date": scores.index, "Score": scores.values})
    return score_df.tail(days)


def build_hotspot_table(news_items):
    combined = " ".join((f"{x.get('title', '')} {x.get('summary', '')}" for x in news_items)).lower()
    rows = []
    for spot in HOTSPOTS:
        hits = sum(combined.count(keyword) for keyword in spot["keywords"])
        intensity = min(100, hits * 25)
        rows.append(
            {
                t["hotspot_label"]: spot["name"],
                t["intensity_label"]: intensity,
                "Latitude": spot["lat"],
                "Longitude": spot["lon"],
            }
        )
    return pd.DataFrame(rows, columns=[t["hotspot_label"], t["intensity_label"], "Latitude", "Longitude"])


def save_newsletter_lead(email: str):
    leads_path = Path("newsletter_leads.csv")
    if not leads_path.exists():
        leads_path.write_text("timestamp,email\n")
    current = leads_path.read_text()
    leads_path.write_text(current + f"{datetime.now().isoformat()},{email}\n")


def build_live_snapshot():
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changes = {}
    asset_rows = []
    unavailable_assets = []

    for symbol, name_key in ASSETS.items():
        price, change, source, market_ts = fetch_price(symbol)
        changes[symbol] = change or 0.0
        if price is None:
            unavailable_assets.append(symbol)

        market_time_text = t["na"]
        freshness = t["na"]
        if market_ts:
            market_dt = datetime.fromtimestamp(market_ts, tz=timezone.utc)
            market_time_text = market_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            freshness_min = max(0, int((datetime.now(timezone.utc) - market_dt).total_seconds() // 60))
            freshness = f"{freshness_min} min"

        asset_rows.append(
            {
                t["col_asset"]: symbol,
                t["col_name"]: t[name_key],
                t["col_price"]: price if price is not None else t["na"],
                t["col_change"]: round(change, 3) if change is not None else t["na"],
                t["col_source"]: source,
                t["col_market_time"]: market_time_text,
                t["col_freshness"]: freshness,
                t["col_status"]: t["status_ok"] if price is not None else t["status_unavailable"],
            }
        )

    return {
        "updated_at": updated_at,
        "changes": changes,
        "asset_rows": asset_rows,
        "unavailable_assets": unavailable_assets,
        "score": war_risk_score(changes),
        "trend_df": fetch_trend_7d(),
        "intraday": fetch_intraday_24h(),
        "news": fetch_live_news(limit=8),
    }


inject_seo_meta(
    t["title"],
    "Live geopolitical market risk dashboard with realtime score, hotspots, scenarios, and alerts.",
)

if "live_snapshot" not in st.session_state:
    st.session_state["live_snapshot"] = build_live_snapshot()
snapshot = st.session_state["live_snapshot"]
score = snapshot["score"]
changes = snapshot["changes"]
asset_rows = snapshot["asset_rows"]

with st.sidebar.expander(t["alerts_title"], expanded=False):
    alert_enabled = st.toggle(t["alerts_enable"], value=False)
    alert_threshold = st.slider(t["alerts_threshold"], min_value=10, max_value=95, value=70, step=5)
    inapp_alert = st.checkbox(t["alerts_inapp"], value=True)
    tg_alert = st.checkbox(t["alerts_telegram"], value=False)
    em_alert = st.checkbox(t["alerts_email"], value=False)
    tg_token = st.text_input(t["alerts_bot_token"], type="password")
    tg_chat_id = st.text_input(t["alerts_chat_id"])
    email_target = st.text_input(t["alerts_email_target"])
    st.caption(t["alerts_email_help"])

tabs = st.tabs([t["tab_live"], t["tab_intel"], t["tab_hotspots"], t["tab_scenarios"], t["tab_growth"]])

with tabs[0]:
    @st.fragment(run_every=15)
    def render_live_dashboard():
        live = build_live_snapshot()
        st.session_state["live_snapshot"] = live

        st.markdown(
            f'<div class="update-chip">{t["last_updated"]}: {live["updated_at"]}</div>',
            unsafe_allow_html=True,
        )
        st.subheader(t["financial_engine"])
        metric_cols = st.columns(4)
        for col, (symbol, name_key) in zip(metric_cols, ASSETS.items()):
            row = next((x for x in live["asset_rows"] if x[t["col_asset"]] == symbol), None)
            if not row or row[t["col_price"]] == t["na"]:
                col.metric(t[name_key], t["na"], t["na"])
            else:
                col.metric(t[name_key], f"{row[t['col_price']]:,.2f}", f"{row[t['col_change']]:+.2f}%")

        prev_above = st.session_state.get("risk_prev_above", False)
        is_above = live["score"] >= alert_threshold
        if alert_enabled and is_above and not prev_above:
            alert_msg = f"{t['risk_title']}: {live['score']}/100 at {live['updated_at']}"
            if inapp_alert:
                st.toast(alert_msg)
            if tg_alert and tg_token and tg_chat_id:
                ok, msg = send_telegram_alert(tg_token, tg_chat_id, alert_msg)
                if not ok:
                    st.sidebar.error(msg)
                else:
                    st.sidebar.success(t["alert_telegram_sent"])
            if em_alert and email_target:
                ok, msg = send_email_alert(email_target, "Global War Risk Alert", alert_msg)
                if not ok:
                    st.sidebar.error(msg)
                else:
                    st.sidebar.success(t["alert_email_sent"])
        st.session_state["risk_prev_above"] = is_above

        if live["unavailable_assets"]:
            st.warning(t["data_feed_warn"] + " " + ", ".join(live["unavailable_assets"]) + ".")

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

        if (live["changes"].get("GC=F", 0) > 0) and (live["changes"].get("LMT", 0) > 0) and (live["changes"].get("RTX", 0) > 0):
            st.markdown(f'<div class="alert-card">{t["war_hedge_msg"]}</div>', unsafe_allow_html=True)

        st.subheader(t["clock_title"])
        clock_cols = st.columns(3)
        clock_cols[0].metric(t["clock_tehran"], datetime.now(ZoneInfo("Asia/Tehran")).strftime("%H:%M:%S"))
        clock_cols[1].metric(t["clock_washington"], datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M:%S"))
        clock_cols[2].metric(t["clock_algiers"], datetime.now(ZoneInfo("Africa/Algiers")).strftime("%H:%M:%S"))

        st.subheader(t["risk_title"])
        if go is not None:
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=live["score"],
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
            st.plotly_chart(fig)
        else:
            st.progress(int(live["score"]))
            st.caption(f'{live["score"]}/100')

        st.subheader(t["summary_title"])
        st.info(build_market_summary(live["changes"]))
        st.subheader(t["correlation_title"])
        st.warning(build_correlation(live["changes"]))

        st.subheader(t["charts_title"])
        if not live["trend_df"].empty:
            st.line_chart(live["trend_df"])

        st.subheader(t["intraday_title"])
        row_cols = st.columns(2)
        for i, (symbol, name_key) in enumerate(ASSETS.items()):
            with row_cols[i % 2]:
                st.markdown(f"**{t[name_key]} ({symbol})**")
                series = live["intraday"].get(symbol)
                if series is not None and not series.empty:
                    st.line_chart(series)

        st.markdown(
            f'<h3 style="margin-top:0.5rem;"><span class="live-dot"></span>{t["news_title"]}</h3>',
            unsafe_allow_html=True,
        )
        if not live["news"]:
            st.info(t["news_empty"])
        else:
            st.subheader(t["ai_summary_title"])
            for line in build_ai_summary(live["news"]):
                st.markdown(line)
            st.divider()
            for item in live["news"]:
                st.markdown(f"**[{item['title']}]({item['link']})**")
                st.caption(f"{t['article_date']}: {item.get('date') or t['date_unknown']}")
                st.caption(item["summary"])
                st.markdown(f"[{t['read_original']}]({item['link']})")

    render_live_dashboard()

with tabs[1]:
    latest = st.session_state.get("live_snapshot", snapshot)
    st.subheader(t["risk_history_title"])
    history_window = st.radio(t["risk_window"], options=[7, 30, 90], horizontal=True)
    history_df = fetch_score_history(history_window)
    if history_df.empty:
        st.info(t["risk_history_unavailable"])
    else:
        st.line_chart(history_df.set_index("Date")["Score"])

    st.subheader(t["score_explainability"])
    breakdown_df = war_risk_breakdown(latest["changes"])
    st.bar_chart(breakdown_df.set_index(t["contrib_label"])[t["points_label"]])
    st.caption(f"{t['current_score']}: {latest['score']}/100")

    st.subheader(t["data_reliability"])
    reliability_df = pd.DataFrame(latest["asset_rows"])
    st.dataframe(reliability_df, width="stretch", hide_index=True)

with tabs[2]:
    st.subheader(t["hotspots_title"])
    latest = st.session_state.get("live_snapshot", snapshot)
    news_for_hotspots = latest["news"] if latest["news"] else fetch_live_news(limit=12)
    hotspot_df = build_hotspot_table(news_for_hotspots)
    if go is not None and not hotspot_df.empty:
        geo = go.Figure(
            go.Scattergeo(
                lon=hotspot_df["Longitude"],
                lat=hotspot_df["Latitude"],
                text=hotspot_df[t["hotspot_label"]] + " | " + t["intensity_label"] + ": " + hotspot_df[t["intensity_label"]].astype(str),
                mode="markers+text",
                textposition="top center",
                marker=dict(
                    size=[8 + int(v / 6) for v in hotspot_df[t["intensity_label"]]],
                    color=hotspot_df[t["intensity_label"]],
                    colorscale="Reds",
                    cmin=0,
                    cmax=100,
                    showscale=True,
                    colorbar=dict(title=t["intensity_label"]),
                ),
            )
        )
        geo.update_layout(geo=dict(showland=True, landcolor="#111827", bgcolor="#0b1220"), height=500)
        st.plotly_chart(geo)
    st.dataframe(hotspot_df[[t["hotspot_label"], t["intensity_label"]]], width="stretch", hide_index=True)

with tabs[3]:
    st.subheader(t["scenario_comparison"])
    latest = st.session_state.get("live_snapshot", snapshot)
    base = latest["changes"].copy()
    presets = {
        t["scenario_escalation"]: {"GC=F": 2.0, "BZ=F": 3.0, "LMT": 1.5, "RTX": 1.2},
        t["scenario_status_quo"]: {"GC=F": 0.2, "BZ=F": 0.2, "LMT": 0.1, "RTX": 0.1},
        t["scenario_deescalation"]: {"GC=F": -1.5, "BZ=F": -2.0, "LMT": -1.0, "RTX": -0.8},
    }
    scenario_rows = []
    for name, deltas in presets.items():
        hypothetical = {k: (base.get(k, 0.0) + deltas.get(k, 0.0)) for k in ASSETS}
        scenario_rows.append({t["scenario_label"]: name, t["projected_score"]: war_risk_score(hypothetical)})
    st.dataframe(pd.DataFrame(scenario_rows), width="stretch", hide_index=True)

    st.subheader(t["custom_scenario"])
    c1, c2 = st.columns(2)
    with c1:
        d_gold = st.slider(t["gold_shift"], -5.0, 5.0, 0.0, 0.1)
        d_oil = st.slider(t["oil_shift"], -5.0, 5.0, 0.0, 0.1)
    with c2:
        d_lmt = st.slider(t["lmt_shift"], -5.0, 5.0, 0.0, 0.1)
        d_rtx = st.slider(t["rtx_shift"], -5.0, 5.0, 0.0, 0.1)
    custom = {
        "GC=F": base.get("GC=F", 0.0) + d_gold,
        "BZ=F": base.get("BZ=F", 0.0) + d_oil,
        "LMT": base.get("LMT", 0.0) + d_lmt,
        "RTX": base.get("RTX", 0.0) + d_rtx,
    }
    st.metric(t["projected_global_risk"], f"{war_risk_score(custom)}/100")

with tabs[4]:
    st.subheader(t["growth_title"])
    st.markdown(f"### {t['premium_signals']}")
    st.write(t["premium_free"])
    st.write(t["premium_pro"])
    st.write(t["premium_enterprise"])
    st.link_button(t["join_waitlist"], "mailto:contact@example.com?subject=Premium%20Waitlist")

    st.markdown(f"### {t['newsletter']}")
    with st.form("newsletter_form", clear_on_submit=True):
        lead_email = st.text_input(t["newsletter"])
        submit_lead = st.form_submit_button(t["subscribe"])
        if submit_lead:
            if "@" not in lead_email:
                st.error(t["invalid_email"])
            else:
                save_newsletter_lead(lead_email.strip())
                st.success(t["subscribed_ok"])

latest_for_share = st.session_state.get("live_snapshot", snapshot)
tweet_text = (
    f"{t['title']} | {t['score_label']} {latest_for_share['score']}/100 | "
    f"{build_correlation(latest_for_share['changes'])} | "
    f"{t['last_updated']}: {latest_for_share['updated_at']}"
)
tweet_url = f"https://x.com/intent/tweet?text={quote(tweet_text)}"
st.link_button(t["share_x"], tweet_url)

st.sidebar.markdown('<div class="support-card">', unsafe_allow_html=True)
st.sidebar.markdown(f"**{t['developer_support']}**")
st.sidebar.markdown(t["support_pitch"])
st.sidebar.write(f"**{t['binance_pay_id']}:** `{BINANCE_PAY_ID}`")
if st.sidebar.button(t["copy_id"], width="stretch"):
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
