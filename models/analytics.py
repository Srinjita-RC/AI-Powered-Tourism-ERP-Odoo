from odoo import models, fields, api
import json


class TourismAnalyticsDashboard(models.Model):
    _name = 'srk.analytics.dashboard'
    _description = 'Tourism Analytics Dashboard'

    name = fields.Char(default='Dashboard')

    # ─────────────────────────────────────────────────────────────
    # KPI COMPUTED FIELDS — pulled from real Odoo records
    # ─────────────────────────────────────────────────────────────

    total_bookings = fields.Integer(
        string='Total Bookings',
        compute='_compute_kpis'
    )
    total_revenue = fields.Float(
        string='Total Revenue (USD)',
        compute='_compute_kpis'
    )
    total_tourists = fields.Integer(
        string='Total Tourists',
        compute='_compute_kpis'
    )
    active_alerts = fields.Integer(
        string='Active Safety Alerts',
        compute='_compute_kpis'
    )
    confirmed_bookings = fields.Integer(
        string='Confirmed Bookings',
        compute='_compute_kpis'
    )
    avg_booking_value = fields.Float(
        string='Avg Booking Value (USD)',
        compute='_compute_kpis'
    )
    top_destination = fields.Char(
        string='Top Destination',
        compute='_compute_kpis'
    )
    occupancy_rate = fields.Float(
        string='Hotel Occupancy Rate %',
        compute='_compute_kpis'
    )

    # Charts as JSON strings for the HTML widget
    bookings_by_destination = fields.Text(compute='_compute_chart_data')
    revenue_by_destination   = fields.Text(compute='_compute_chart_data')
    bookings_by_status       = fields.Text(compute='_compute_chart_data')
    bookings_by_transport    = fields.Text(compute='_compute_chart_data')
    revenue_trend            = fields.Text(compute='_compute_chart_data')
    nationality_breakdown    = fields.Text(compute='_compute_chart_data')
    alerts_by_severity       = fields.Text(compute='_compute_chart_data')
    top_hotels               = fields.Text(compute='_compute_chart_data')

    # Full rendered dashboard HTML
    dashboard_html = fields.Html(
        string='Dashboard',
        compute='_compute_dashboard_html',
        sanitize=False
    )

    # ─────────────────────────────────────────────────────────────
    # COMPUTE KPIs
    # ─────────────────────────────────────────────────────────────
    @api.depends()
    def _compute_kpis(self):
        for rec in self:
            bookings = self.env['srk.booking'].search([])
            tourists = self.env['tourist.profile'].search([])
            alerts   = self.env['srk.safety.alert'].search([('is_active', '=', True)])
            hotels   = self.env['srk.hotel'].search([])

            rec.total_bookings    = len(bookings)
            rec.total_revenue     = sum(b.total_amount for b in bookings)
            rec.total_tourists    = len(tourists)
            rec.active_alerts     = len(alerts)
            rec.confirmed_bookings = len(bookings.filtered(
                lambda b: b.booking_status in ('confirmed', 'checked_in', 'completed')
            ))
            rec.avg_booking_value = (
                rec.total_revenue / rec.total_bookings if rec.total_bookings else 0
            )

            # Top destination by booking count
            dest_counts = {}
            for b in bookings:
                if b.destination:
                    dest_counts[b.destination] = dest_counts.get(b.destination, 0) + 1
            if dest_counts:
                top_key = max(dest_counts, key=dest_counts.get)
                dest_labels = dict(self.env['srk.booking']._fields['destination'].selection)
                rec.top_destination = dest_labels.get(top_key, top_key)
            else:
                rec.top_destination = 'N/A'

            # Hotel occupancy rate
            total_rooms = sum(h.total_rooms for h in hotels) or 1
            available   = sum(h.available_rooms for h in hotels)
            rec.occupancy_rate = round(((total_rooms - available) / total_rooms) * 100, 1)

    # ─────────────────────────────────────────────────────────────
    # COMPUTE CHART DATA
    # ─────────────────────────────────────────────────────────────
    @api.depends()
    def _compute_chart_data(self):
        for rec in self:
            bookings = self.env['srk.booking'].search([])
            tourists = self.env['tourist.profile'].search([])
            alerts   = self.env['srk.safety.alert'].search([])
            hotels   = self.env['srk.hotel'].search([])

            dest_labels = dict(self.env['srk.booking']._fields['destination'].selection)
            # strip flag emoji for chart labels
            def clean(label):
                if not label:
                    return ''
                parts = label.split(' ', 1)
                return parts[1] if len(parts) > 1 else label

            # ── bookings by destination ──
            dest_counts = {}
            dest_revenue = {}
            for b in bookings:
                if b.destination:
                    lbl = clean(dest_labels.get(b.destination, b.destination))
                    dest_counts[lbl]  = dest_counts.get(lbl, 0) + 1
                    dest_revenue[lbl] = dest_revenue.get(lbl, 0) + b.total_amount
            sorted_dest = sorted(dest_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            rec.bookings_by_destination = json.dumps({
                'labels': [d[0] for d in sorted_dest],
                'values': [d[1] for d in sorted_dest],
            })
            sorted_rev = sorted(dest_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
            rec.revenue_by_destination = json.dumps({
                'labels': [d[0] for d in sorted_rev],
                'values': [round(d[1], 2) for d in sorted_rev],
            })

            # ── bookings by status ──
            status_labels = dict(bookings._fields['booking_status'].selection) if bookings else {}
            status_counts = {}
            for b in bookings:
                lbl = status_labels.get(b.booking_status, b.booking_status)
                status_counts[lbl] = status_counts.get(lbl, 0) + 1
            rec.bookings_by_status = json.dumps({
                'labels': list(status_counts.keys()),
                'values': list(status_counts.values()),
            })

            # ── bookings by transport ──
            transport_labels = dict(bookings._fields['transport_mode'].selection) if bookings else {}
            transport_counts = {}
            for b in bookings:
                if b.transport_mode:
                    lbl = clean(transport_labels.get(b.transport_mode, b.transport_mode))
                    transport_counts[lbl] = transport_counts.get(lbl, 0) + 1
            rec.bookings_by_transport = json.dumps({
                'labels': list(transport_counts.keys()),
                'values': list(transport_counts.values()),
            })

            # ── nationality breakdown of tourists ──
            nat_labels = dict(tourists._fields['nationality'].selection) if tourists else {}
            nat_counts = {}
            for t in tourists:
                if t.nationality:
                    lbl = clean(nat_labels.get(t.nationality, t.nationality))
                    nat_counts[lbl] = nat_counts.get(lbl, 0) + 1
            sorted_nat = sorted(nat_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            rec.nationality_breakdown = json.dumps({
                'labels': [n[0] for n in sorted_nat],
                'values': [n[1] for n in sorted_nat],
            })

            # ── alerts by severity ──
            sev_labels = dict(alerts._fields['severity'].selection) if alerts else {}
            sev_counts = {}
            for a in alerts:
                if a.severity:
                    lbl = clean(sev_labels.get(a.severity, a.severity))
                    sev_counts[lbl] = sev_counts.get(lbl, 0) + 1
            rec.alerts_by_severity = json.dumps({
                'labels': list(sev_counts.keys()),
                'values': list(sev_counts.values()),
            })

            # ── top hotels by booking count ──
            hotel_data = sorted(
                [(h.name, h.booking_count, h.price_per_night) for h in hotels if h.booking_count > 0],
                key=lambda x: x[1], reverse=True
            )[:8]
            rec.top_hotels = json.dumps({
                'labels': [h[0] for h in hotel_data],
                'bookings': [h[1] for h in hotel_data],
                'prices':   [h[2] for h in hotel_data],
            })

            # ── revenue trend (by checkin month) ──
            monthly = {}
            for b in bookings:
                if b.checkin_date and b.total_amount:
                    key = b.checkin_date.strftime('%b %Y')
                    monthly[key] = monthly.get(key, 0) + b.total_amount
            rec.revenue_trend = json.dumps({
                'labels': list(monthly.keys()),
                'values': [round(v, 2) for v in monthly.values()],
            })

    # ─────────────────────────────────────────────────────────────
    # RENDER FULL DASHBOARD HTML
    # ─────────────────────────────────────────────────────────────
    @api.depends()
    def _compute_dashboard_html(self):
        for rec in self:
            # force compute of kpis and chart data
            rec._compute_kpis()
            rec._compute_chart_data()

            def fmt_currency(v):
                if v >= 1_000_000:
                    return f'${v/1_000_000:.1f}M'
                if v >= 1_000:
                    return f'${v/1_000:.1f}K'
                return f'${v:.0f}'

            kpi_tiles = [
                ('Total Bookings',    str(rec.total_bookings),         '#1565c0', '📋'),
                ('Total Revenue',     fmt_currency(rec.total_revenue), '#2e7d32', '💰'),
                ('Total Tourists',    str(rec.total_tourists),         '#6a1b9a', '🌍'),
                ('Active Alerts',     str(rec.active_alerts),          '#b71c1c', '🚨'),
                ('Confirmed',         str(rec.confirmed_bookings),     '#00695c', '✅'),
                ('Avg Booking',       fmt_currency(rec.avg_booking_value), '#e65100', '📊'),
                ('Top Destination',   rec.top_destination,             '#1565c0', '🏆'),
                ('Occupancy Rate',    f'{rec.occupancy_rate}%',        '#37474f', '🏨'),
            ]

            tiles_html = ''
            for title, value, color, icon in kpi_tiles:
                tiles_html += f'''
                <div style="background:white;border-radius:14px;padding:20px 16px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);text-align:center;
                    border-top:4px solid {color};min-width:140px;flex:1;">
                    <div style="font-size:24px;margin-bottom:6px;">{icon}</div>
                    <div style="font-size:22px;font-weight:bold;color:{color};">{value}</div>
                    <div style="font-size:12px;color:#888;margin-top:4px;">{title}</div>
                </div>'''

            # build chart json strings safely
            bbd  = rec.bookings_by_destination or '{}'
            rbd  = rec.revenue_by_destination  or '{}'
            bbs  = rec.bookings_by_status       or '{}'
            bbt  = rec.bookings_by_transport    or '{}'
            nb   = rec.nationality_breakdown    or '{}'
            abs_ = rec.alerts_by_severity       or '{}'
            th   = rec.top_hotels               or '{}'
            rt   = rec.revenue_trend            or '{}'

            rec.dashboard_html = f'''
<div style="font-family:Arial,sans-serif;background:#f5f6fa;padding:20px;min-height:100vh;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1565c0,#42a5f5);color:white;
        padding:20px 24px;border-radius:16px;margin-bottom:24px;">
        <div style="font-size:22px;font-weight:bold;">SRK Tourism — Analytics Dashboard</div>
        <div style="font-size:13px;opacity:0.85;margin-top:4px;">
            Real-time data from your Odoo records
        </div>
    </div>

    <!-- KPI Tiles -->
    <div style="display:flex;flex-wrap:wrap;gap:14px;margin-bottom:24px;">
        {tiles_html}
    </div>

    <!-- Row 1: Bookings by Destination + Revenue by Destination -->
    <div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:20px;">
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:1;min-width:300px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#1565c0;">
                📋 Bookings by Destination
            </div>
            <canvas id="chart_dest_bookings" height="220"></canvas>
        </div>
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:1;min-width:300px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#2e7d32;">
                💰 Revenue by Destination (USD)
            </div>
            <canvas id="chart_dest_revenue" height="220"></canvas>
        </div>
    </div>

    <!-- Row 2: Booking Status (donut) + Transport Mode (donut) -->
    <div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:20px;">
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:1;min-width:260px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#6a1b9a;">
                📊 Booking Status Breakdown
            </div>
            <canvas id="chart_status" height="220"></canvas>
        </div>
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:1;min-width:260px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#e65100;">
                ✈️ Transport Mode Popularity
            </div>
            <canvas id="chart_transport" height="220"></canvas>
        </div>
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:1;min-width:260px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#00695c;">
                🌍 Tourist Nationality Mix
            </div>
            <canvas id="chart_nationality" height="220"></canvas>
        </div>
    </div>

    <!-- Row 3: Revenue Trend (line) + Safety Alerts (donut) -->
    <div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:20px;">
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:2;min-width:320px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#1565c0;">
                📈 Revenue Trend (by Month)
            </div>
            <canvas id="chart_trend" height="160"></canvas>
        </div>
        <div style="background:white;border-radius:14px;padding:20px;
            box-shadow:0 2px 12px rgba(0,0,0,0.08);flex:1;min-width:260px;">
            <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#b71c1c;">
                🚨 Safety Alerts by Severity
            </div>
            <canvas id="chart_alerts" height="220"></canvas>
        </div>
    </div>

    <!-- Row 4: Top Hotels -->
    <div style="background:white;border-radius:14px;padding:20px;
        box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:20px;">
        <div style="font-weight:bold;font-size:15px;margin-bottom:16px;color:#37474f;">
            🏨 Top Hotels by Booking Count
        </div>
        <canvas id="chart_hotels" height="120"></canvas>
    </div>

    <!-- No data message if empty -->
    <div id="no_data_msg" style="display:none;text-align:center;
        padding:40px;color:#888;font-size:15px;">
        No booking data yet. Add bookings to see analytics.
    </div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
(function() {{
    var PALETTE = [
        '#1565c0','#2e7d32','#6a1b9a','#b71c1c',
        '#e65100','#00695c','#37474f','#f9a825',
        '#ad1457','#00838f'
    ];

    function safe(json_str) {{
        try {{ return JSON.parse(json_str); }}
        catch(e) {{ return {{labels:[], values:[]}}; }}
    }}

    var bbd  = safe({repr(bbd)});
    var rbd  = safe({repr(rbd)});
    var bbs  = safe({repr(bbs)});
    var bbt  = safe({repr(bbt)});
    var nb   = safe({repr(nb)});
    var abs_ = safe({repr(abs_)});
    var th   = safe({repr(th)});
    var rt   = safe({repr(rt)});

    var total = (bbd.values||[]).reduce(function(a,b){{return a+b;}},0);
    if (total === 0) {{
        document.getElementById('no_data_msg').style.display = 'block';
    }}

    function barChart(id, data, color, label) {{
        var ctx = document.getElementById(id);
        if (!ctx || !data.labels || !data.labels.length) return;
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: data.labels,
                datasets: [{{ label: label, data: data.values,
                    backgroundColor: color + 'cc', borderColor: color,
                    borderWidth: 1, borderRadius: 6 }}]
            }},
            options: {{
                responsive: true, plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }},
                           x: {{ grid: {{ display: false }} }} }}
            }}
        }});
    }}

    function donutChart(id, data) {{
        var ctx = document.getElementById(id);
        if (!ctx || !data.labels || !data.labels.length) return;
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: data.labels,
                datasets: [{{ data: data.values,
                    backgroundColor: PALETTE.slice(0, data.labels.length),
                    borderWidth: 2, borderColor: '#fff' }}]
            }},
            options: {{
                responsive: true, cutout: '60%',
                plugins: {{ legend: {{ position: 'bottom',
                    labels: {{ font: {{ size: 11 }}, padding: 10 }} }} }}
            }}
        }});
    }}

    function lineChart(id, data) {{
        var ctx = document.getElementById(id);
        if (!ctx || !data.labels || !data.labels.length) return;
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: data.labels,
                datasets: [{{ label: 'Revenue (USD)', data: data.values,
                    borderColor: '#1565c0', backgroundColor: '#1565c022',
                    fill: true, tension: 0.4, pointRadius: 4,
                    pointBackgroundColor: '#1565c0' }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }},
                           x: {{ grid: {{ display: false }} }} }}
            }}
        }});
    }}

    function horizontalBar(id, data) {{
        var ctx = document.getElementById(id);
        if (!ctx || !data.labels || !data.labels.length) return;
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: data.labels,
                datasets: [{{
                    label: 'Bookings',
                    data: data.bookings,
                    backgroundColor: '#1565c0cc',
                    borderColor: '#1565c0',
                    borderWidth: 1, borderRadius: 4
                }}]
            }},
            options: {{
                indexAxis: 'y', responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ x: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }},
                           y: {{ grid: {{ display: false }} }} }}
            }}
        }});
    }}

    // render all charts
    barChart('chart_dest_bookings', bbd, '#1565c0', 'Bookings');
    barChart('chart_dest_revenue',  rbd, '#2e7d32', 'Revenue (USD)');
    donutChart('chart_status',      bbs);
    donutChart('chart_transport',   bbt);
    donutChart('chart_nationality', nb);
    donutChart('chart_alerts',      abs_);
    lineChart('chart_trend',        rt);
    horizontalBar('chart_hotels',   th);
}})();
</script>'''