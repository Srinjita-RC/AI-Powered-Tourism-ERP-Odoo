from odoo import models, fields, api


class HotelProperty(models.Model):
    _name        = 'srk.hotel'
    _description = 'Hotel Property'

    name            = fields.Char(string='Hotel Name', required=True)
    country         = fields.Selection([
        ('in','🇮🇳 India'),('jp','🇯🇵 Japan'),('th','🇹🇭 Thailand'),
        ('fr','🇫🇷 France'),('it','🇮🇹 Italy'),('ae','🇦🇪 UAE'),
        ('sg','🇸🇬 Singapore'),('gb','🇬🇧 United Kingdom'),
        ('au','🇦🇺 Australia'),('gr','🇬🇷 Greece'),
    ], string='Country')
    star_rating     = fields.Selection([
        ('1','⭐'),('2','⭐⭐'),('3','⭐⭐⭐'),
        ('4','⭐⭐⭐⭐'),('5','⭐⭐⭐⭐⭐'),
    ], string='Star Rating')
    price_per_night = fields.Float(string='Price Per Night (USD)')
    total_rooms     = fields.Integer(string='Total Rooms')
    available_rooms = fields.Integer(string='Available Rooms')
    amenities       = fields.Text(string='Amenities')
    address         = fields.Char(string='Address')
    status          = fields.Selection([
        ('active','Active'),('full','Fully Booked'),
        ('maintenance','Under Maintenance'),
    ], default='active', string='Status')
    booking_ids   = fields.One2many('srk.booking', 'hotel_id', string='Bookings')
    booking_count = fields.Integer(compute='_compute_booking_count', store=True)

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for rec in self:
            rec.booking_count = len(rec.booking_ids)


