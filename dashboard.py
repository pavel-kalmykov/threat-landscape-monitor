import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from google.cloud import bigquery

st.set_page_config(page_title="Threat Landscape Monitor", layout="wide")

# =============================================================================
# THEME
# =============================================================================

ACCENT_RED = "#cf222e"
ACCENT_BLUE = "#2f81f7"
ACCENT_ORANGE = "#f0883e"

THEMES = {
    "dark": {
        "bg": "#0f1117",
        "bg_raised": "#161b22",
        "border": "#30363d",
        "text": "#e6edf3",
        "text_muted": "#8b949e",
        "text_secondary": "#6e7681",
        "chart_grid": "rgba(255,255,255,0.04)",
        "chart_text": "#8b949e",
        "card_light_bg": "#1c2129",
        "card_light_border": "#30363d",
        "card_light_text": "#c9d1d9",
    },
    "light": {
        "bg": "#ffffff",
        "bg_raised": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#1f2328",
        "text_muted": "#656d76",
        "text_secondary": "#8b949e",
        "chart_grid": "rgba(0,0,0,0.06)",
        "chart_text": "#656d76",
        "card_light_bg": "#f6f8fa",
        "card_light_border": "#d0d7de",
        "card_light_text": "#1f2328",
    },
}

# Read theme from query param (set by JS toggle). Default dark.
raw_theme = st.query_params.get("theme", "dark")
if raw_theme not in ("dark", "light"):
    raw_theme = "dark"

T = THEMES[raw_theme]

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');

    :root {{
        --bg: {T["bg"]}; --bg-raised: {T["bg_raised"]}; --border: {T["border"]};
        --text: {T["text"]}; --text-muted: {T["text_muted"]}; --text-secondary: {T["text_secondary"]};
        --red: {ACCENT_RED}; --blue: {ACCENT_BLUE}; --orange: {ACCENT_ORANGE};
        --card-light-bg: {T["card_light_bg"]}; --card-light-border: {T["card_light_border"]};
        --card-light-text: {T["card_light_text"]};
    }}

    header[data-testid="stHeader"] {{ display: none; }}
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stApp"] {{ background: var(--bg); }}
    .block-container {{ padding: 2.5rem 2rem 1rem !important; max-width: 900px !important; }}
    html, body, [data-testid="stApp"] {{ font-family: 'Inter', sans-serif; color: var(--text); }}

    /* Theme toggle button */
    .theme-toggle {{
        position: fixed; top: 1rem; right: 1.5rem; z-index: 9999;
        background: var(--bg-raised); border: 1px solid var(--border);
        border-radius: 8px; padding: 0.4rem 0.6rem;
        cursor: pointer; font-size: 1rem; line-height: 1;
        transition: background 0.2s;
    }}
    .theme-toggle:hover {{ background: var(--border); }}

    .hero-title {{
        font-size: 2.8rem; font-weight: 900;
        letter-spacing: -0.04em; line-height: 1.05;
        color: var(--text); margin-bottom: 0.8rem;
    }}
    .hero-sub {{ font-size: 1rem; line-height: 1.7; color: var(--text-muted); }}
    .hero-sub a {{ color: var(--blue); }}

    .stat-row {{ display: flex; gap: 2rem; margin-top: 1.8rem; flex-wrap: wrap; }}
    .stat-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; line-height: 1; }}
    .stat-label {{ font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-top: 0.2rem; }}

    .card {{
        background: var(--bg-raised); border: 1px solid var(--border);
        border-radius: 12px; padding: 1.6rem 1.8rem; margin: 1.2rem 0; color: var(--text);
    }}
    .card-light {{
        background: var(--card-light-bg); border-color: var(--card-light-border); color: var(--card-light-text);
    }}

    .s-title {{ font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.3rem; color: var(--text); }}
    .s-copy {{ font-size: 0.92rem; line-height: 1.7; color: var(--text-muted); }}
    .s-copy strong {{ color: var(--text); }}
    .card-light .s-copy strong {{ color: var(--card-light-text); }}
    .card-light .s-title {{ color: var(--card-light-text); }}

    .callout {{
        border-left: 3px solid var(--red); padding: 0.8rem 1rem;
        margin: 0.8rem 0 0; font-size: 0.85rem; line-height: 1.6;
        background: rgba(207,34,46,0.06); border-radius: 0 6px 6px 0;
        color: var(--text-muted);
    }}
    .callout strong {{ color: var(--red); }}
    .callout-blue {{ border-left-color: var(--blue); background: rgba(47,129,247,0.06); }}
    .callout-blue strong {{ color: var(--blue); }}

    abbr {{ text-decoration: underline dotted var(--text-secondary); text-underline-offset: 3px; cursor: help; }}

    .footer {{ text-align: center; padding: 1.5rem 0; font-size: 0.75rem; color: var(--text-secondary); }}
    .footer a {{ color: var(--text-secondary); }}

    div[data-testid="stMetric"] {{ background: none !important; border: none !important; padding: 0 !important; }}
