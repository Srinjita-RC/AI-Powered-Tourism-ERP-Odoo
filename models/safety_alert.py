from odoo import models, fields, api
import requests
import re
import base64
from datetime import date


class SafetyAlert(models.Model):
    _name = 'srk.safety.alert'
    _description = 'Travel Safety Alert'
    _rec_name = 'location'

    location   = fields.Char(string='Location / Zone', required=True)
    country    = fields.Selection([
        ('in','🇮🇳 India'),('jp','🇯🇵 Japan'),('th','🇹🇭 Thailand'),
        ('fr','🇫🇷 France'),('it','🇮🇹 Italy'),('ae','🇦🇪 UAE'),
        ('sg','🇸🇬 Singapore'),('gb','🇬🇧 United Kingdom'),
        ('au','🇦🇺 Australia'),('gr','🇬🇷 Greece'),
        ('np','🇳🇵 Nepal'),('lk','🇱🇰 Sri Lanka'),
        ('tr','🇹🇷 Turkey'),('id','🇮🇩 Indonesia'),
        ('sa','🇸🇦 Saudi Arabia'),('de','🇩🇪 Germany'),
        ('sy','🇸🇾 Syria'),('iq','🇮🇶 Iraq'),
        ('af','🇦🇫 Afghanistan'),('ua','🇺🇦 Ukraine'),
        ('ye','🇾🇪 Yemen'),('ly','🇱🇾 Libya'),
        ('so','🇸🇴 Somalia'),('sd','🇸🇩 Sudan'),
        ('mm','🇲🇲 Myanmar'),('pk','🇵🇰 Pakistan'),
        ('ng','🇳🇬 Nigeria'),('et','🇪🇹 Ethiopia'),
        ('il','🇮🇱 Israel'),('ps','🇵🇸 Palestine / Gaza'),
        ('lb','🇱🇧 Lebanon'),('jo','🇯🇴 Jordan'),
        ('ru','🇷🇺 Russia'),('cn','🇨🇳 China'),
        ('us','🇺🇸 United States'),('mx','🇲🇽 Mexico'),
        ('kw','🇰🇼 Kuwait'),('qa','🇶🇦 Qatar'),
        ('om','🇴🇲 Oman'),('bh','🇧🇭 Bahrain'),
    ], string='Country', required=True)

    alert_type = fields.Selection([
        ('political','🏛️ Political Unrest'),('natural','🌋 Natural Disaster'),
        ('health','🦠 Health Advisory'),('crime','🚨 High Crime Area'),
        ('weather','⛈️ Severe Weather'),('terrorism','⚠️ Terrorism Risk'),
        ('war','💣 War / Conflict Zone'),
    ], string='Alert Type')

    severity = fields.Selection([
        ('low','🟢 Low — Exercise Caution'),
        ('medium','🟡 Medium — High Caution'),
        ('high','🔴 High — Avoid if Possible'),
        ('critical','⛔ Critical — Do Not Travel'),
    ], string='Severity Level')

    date_issued      = fields.Date(default=fields.Date.today)
    is_active        = fields.Boolean(default=True)
    issued_by        = fields.Char(default='SRK Tourism Safety Team')
    ai_safety_report = fields.Html(readonly=True, sanitize=False)
    report_pdf       = fields.Binary(readonly=True, attachment=True)
    report_pdf_name  = fields.Char(default='safety_report.pdf')

    # ─────────────────────────────────────────────────────────────
    # STEP 1 — Fetch live news headlines via NewsAPI
    # ─────────────────────────────────────────────────────────────
    def _fetch_live_news(self, country_clean):
        """
        Fetches real-time news headlines about the country from NewsAPI.
        Get a free API key at: https://newsapi.org (free tier = 100 req/day)
        Store it in Odoo System Parameters as: srk_tourism.newsapi_key
        """
        NEWS_KEY = self.env['ir.config_parameter'].sudo().get_param(
            'srk_tourism.newsapi_key'
        )

        headlines = []

        if NEWS_KEY:
            try:
                # Search for safety/conflict/travel news about this country
                queries = [
                    f"{country_clean} travel safety 2026",
                    f"{country_clean} conflict war attack 2026",
                    f"{country_clean} travel advisory warning",
                ]
                seen = set()
                for q in queries:
                    resp = requests.get(
                        "https://newsapi.org/v2/everything",
                        params={
                            "q":        q,
                            "language": "en",
                            "sortBy":   "publishedAt",
                            "pageSize": 5,
                            "apiKey":   NEWS_KEY,
                        },
                        timeout=10
                    )
                    if resp.status_code == 200:
                        articles = resp.json().get('articles', [])
                        for art in articles:
                            title = art.get('title', '')
                            desc  = art.get('description', '') or ''
                            src   = art.get('source', {}).get('name', '')
                            pub   = art.get('publishedAt', '')[:10]
                            if title and title not in seen:
                                seen.add(title)
                                headlines.append(
                                    f"[{pub}] ({src}) {title}. {desc[:120]}"
                                )
                    if len(headlines) >= 12:
                        break

            except Exception as e:
                headlines.append(f"[NewsAPI error: {str(e)}]")

        # Fallback — also try GDELT (no key needed, truly free & real-time)
        if len(headlines) < 5:
            try:
                gdelt_resp = requests.get(
                    "https://api.gdeltproject.org/api/v2/doc/doc",
                    params={
                        "query":      f"{country_clean} safety conflict attack",
                        "mode":       "artlist",
                        "maxrecords": 10,
                        "format":     "json",
                        "timespan":   "30d",
                    },
                    timeout=10
                )
                if gdelt_resp.status_code == 200:
                    data = gdelt_resp.json()
                    for art in data.get('articles', [])[:10]:
                        title = art.get('title', '')
                        if title and title not in {h.split('] ')[-1] for h in headlines}:
                            headlines.append(f"[GDELT] {title}")
            except Exception:
                pass

        return headlines

    # ─────────────────────────────────────────────────────────────
    # STEP 2 — Generate report with live news context
    # ─────────────────────────────────────────────────────────────
    def action_generate_safety_report(self):
        GROQ_KEY = self.env['ir.config_parameter'].sudo().get_param('srk_tourism.groq_api_key')

        for rec in self:
            country_name  = dict(rec._fields['country'].selection).get(rec.country, rec.country)
            country_clean = country_name.split(' ', 1)[-1] if country_name else country_name
            # strip emoji + phone code if any
            country_clean = re.sub(r'\(.*?\)', '', country_clean).strip()

            # ── Fetch live headlines ───────────────────────────────
            headlines = self._fetch_live_news(country_clean)

            if headlines:
                news_block = "LIVE NEWS HEADLINES (fetched right now — April 2026):\n"
                news_block += "\n".join(f"  • {h}" for h in headlines[:15])
            else:
                news_block = "No live news fetched. Use your best knowledge of April 2026 global events."

            prompt = f"""You are a senior travel safety analyst.
Today: April 2026.

{news_block}

Using the live headlines above as your PRIMARY source of truth, generate a
detailed safety report for tourists considering travel to:
  Country : {country_clean}
  Zone    : {rec.location}

STRICT RULES:
- Base your threat assessment on the LIVE HEADLINES above — they are current
- If headlines mention attacks, conflicts, bombings, missiles → reflect that ACCURATELY
- Do NOT downplay dangers. Tourist safety depends on honest reporting
- Do NOT invent incidents not mentioned in the headlines or your verified knowledge
- Write in present tense, reference 2026 specifically

Include EXACTLY these sections:

🚨 CURRENT THREAT LEVEL (April 2026)
- Safety rating: X/10 (10 = safest)
- Status: Safe / Exercise Caution / Avoid / Do Not Travel
- Summary of current situation based on live news above

⚠️ ACTIVE CONFLICTS & DANGERS
- Specific ongoing incidents from the headlines
- Areas of active operations, protests, or attacks

✅ RELATIVELY SAFER AREAS
- Which zones are comparatively safer and why

🦠 HEALTH & ENVIRONMENT
- Active health advisories, disease outbreaks, air quality issues

🚔 CRIME & TOURIST SAFETY
- Common crimes targeting tourists, known scams in 2026

🆘 EMERGENCY CONTACTS
- Police number, Ambulance, Tourist helpline, Nearest hospital

✈️ OFFICIAL TRAVEL ADVISORIES
- US State Dept level, UK FCDO level, Australian DFAT level
- Final recommendation: Safe / Caution / Avoid / Do Not Travel

🔄 SAFER ALTERNATIVES
- 2 destinations with similar appeal but safer right now in 2026

Be specific, reference the headlines where relevant, be honest."""

            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_KEY}",
                        "Content-Type":  "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a global travel safety analyst. "
                                    "You have been given LIVE news headlines as ground truth. "
                                    "Always reflect what the headlines say accurately. "
                                    "Never soften danger warnings in conflict zones. "
                                    "Tourist safety depends on your honesty. "
                                    "Current year is 2026."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens":  3000,
                    },
                    timeout=60
                )

                if resp.status_code == 200:
                    raw  = resp.json()['choices'][0]['message']['content']
                    html = self._format_safety_html(
                        raw, country_name, rec.location, headlines
                    )
                    rec.ai_safety_report = html
                    rec.is_active        = True
                    rec.issued_by        = 'SRK AI Safety System (April 2026 — Live Data)'
                    rec.date_issued      = fields.Date.today()

                    # Auto-set severity
                    raw_l = raw.lower()
                    if 'do not travel' in raw_l or 'active military' in raw_l or '1/10' in raw_l or '2/10' in raw_l:
                        rec.severity = 'critical'
                    elif 'avoid' in raw_l or 'high risk' in raw_l or '3/10' in raw_l or '4/10' in raw_l:
                        rec.severity = 'high'
                    elif 'exercise caution' in raw_l or '5/10' in raw_l or '6/10' in raw_l:
                        rec.severity = 'medium'
                    else:
                        rec.severity = 'low'

                    rec._generate_pdf(raw, country_name, rec.location, headlines)
                else:
                    rec.ai_safety_report = f"<p style='color:red'>API Error: {resp.text}</p>"

            except Exception as e:
                rec.ai_safety_report = f"<p style='color:red'>Error: {str(e)}</p>"

    # ─────────────────────────────────────────────────────────────
    # PDF Generation via reportlab
    # ─────────────────────────────────────────────────────────────
    def _generate_pdf(self, raw_text, country_name, zone, headlines=None):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.colors import HexColor, white, black
            from reportlab.platypus import (SimpleDocTemplate, Paragraph,
                                             Spacer, HRFlowable, Table, TableStyle)
            from reportlab.lib.units import cm
            import io

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4,
                                    leftMargin=2*cm, rightMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)

            RED   = HexColor('#b71c1c')
            MGRAY = HexColor('#757575')
            LGRAY = HexColor('#f5f5f5')

            styles    = getSampleStyleSheet()
            today_str = date.today().strftime('%d %B %Y')
            country_clean = country_name.split(' ', 1)[-1] if country_name else country_name
            country_clean = re.sub(r'\(.*?\)', '', country_clean).strip()

            title_s = ParagraphStyle('ts', fontSize=18, textColor=white,
                                      fontName='Helvetica-Bold', spaceAfter=4)
            sub_s   = ParagraphStyle('ss', fontSize=10, textColor=white,
                                      fontName='Helvetica')
            body_s  = ParagraphStyle('bs', fontSize=10, textColor=black,
                                      fontName='Helvetica', spaceBefore=3,
                                      spaceAfter=3, leftIndent=12, leading=15)
            bullet_s = ParagraphStyle('buls', fontSize=10, textColor=black,
                                       fontName='Helvetica', spaceBefore=2,
                                       spaceAfter=2, leftIndent=24, leading=14)
            warn_s  = ParagraphStyle('ws', fontSize=10,
                                      textColor=HexColor('#b71c1c'),
                                      fontName='Helvetica-Bold',
                                      backColor=HexColor('#ffebee'),
                                      spaceBefore=4, spaceAfter=4,
                                      leftIndent=12, borderPadding=6)
            safe_s  = ParagraphStyle('sfs', fontSize=10,
                                      textColor=HexColor('#1b5e20'),
                                      fontName='Helvetica',
                                      backColor=HexColor('#e8f5e9'),
                                      spaceBefore=3, spaceAfter=3,
                                      leftIndent=12, borderPadding=6)
            news_s  = ParagraphStyle('ns', fontSize=8,
                                      textColor=HexColor('#424242'),
                                      fontName='Helvetica',
                                      spaceBefore=2, spaceAfter=2,
                                      leftIndent=16, leading=12)
            disc_s  = ParagraphStyle('ds', fontSize=8, textColor=MGRAY,
                                      fontName='Helvetica', leading=12,
                                      backColor=LGRAY, borderPadding=8,
                                      spaceAfter=12)

            story = []

            # Header
            hdr = Table([[
                Paragraph("TRAVEL SAFETY REPORT", title_s), ''
            ],[
                Paragraph(f"{country_clean} — {zone}", sub_s),
                Paragraph(f"Generated: {today_str}", sub_s),
            ]], colWidths=['70%', '30%'])
            hdr.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), RED),
                ('TEXTCOLOR',  (0,0), (-1,-1), white),
                ('PADDING',    (0,0), (-1,-1), 12),
                ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN',      (1,0), (1,-1), 'RIGHT'),
            ]))
            story.append(hdr)
            story.append(Spacer(1, 14))

            story.append(Paragraph(
                "<b>DISCLAIMER:</b> This report is AI-generated using live news data "
                "fetched in real time (April 2026). Always verify with official government "
                "advisories: travel.state.gov | gov.uk/foreign-travel-advice | smartraveller.gov.au",
                disc_s
            ))

            # Live news sources section
            if headlines:
                story.append(Paragraph("LIVE NEWS SOURCES USED", ParagraphStyle(
                    'nh', fontSize=11, textColor=RED,
                    fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4
                )))
                story.append(HRFlowable(width='100%', thickness=1, color=RED))
                for h in headlines[:8]:
                    clean_h = re.sub(r'[^\x00-\x7F]', '', h).strip()
                    clean_h = clean_h.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                    story.append(Paragraph(f"• {clean_h}", news_s))
                story.append(Spacer(1, 10))

            # Main report content
            for line in raw_text.split('\n'):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 4))
                    continue

                line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                line = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                line = re.sub(r'[^\x00-\x7F]', '', line).strip()
                if not line:
                    continue

                if any(line.upper().startswith(x) for x in
                       ['[THREAT]','[DANGERS]','[SAFE','[HEALTH]',
                        '[CRIME]','[EMERGENCY]','[ADVISORY]','[ALTERNATIVES]']):
                    story.append(Spacer(1, 8))
                    story.append(HRFlowable(width='100%', thickness=1, color=RED))
                    story.append(Paragraph(line, ParagraphStyle(
                        'sec', fontSize=12, textColor=RED,
                        fontName='Helvetica-Bold', spaceBefore=6, spaceAfter=4
                    )))
                elif line.startswith('- ') or line.startswith('* '):
                    story.append(Paragraph(f"• {line[2:]}", bullet_s))
                elif re.match(r'^\d+\.', line):
                    story.append(Paragraph(line, bullet_s))
                elif 'do not travel' in line.lower() or 'critical' in line.lower():
                    story.append(Paragraph(f"DO NOT TRAVEL: {line}", warn_s))
                elif 'safe' in line.lower() and 'unsafe' not in line.lower():
                    story.append(Paragraph(line, safe_s))
                else:
                    story.append(Paragraph(line, body_s))

            # Footer
            story.append(Spacer(1, 20))
            story.append(HRFlowable(width='100%', thickness=0.5, color=MGRAY))
            story.append(Paragraph(
                f"SRK Tourism Safety Intelligence | {today_str} | "
                "travel.state.gov | gov.uk/foreign-travel-advice | smartraveller.gov.au",
                ParagraphStyle('ft', fontSize=7, textColor=MGRAY,
                                fontName='Helvetica', leading=10)
            ))

            doc.build(story)
            pdf_bytes = buf.getvalue()
            self.report_pdf      = base64.b64encode(pdf_bytes)
            self.report_pdf_name = (
                f"Safety_Report_"
                f"{country_clean.replace(' ','_')}_"
                f"{zone.replace(' ','_')}_"
                f"{today_str.replace(' ','_')}.pdf"
            )
        except Exception as e:
            pass  # HTML report still works even if PDF fails

    # ─────────────────────────────────────────────────────────────
    # HTML Formatter
    # ─────────────────────────────────────────────────────────────
    def _format_safety_html(self, text, country_name, zone, headlines=None):
        today_str     = date.today().strftime('%d %B %Y')
        country_clean = country_name.split(' ', 1)[-1] if country_name else country_name
        country_clean = re.sub(r'\(.*?\)', '', country_clean).strip()

        # Build live news banner
        news_html = ''
        if headlines:
            items = ''.join(
                f'<div style="padding:4px 0;border-bottom:1px solid #e0e0e0;'
                f'font-size:12px;color:#333;">📰 {h}</div>'
                for h in headlines[:8]
            )
            news_html = f'''
            <div style="background:#e8f5e9;border-left:4px solid #2e7d32;
                padding:12px 16px;border-radius:6px;margin-bottom:14px;">
                <div style="font-size:13px;font-weight:bold;color:#1b5e20;margin-bottom:8px;">
                    📡 Live News Headlines Used (fetched {today_str})
                </div>
                {items}
            </div>'''

        lines = text.split('\n')
        html  = [f'''<div style="font-family:Arial,sans-serif;padding:10px;">
            <div style="background:linear-gradient(135deg,#b71c1c,#e53935);
                color:white;padding:16px 20px;border-radius:12px;margin-bottom:14px;">
                <div style="font-size:18px;font-weight:bold;">
                    🚨 Live Safety Report — {country_clean} ({zone})
                </div>
                <div style="font-size:12px;opacity:0.85;margin-top:4px;">
                    Generated: {today_str} &nbsp;|&nbsp;
                    Source: Live NewsAPI + GDELT + Groq AI Analysis
                </div>
            </div>
            <div style="background:#fff3e0;border-left:4px solid #ff9800;
                padding:10px 14px;border-radius:6px;margin-bottom:12px;font-size:12px;color:#6d4c41;">
                <b>Note:</b> This report uses real-time news headlines fetched today.
                Always cross-check with official government advisories before travel.
            </div>
            {news_html}''']

        for line in lines:
            line     = line.strip()
            if not line:
                html.append('<div style="margin:4px 0;"></div>')
                continue
            line_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)

            if any(line.startswith(ic) for ic in
                   ['🚨','⚠️','✅','🦠','🚔','🆘','✈️','🔄']):
                html.append(f'''
                    <div style="background:linear-gradient(135deg,#b71c1c,#c62828);
                        color:white;padding:10px 16px;border-radius:8px;
                        margin:14px 0 6px 0;font-size:14px;font-weight:bold;">
                        {line_html}
                    </div>''')
            elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                html.append(f'''
                    <div style="padding:5px 10px 5px 24px;color:#333;
                        border-bottom:1px solid #f5f5f5;font-size:13px;">
                        &#9658; {line_html[2:]}
                    </div>''')
            elif re.match(r'^\d+\.', line):
                html.append(f'<div style="padding:5px 10px 5px 24px;font-size:13px;color:#333;">{line_html}</div>')
            elif 'do not travel' in line.lower() or 'critical' in line.lower():
                html.append(f'''
                    <div style="background:#ffebee;border-left:4px solid #f44336;
                        padding:8px 14px;margin:4px 0;border-radius:0 8px 8px 0;
                        color:#b71c1c;font-weight:bold;font-size:13px;">
                        &#9940; {line_html}
                    </div>''')
            elif 'safe' in line.lower() and 'unsafe' not in line.lower():
                html.append(f'''
                    <div style="background:#e8f5e9;border-left:4px solid #4caf50;
                        padding:8px 14px;margin:4px 0;border-radius:0 8px 8px 0;
                        color:#2e7d32;font-size:13px;">
                        &#10003; {line_html}
                    </div>''')
            else:
                html.append(f'<p style="padding:2px 10px;color:#444;margin:2px 0;font-size:13px;">{line_html}</p>')

        html.append('</div>')
        return '\n'.join(html)