class TourBooking(models.Model):
    _name        = 'srk.booking'
    _description = 'Tour Booking'
    _rec_name    = 'booking_ref'

    booking_ref   = fields.Char(
        string='Booking Reference', readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('srk.booking')
    )
    tourist_id    = fields.Many2one('tourist.profile', string='Tourist', required=True)
    hotel_id      = fields.Many2one('srk.hotel', string='Hotel')
    destination   = fields.Selection([
        ('in','🇮🇳 India'),('jp','🇯🇵 Japan'),('th','🇹🇭 Thailand'),
        ('fr','🇫🇷 France'),('it','🇮🇹 Italy'),('ae','🇦🇪 UAE'),
        ('sg','🇸🇬 Singapore'),('gb','🇬🇧 United Kingdom'),
        ('au','🇦🇺 Australia'),('gr','🇬🇷 Greece'),
        ('np','🇳🇵 Nepal'),('lk','🇱🇰 Sri Lanka'),
        ('tr','🇹🇷 Turkey'),('id','🇮🇩 Indonesia'),
    ], string='Destination')
    budget_usd    = fields.Float(string='Budget (USD)')
    checkin_date  = fields.Date(string='Check-in')
    checkout_date = fields.Date(string='Check-out')
    num_nights    = fields.Integer(compute='_compute_nights', store=True)
    transport_mode = fields.Selection([
        ('flight','✈️ Flight'),('train','🚂 Train'),
        ('car','🚗 Car'),('cruise','🛳️ Cruise'),('bus','🚌 Bus'),
    ], string='Transport')
    num_travelers = fields.Integer(string='Number of Travelers', default=1)

    # Hotel search preferences
    preferred_stars     = fields.Selection([
        ('any','Any Stars'),('3','3 Stars'),('4','4 Stars'),('5','5 Stars'),
    ], string='Star Rating', default='any')
    preferred_max_price = fields.Float(string='Max Price/Night (USD)',
                                        help='Leave 0 to use total budget')

    hotel_cost   = fields.Float(compute='_compute_costs', store=True)
    total_amount = fields.Float(compute='_compute_costs', store=True)

    payment_status = fields.Selection([
        ('unpaid','🔴 Unpaid'),('partial','🟡 Partial'),
        ('paid','🟢 Paid'),('refunded','↩️ Refunded'),
    ], default='unpaid', string='Payment Status')
    booking_status = fields.Selection([
        ('draft','Draft'),('confirmed','Confirmed'),
        ('checked_in','Checked In'),('completed','Completed'),('cancelled','Cancelled'),
    ], default='draft', string='Booking Status')

    hotel_recommendations = fields.Html(readonly=True, sanitize=False)
    flight_info           = fields.Html(readonly=True, sanitize=False)

    # ── Computes ──────────────────────────────────────────────────
    @api.depends('checkin_date', 'checkout_date')
    def _compute_nights(self):
        for rec in self:
            if rec.checkin_date and rec.checkout_date:
                rec.num_nights = (rec.checkout_date - rec.checkin_date).days
            else:
                rec.num_nights = 0

    @api.depends('hotel_id', 'hotel_id.price_per_night', 'num_nights', 'num_travelers')
    def _compute_costs(self):
        for rec in self:
            cost = (rec.hotel_id.price_per_night or 0) * (rec.num_nights or 0)
            rec.hotel_cost   = cost
            rec.total_amount = cost * (rec.num_travelers or 1)

    # ── Status ────────────────────────────────────────────────────
    def action_confirm(self):  self.booking_status = 'confirmed'
    def action_checkin(self):  self.booking_status = 'checked_in'
    def action_complete(self):
        self.booking_status = 'completed'
        self.payment_status = 'paid'
    def action_cancel(self):   self.booking_status = 'cancelled'

    # ── Find Hotels ───────────────────────────────────────────────
    def action_get_hotels(self):
        import requests as req
        GROQ_KEY = self.env['ir.config_parameter'].sudo().get_param('srk_tourism.groq_api_key')

        for rec in self:
            tourist   = rec.tourist_id
            dest_code = rec.destination or (tourist.destination if tourist else None)
            budget    = rec.budget_usd  or (tourist.budget_amount if tourist else 0)
            checkin   = rec.checkin_date  or (tourist.checkin_date  if tourist else '')
            checkout  = rec.checkout_date or (tourist.checkout_date if tourist else '')
            nights    = rec.num_nights or 1

            dest_labels = dict(rec._fields['destination'].selection)
            dest_name   = dest_labels.get(dest_code, dest_code or 'the destination')
            dest_clean  = dest_name.split(' ', 1)[-1] if dest_name else dest_name

            star_map   = {'any':'any star rating','3':'exactly 3 stars','4':'exactly 4 stars','5':'5-star luxury only'}
            star_text  = star_map.get(rec.preferred_stars or 'any', 'any star rating')
            max_price  = rec.preferred_max_price or 0
            price_text = f"max ${max_price:.0f} per night" if max_price > 0 else f"total budget ${budget:.0f}"

            prompt = f"""You are a hotel booking expert for {dest_clean}.
Dates: {checkin} to {checkout} ({nights} nights) | Budget: {price_text} | Stars: {star_text}

List 5 REAL hotels currently available on Booking.com in {dest_clean} matching these criteria.
Use hotels that ACTUALLY EXIST and can be booked today.

For each, use EXACTLY this format with no extra lines:
HOTEL: [Exact hotel name as on Booking.com]
STARS: [1-5 digit only]
PRICE: [price per night in USD, digits only, e.g. 120]
AREA: [district or neighborhood]
HIGHLIGHT: [one sentence — best feature]
AMENITIES: [WiFi, Pool, Breakfast, Gym etc comma separated]
RATING: [guest rating out of 10, e.g. 8.4]
---

Strictly match the star rating preference: {star_text}
Strictly stay within: {price_text}
Use ONLY real hotels bookable in {dest_clean} right now."""

            try:
                resp = req.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "Hotel booking expert. Only suggest real bookable hotels. Be precise with prices and ratings."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.4,
                        "max_tokens": 2000,
                    },
                    timeout=30
                )
                if resp.status_code == 200:
                    raw = resp.json()['choices'][0]['message']['content']
                    rec.hotel_recommendations = self._format_hotel_html(
                        raw, dest_name, dest_clean, checkin, checkout,
                        rec.preferred_stars, max_price
                    )
                else:
                    rec.hotel_recommendations = f"<p style='color:red'>Error: {resp.text}</p>"
            except Exception as e:
                rec.hotel_recommendations = f"<p style='color:red'>Error: {str(e)}</p>"

    # ── Find Flights ──────────────────────────────────────────────
    def action_get_flights(self):
        import requests as req
        GROQ_KEY = self.env['ir.config_parameter'].sudo().get_param('srk_tourism.groq_api_key')

        for rec in self:
            tourist   = rec.tourist_id
            dest_code = rec.destination or (tourist.destination if tourist else None)
            checkin   = rec.checkin_date  or (tourist.checkin_date  if tourist else '')
            checkout  = rec.checkout_date or (tourist.checkout_date if tourist else '')
            budget    = rec.budget_usd  or (tourist.budget_amount if tourist else 0)

            dest_labels = dict(rec._fields['destination'].selection)
            dest_name   = dest_labels.get(dest_code, 'your destination')
            dest_clean  = dest_name.split(' ', 1)[-1] if dest_name else dest_name

            tourist_nat = ''
            if tourist and tourist.nationality:
                tourist_nat = dict(tourist._fields['nationality'].selection).get(tourist.nationality, '')
            origin_country = tourist_nat.split(' ', 1)[-1].split('(')[0].strip() if tourist_nat else 'India'

            prompt = f"""Flight expert. Find 3 real flights from {origin_country} to {dest_clean}.
Dates: {checkin} to {checkout} | Budget: ${budget} USD

For each use EXACTLY:
FLIGHT: [Airline]
ROUTE: [IATA] to [IATA]
DEPART: [HH:MM]
ARRIVE: [HH:MM]
DURATION: [Xh Ym]
STOPS: [Non-stop OR 1 stop via City]
PRICE: [USD digits only, e.g. 450]
TIP: [one booking tip]
---
Real airlines, 2025-2026 realistic prices."""

            try:
                resp = req.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "Flight expert. Real airlines, realistic prices."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.4,
                        "max_tokens": 1500,
                    },
                    timeout=30
                )
                if resp.status_code == 200:
                    raw = resp.json()['choices'][0]['message']['content']
                    rec.flight_info = self._format_flight_html(raw, dest_name, dest_clean, str(checkin), str(checkout))
                else:
                    rec.flight_info = f"<p style='color:red'>Error: {resp.text}</p>"
            except Exception as e:
                rec.flight_info = f"<p style='color:red'>Error: {str(e)}</p>"

    # ── Hotel HTML: clickable list rows, no images ─────────────────
    def _format_hotel_html(self, text, dest_name, dest_clean,
                            checkin, checkout, star_pref, max_price):
        import urllib.parse

        # Star filter label
        star_labels = {'any':'All Stars','3':'3 Stars','4':'4 Stars','5':'5 Stars'}
        filter_label = star_labels.get(star_pref or 'any','All Stars')
        price_label  = f"Max ${max_price:.0f}/night" if max_price else "Any Price"

        hotels = [h for h in text.strip().split('---') if h.strip()]

        html = f'''
        <div style="font-family:Arial,sans-serif;">
            <div style="background:linear-gradient(135deg,#1565c0,#42a5f5);
                color:white;padding:14px 18px;border-radius:12px;margin-bottom:12px;">
                <div style="font-size:16px;font-weight:bold;">
                    🏨 Hotels in {dest_name}
                </div>
                <div style="font-size:11px;opacity:0.85;margin-top:4px;">
                    Filter: {filter_label} &nbsp;|&nbsp; {price_label} &nbsp;|&nbsp;
                    {checkin} to {checkout} &nbsp;|&nbsp;
                    Click any row to book on Booking.com
                </div>
            </div>

            <!-- Column headers -->
            <div style="display:grid;
                grid-template-columns:2fr 80px 100px 80px 100px 120px;
                background:#e3f2fd;padding:8px 14px;
                border-radius:8px 8px 0 0;
                font-size:12px;font-weight:bold;color:#1565c0;gap:8px;">
                <span>Hotel Name</span>
                <span>Stars</span>
                <span>Price/Night</span>
                <span>Rating</span>
                <span>Area</span>
                <span></span>
            </div>'''

        for i, hotel in enumerate(hotels):
            lines = hotel.strip().split('\n')
            data  = {}
            for line in lines:
                if ':' in line:
                    k, v = line.split(':', 1)
                    data[k.strip()] = v.strip()

            hotel_name = data.get('HOTEL', 'Hotel')
            stars_num  = data.get('STARS', '3').strip()
            try:
                stars_int = int(stars_num)
            except Exception:
                stars_int = 3
            stars_disp = '⭐' * stars_int

            price_raw  = data.get('PRICE', '0').replace('$','').replace(',','').strip()
            try:
                price_val = float(price_raw)
                price_disp = f"${price_val:.0f}"
            except Exception:
                price_disp = price_raw or 'N/A'

            rating     = data.get('RATING', 'N/A')
            area       = data.get('AREA', '')
            highlight  = data.get('HIGHLIGHT', '')
            amenities  = data.get('AMENITIES', '')

            # Build Booking.com URL with dates
            name_enc   = urllib.parse.quote(hotel_name)
            dest_enc   = urllib.parse.quote(dest_clean)
            ci_str     = str(checkin).replace('-','') if checkin else ''
            co_str     = str(checkout).replace('-','') if checkout else ''
            book_url   = (
                f"https://www.booking.com/searchresults.html"
                f"?ss={name_enc}+{dest_enc}"
                f"&checkin={ci_str}&checkout={co_str}"
                f"&group_adults=1&no_rooms=1&nflt=class%3D{stars_int}"
            )

            row_bg = '#ffffff' if i % 2 == 0 else '#f8f9fa'

            html += f'''
            <a href="{book_url}" target="_blank"
               style="text-decoration:none;color:inherit;display:block;">
                <div style="display:grid;
                    grid-template-columns:2fr 80px 100px 80px 100px 120px;
                    background:{row_bg};padding:12px 14px;
                    border-bottom:1px solid #e0e0e0;gap:8px;
                    align-items:center;transition:background 0.15s;"
                    onmouseover="this.style.background='#e8f4fd'"
                    onmouseout="this.style.background='{row_bg}'">
                    <div>
                        <div style="font-size:14px;font-weight:bold;color:#1565c0;">
                            {hotel_name}
                        </div>
                        <div style="font-size:11px;color:#777;margin-top:3px;">
                            ✨ {highlight}
                        </div>
                        <div style="font-size:11px;color:#999;margin-top:2px;">
                            🛎️ {amenities}
                        </div>
                    </div>
                    <div style="font-size:13px;">{stars_disp}</div>
                    <div style="font-size:15px;font-weight:bold;color:#2e7d32;">
                        {price_disp}<span style="font-size:10px;color:#888;">/night</span>
                    </div>
                    <div style="font-size:13px;color:#e65100;font-weight:bold;">
                        ⭐ {rating}
                    </div>
                    <div style="font-size:11px;color:#666;">📍 {area}</div>
                    <div>
                        <span style="background:#1565c0;color:white;
                            padding:6px 12px;border-radius:20px;
                            font-size:11px;font-weight:bold;white-space:nowrap;">
                            Book Now →
                        </span>
                    </div>
                </div>
            </a>'''

        html += '''
            <div style="padding:10px 14px;background:#f5f5f5;
                border-radius:0 0 8px 8px;font-size:11px;color:#888;">
                Prices are AI estimates. Final price confirmed on Booking.com.
            </div>
        </div>'''
        return html

    # ── Flight HTML: clickable cards ──────────────────────────────
    def _format_flight_html(self, text, dest_name, dest_clean, checkin, checkout):
        import urllib.parse
        flights = [f for f in text.strip().split('---') if f.strip()]

        html = f'''
        <div style="font-family:Arial,sans-serif;">
            <div style="background:linear-gradient(135deg,#4a148c,#7b1fa2);
                color:white;padding:14px 18px;border-radius:12px;margin-bottom:14px;">
                <div style="font-size:16px;font-weight:bold;">
                    ✈️ Flights to {dest_name}
                </div>
                <div style="font-size:11px;opacity:0.8;margin-top:3px;">
                    Click any card to search and book on Google Flights
                </div>
            </div>'''

        for flight in flights:
            lines = flight.strip().split('\n')
            data  = {}
            for line in lines:
                if ':' in line:
                    k, v = line.split(':', 1)
                    data[k.strip()] = v.strip()

            route_raw  = data.get('ROUTE', '')
            price_raw  = data.get('PRICE', '0').replace('$','').replace(',','').strip()
            try:
                price_val  = float(price_raw)
                price_disp = f"${price_val:.0f}"
            except Exception:
                price_disp = price_raw or 'N/A'

            # Google Flights URL with dates
            dest_enc = urllib.parse.quote(dest_clean)
            ci_enc   = urllib.parse.quote(str(checkin))
            co_enc   = urllib.parse.quote(str(checkout))
            book_url = (
                f"https://www.google.com/travel/flights?q="
                f"flights+to+{dest_enc}+on+{ci_enc}+returning+{co_enc}"
            )

            html += f'''
            <a href="{book_url}" target="_blank"
               style="text-decoration:none;color:inherit;display:block;margin-bottom:12px;">
                <div style="background:white;border:1px solid #e0e0e0;
                    border-radius:12px;padding:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    transition:transform 0.2s,box-shadow 0.2s;"
                    onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 20px rgba(0,0,0,0.14)'"
                    onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.06)'">
                    <div style="display:flex;justify-content:space-between;
                        align-items:center;flex-wrap:wrap;gap:10px;">
                        <div>
                            <div style="font-size:15px;font-weight:bold;color:#4a148c;">
                                ✈️ {data.get('FLIGHT','Airline')}
                            </div>
                            <div style="font-size:13px;color:#666;margin-top:3px;">
                                🛫 {route_raw} &nbsp;|&nbsp;
                                ⏱️ {data.get('DURATION','')} &nbsp;|&nbsp;
                                🔄 {data.get('STOPS','')}
                            </div>
                        </div>
                        <div style="text-align:center;background:#f3e5f5;
                            border-radius:10px;padding:8px 18px;">
                            <div style="font-size:20px;font-weight:bold;color:#4a148c;">
                                {price_disp}
                            </div>
                            <div style="font-size:10px;color:#7b1fa2;">per person</div>
                        </div>
                    </div>
                    <div style="margin-top:10px;font-size:12px;color:#555;
                        border-top:1px solid #f0f0f0;padding-top:8px;
                        display:flex;justify-content:space-between;align-items:center;">
                        <span>
                            🕐 {data.get('DEPART','')} → 🛬 {data.get('ARRIVE','')}
                            &nbsp;|&nbsp; 💡 {data.get('TIP','')}
                        </span>
                        <span style="background:#4a148c;color:white;
                            padding:5px 14px;border-radius:16px;
                            font-size:11px;font-weight:bold;white-space:nowrap;">
                            Search →
                        </span>
                    </div>
                </div>
            </a>'''

        html += '</div>'
        return html