</style>

""",
    unsafe_allow_html=True,
)

components.html(
    """
<script>
(function() {
    var doc = window.parent.document;

    // Remove old button if exists (Streamlit reruns)
    var old = doc.getElementById('themeToggle');
    if (old) old.remove();

    // Create button
    var btn = doc.createElement('div');
    btn.id = 'themeToggle';
    btn.style.cssText = 'position:fixed;top:1rem;right:1.5rem;z-index:9999;background:var(--bg-raised);border:1px solid var(--border);border-radius:8px;padding:0.4rem 0.6rem;cursor:pointer;font-size:1rem;line-height:1;transition:background 0.2s;user-select:none;';
    doc.body.appendChild(btn);

    var modes = ['dark', 'light'];
    var icons = { dark: '\u263d', light: '\u2600' };

    var params = new URLSearchParams(doc.location.search);
    var current = params.get('theme') || 'dark';
    if (modes.indexOf(current) === -1) current = 'dark';

    btn.textContent = icons[current];
    btn.title = 'Theme: ' + current;

    // Use a script in the parent DOM so click handler has navigation rights
    var handler = doc.createElement('script');
    handler.textContent = `
        document.getElementById('themeToggle').addEventListener('click', function() {
            var modes = ['dark', 'light'];
            var params = new URLSearchParams(window.location.search);
            var current = params.get('theme') || 'dark';
            var idx = modes.indexOf(current);
            var next = modes[(idx + 1) % modes.length];
            params.set('theme', next);
            window.location.search = '?' + params.toString();
        });
    `;
    doc.body.appendChild(handler);
})();
</script>
""",
    height=0,
)

# =============================================================================
# DATA
# =============================================================================

PROJECT_ID = "threat-landscape-putopavel"
DATASET = "threat_intelligence"


@st.cache_data(ttl=3600)
def query_bq(sql):
    if "gcp_service_account" in st.secrets:
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        client = bigquery.Client(project=PROJECT_ID, credentials=creds)
    else:
        client = bigquery.Client(project=PROJECT_ID)
    return client.query(sql).to_dataframe()


# Pre-aggregated tables: tiny, fast
stats = query_bq(f"SELECT * FROM `{PROJECT_ID}.{DATASET}.mart_dashboard_stats`")
total_urls = int(stats["total_urls"].iloc[0])
still_online = int(stats["still_online"].iloc[0])
avg_h = float(stats["avg_takedown_h"].iloc[0])
median_h = float(stats["median_takedown_h"].iloc[0])
total_iocs = int(stats["total_iocs"].iloc[0])

monthly = query_bq(
    f"SELECT * FROM `{PROJECT_ID}.{DATASET}.mart_dashboard_takedown_monthly`"
)
domain_stats_all = query_bq(
    f"SELECT * FROM `{PROJECT_ID}.{DATASET}.mart_dashboard_domain_stats`"
)
ioc_types = query_bq(f"SELECT * FROM `{PROJECT_ID}.{DATASET}.mart_dashboard_ioc_types`")
trends = query_bq(
    f"SELECT report_date, source, threat_type, malware_family, daily_count FROM `{PROJECT_ID}.{DATASET}.mart_threat_trends`"
)

CHART = dict(
    font=dict(family="Inter, sans-serif", color=T["chart_text"], size=11),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=30, l=10, r=10),
    xaxis=dict(
        gridcolor=T["chart_grid"],
        zeroline=False,
        tickfont=dict(color=T["chart_text"]),
        title=dict(font=dict(color=T["chart_text"])),
    ),
    yaxis=dict(
        gridcolor=T["chart_grid"],
        zeroline=False,
        tickfont=dict(color=T["chart_text"]),
        title=dict(font=dict(color=T["chart_text"])),
    ),
)
NO_BAR = {"displayModeBar": False}


# HTML abbreviation tooltips for technical terms
def abbr(term, definition):
    return f'<abbr title="{definition}">{term}</abbr>'


IOC = abbr(
    "IOC",
    "Indicator of Compromise: a piece of evidence (domain, IP, URL, or file hash) that a system has been compromised",
)
IOCS = abbr(
    "IOCs",
    "Indicators of Compromise: pieces of evidence (domains, IPs, URLs, or file hashes) linked to malicious activity",
)
RAT = abbr(
    "RAT",
    "Remote Access Trojan: malware that gives an attacker remote control over a victim's computer",
)
RATS = abbr(
    "RATs",
    "Remote Access Trojans: malware that gives attackers remote control over victims' computers",
)
C2 = abbr(
    "C2",
    "Command and Control: the server infrastructure attackers use to communicate with and control compromised machines",
)
SOC = abbr(
    "SOC",
    "Security Operations Center: the team that monitors an organization's systems for security threats 24/7",
)
BOTNET = abbr(
    "botnet",
    "A network of compromised devices (computers, routers, cameras) controlled remotely by an attacker",
)
TAKEDOWN = abbr(
    "takedown",
    "The process of removing a malicious URL or resource after it has been reported to the hosting provider",
)

# =============================================================================
# HERO
# =============================================================================

st.markdown(
    f"""
<div class="hero-title">Threat Landscape Monitor</div>
<div class="hero-sub">
    Thousands of new malicious URLs pop up every day. A volunteer community at
    <a href="https://abuse.ch">abuse.ch</a> has been tracking them since 2018.
    This report digs into that data: how long do these URLs stay up,
    and what malware is behind them?
</div>
<div class="stat-row">
    <div><div class="stat-value" style="color:var(--red)">{still_online:,}</div><div class="stat-label">live now</div></div>
    <div><div class="stat-value" style="color:var(--orange)">{avg_h:.0f}h</div><div class="stat-label">avg. {TAKEDOWN}</div></div>
    <div><div class="stat-value" style="color:var(--blue)">{median_h:.0f}h</div><div class="stat-label">median {TAKEDOWN}</div></div>
    <div><div class="stat-value" style="color:var(--text)">{total_urls:,}</div><div class="stat-label">total tracked</div></div>
    <div><div class="stat-value" style="color:var(--text)">{total_iocs:,}</div><div class="stat-label">ThreatFox {IOCS}</div></div>
</div>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# ACT 1: TAKEDOWN
# =============================================================================

st.markdown(
    """
<div class="card" style="margin-top: 2.5rem;">
    <div class="s-title">How long until someone pulls the plug?</div>
    <div class="s-copy">
        You report a malicious URL. The hosting provider is supposed to remove it.
        Sometimes that takes an hour. Sometimes a month. Sometimes nothing happens.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=monthly["month"],
        y=monthly["mean"],
        mode="lines+markers",
        name="Average",
        line=dict(color=ACCENT_RED, width=2.5),
        marker=dict(size=6),
    )
)
fig.add_trace(
    go.Scatter(
        x=monthly["month"],
        y=monthly["median"],
        mode="lines+markers",
        name="Median",
        line=dict(color=T["chart_text"], width=2.5, dash="dot"),
        marker=dict(size=6),
    )
)
fig.update_layout(
    **CHART,
    height=280,
    yaxis_title="Hours",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        font=dict(size=10, color=T["chart_text"]),
    ),
)
st.plotly_chart(fig, use_container_width=True, config=NO_BAR)

st.markdown(
    f"""
<div class="callout">
    The average is <strong>{avg_h:.0f} hours</strong> ({avg_h / 24:.1f} days).
    The median is <strong>{median_h:.0f} hours</strong>. Big gap.
    Most URLs come down within a day or two, but a stubborn minority sticks
    around for weeks and wrecks the average.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="card">
    <div class="s-title">The hosts that don't care</div>
    <div class="s-copy">Ranked by average takedown time. Adjust the filters below.</div>
</div>
""",
    unsafe_allow_html=True,
)

col_slider, col_toggle = st.columns([3, 1])
with col_slider:
    min_urls = st.slider("Min reported URLs", 5, 100, 20, label_visibility="visible")
with col_toggle:
    only_hostnames = st.toggle(
        "Only hostnames", value=False, help="Hide bare IP addresses"
    )

domain_stats = domain_stats_all.query(f"url_count >= {min_urls}").copy()
if only_hostnames:
    domain_stats = domain_stats[
        ~domain_stats["domain"].str.match(r"^\d+\.\d+\.\d+\.\d+$")
    ]
domain_stats = domain_stats.sort_values("avg_hours", ascending=True).tail(12)

fig2 = go.Figure()
fig2.add_trace(
    go.Bar(
        y=domain_stats["domain"],
        x=domain_stats["avg_hours"],
        orientation="h",
        marker=dict(color=ACCENT_RED, opacity=0.85),
        text=domain_stats["avg_hours"].apply(lambda x: f"{x:.0f}h"),
        textposition="outside",
        textfont=dict(color=T["chart_text"], size=10),
    )
)
fig2.update_layout(**CHART, height=max(200, len(domain_stats) * 30))
fig2.update_xaxes(title="Hours")
st.plotly_chart(fig2, use_container_width=True, config=NO_BAR)

st.markdown(
    """
<div class="callout">
    Almost all bare IP addresses. No registrar to complain to, nobody monitoring
    an abuse@ inbox. Bulletproof hosts or compromised boxes. Named domains
    come down faster because registrars can pull the plug.
</div>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# ACT 2: WHAT'S OUT THERE
# =============================================================================

st.markdown(
    f"""
<div class="card">
    <div class="s-title">So what's actually out there?</div>
    <div class="s-copy">
        Two sources. <strong>URLhaus</strong> tracks where the malware lives (the URLs).
        <strong>ThreatFox</strong> tracks the {IOCS}: the fingerprints that tie a URL,
        IP, or file back to a specific malware family. One tells you <em>where</em>. The other, <em>what</em>.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

col_vol, col_types = st.columns([3, 2])

with col_vol:
    st.markdown(
        '<p style="font-size:0.88rem; color:var(--text-muted); margin-bottom:0;"><strong style="color:var(--text);">Daily reporting volume</strong> (last 12 months)</p>',
        unsafe_allow_html=True,
    )
    trends["report_date"] = trends["report_date"].astype(str)
    recent = trends[trends["report_date"] >= "2025-04-01"]
    daily = recent.groupby(["report_date", "source"])["daily_count"].sum().reset_index()
    fig4 = go.Figure()
    for src, color in [("urlhaus", ACCENT_BLUE), ("threatfox", ACCENT_ORANGE)]:
        d = daily[daily["source"] == src]
        fig4.add_trace(
            go.Bar(
                x=d["report_date"],
                y=d["daily_count"],
                name=src,
                marker=dict(color=color),
            )
        )
    fig4.update_layout(
        **CHART,
        height=260,
        yaxis_title="Reports",
        barmode="stack",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            font=dict(size=10, color=T["chart_text"]),
        ),
    )
    st.plotly_chart(fig4, use_container_width=True, config=NO_BAR)

with col_types:
    st.markdown(
        f'<p style="font-size:0.88rem; color:var(--text-muted); margin-bottom:0;"><strong style="color:var(--text);">{IOC} types in ThreatFox</strong></p>',
        unsafe_allow_html=True,
    )
    blues = [ACCENT_BLUE, "#5a9cf5", "#85b8f8", "#b0d4fc"]
    fig3 = go.Figure(
        go.Pie(
            labels=ioc_types["ioc_type"],
            values=ioc_types["count"],
            hole=0.55,
            marker=dict(colors=blues),
            textinfo="label+percent",
            textfont=dict(size=10, color=T["text"]),
        )
    )
    fig3.update_layout(**CHART, height=230, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True, config=NO_BAR)

total_recent = daily["daily_count"].sum()
url_recent = daily[daily["source"] == "urlhaus"]["daily_count"].sum()
tf_recent = daily[daily["source"] == "threatfox"]["daily_count"].sum()
bigger = "ThreatFox" if tf_recent > url_recent else "URLhaus"
bigger_n = max(tf_recent, url_recent)
smaller = "URLhaus" if bigger == "ThreatFox" else "ThreatFox"
smaller_n = min(tf_recent, url_recent)
ioc_pct = ioc_types["count"].iloc[0] / ioc_types["count"].sum() * 100
st.markdown(
    f"""
<div class="callout" style="border-left-color: var(--blue); background: rgba(47,129,247,0.06);">
    Over the last 12 months, <strong style="color:var(--blue)">{bigger}</strong> contributed
    {bigger_n:,.0f} reports vs {smaller_n:,.0f} from {smaller}. Both feeds saw a sharp uptick
    in late 2025 as the abuse.ch community grew: more reporters, more submissions, more
    visibility into what's happening out there. The daily spikes from December onward are
    the new baseline. On the {IOC} types:
    <strong style="color:var(--blue)">{ioc_pct:.0f}% are domain names</strong>,
    because throwaway domains are still the cheapest way to push malware.
</div>
""",
    unsafe_allow_html=True,
)

# -- Malware families --

MALWARE_INFO = {
    "clearfake": "Fake browser update scam. Tricks users into downloading malware by showing a bogus 'update Chrome' page.",
    "cobalt_strike": "Commercial penetration testing tool. The most pirated security tool in history; used by both red teams and criminals.",
    "asyncrat": "Remote access trojan. Lets an attacker control the victim's machine, log keystrokes, and steal files.",
    "metastealer": "Information stealer targeting macOS. Grabs passwords, cookies, and crypto wallets from browsers and apps.",
    "phorpiex": "Spam botnet active since 2010. Sends millions of sextortion and phishing emails, also distributes ransomware.",
    "quasar_rat": "Open source remote access tool. Popular with low-skill attackers because it's free and easy to deploy.",
    "vidar": "Information stealer. Grabs browser passwords, crypto wallets, and session cookies, then sends them to the attacker.",
    "remcos": "Commercial RAT marketed as 'Remote Control & Surveillance'. Sold legally but used almost exclusively by criminals.",
    "formbook": "Form-grabbing malware. Intercepts data typed into web forms, particularly login credentials and credit cards.",
    "meterpreter": "Payload from Metasploit. Gives the attacker a shell on the victim's machine; a staple of both pentesters and criminals.",
    "xworm": "Modular RAT sold on Telegram. Keylogging, screen capture, ransomware deployment, all in one package.",
    "sliver": "Open source C2 framework. Like Cobalt Strike but free, increasingly used by real attackers.",
    "dcrat": "Dark Crystal RAT. Cheap, sold on forums. Remote access with keylogging, webcam capture, and file theft.",
    "rhadamanthys": "Advanced stealer written in C++. Targets browser data, email clients, crypto wallets, and FTP credentials.",
    "iclickfix": "Social engineering scam. Shows fake CAPTCHA pages that trick users into running malicious PowerShell commands.",
    "kimsuky": "North Korean state-sponsored group. Primarily targets South Korean organizations for espionage.",
    "acr_stealer": "Credential stealer distributed through cracked software downloads.",
    "spynote": "Android spyware. Gives the attacker full control of the victim's phone including camera and microphone.",
    "odyssey_stealer": "Information stealer focused on browser data and cryptocurrency wallets.",
    "mirai": "IoT botnet. Infects routers and cameras with default passwords, then uses them for DDoS attacks.",
    "bumblebee": "Malware loader. Delivers other payloads like ransomware; often arrives through phishing emails.",
    "evilginx": "Phishing framework that can bypass two-factor authentication by acting as a man-in-the-middle proxy.",
}

st.markdown(
    f"""
<div class="card">
    <div class="s-title">The names that keep coming up</div>
    <div class="s-copy">
        ThreatFox tags every {IOC} with the malware family behind it.
        Some are {RATS} that let someone else use your machine.
        Some are stealers that grab your passwords. Some are {BOTNET}s.
        Hover over any block (or long press on mobile) to learn what it does.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

families = (
    trends.query("source == 'threatfox' and malware_family.notna()")
    .groupby("malware_family")["daily_count"]
    .sum()
    .sort_values(ascending=True)
    .tail(12)
    .reset_index()
)

max_val = families["daily_count"].max()
tree_colors = [
    f"rgba(47,129,247,{0.3 + 0.7 * (v / max_val):.2f})" for v in families["daily_count"]
]
hover_texts = [
    f"<b>{row.malware_family}</b><br>{row.daily_count} IOCs<br><br><i>{MALWARE_INFO.get(row.malware_family, '')}</i>"
    for _, row in families.iterrows()
]

fig5 = go.Figure(
    go.Treemap(
        labels=families["malware_family"],
        values=families["daily_count"],
        parents=[""] * len(families),
        textinfo="label+value",
        textfont=dict(family="Inter, sans-serif", size=13, color="#ffffff"),
        marker=dict(colors=tree_colors, line=dict(width=2, color=T["bg"])),
        hovertext=hover_texts,
        hoverinfo="text",
    )
)
fig5.update_layout(
    font=dict(family="Inter, sans-serif", color=T["text"]),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=350,
    margin=dict(t=5, b=5, l=5, r=5),
)
st.plotly_chart(fig5, use_container_width=True, config=NO_BAR)

top = families.iloc[-1]
second = families.iloc[-2]
third = families.iloc[-3]
top_6_sum = families.tail(6).iloc[:-1]["daily_count"].sum()
st.markdown(
    f"""
<div class="callout" style="border-left-color: var(--blue); background: rgba(47,129,247,0.06);">
    <strong style="color:var(--blue)">{top.malware_family}</strong> towers over everything
    else with {top.daily_count:,} {IOCS}, more than the next five combined ({top_6_sum:,}).
    {MALWARE_INFO.get(top.malware_family, "")}
    After that, <strong style="color:var(--blue)">{second.malware_family}</strong> ({second.daily_count:,})
    and <strong style="color:var(--blue)">{third.malware_family}</strong> ({third.daily_count:,})
    round out the podium. The rest is a rotating lineup of {RATS}, stealers, and {BOTNET}s:
    the bread and butter of modern cybercrime. If you run a {SOC}, these are the names
    filling your analysts' queues before their first coffee.
</div>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown(
    """
<div class="footer">
    Built with Bruin + BigQuery + Terraform + Streamlit. Runs daily via GitHub Actions.<br>
    Data by <a href="https://abuse.ch">abuse.ch</a>.
    Code on <a href="https://github.com/pavel-kalmykov/threat-landscape-monitor">GitHub</a>.
</div>
""",
    unsafe_allow_html=True,
)
