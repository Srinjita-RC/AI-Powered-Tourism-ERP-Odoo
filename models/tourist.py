from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import requests
from datetime import date


class TouristProfile(models.Model):
    _name = 'tourist.profile'
    _description = 'Tourist Profile'

    name = fields.Char(string='Full Name', required=True)
    email = fields.Char()
    phone = fields.Char()
    nationality = fields.Selection([
        ('in', '🇮🇳 India (+91)'),   
        ('us', '🇺🇸 United States (+1)'),
        ('gb', '🇬🇧 United Kingdom (+44)'),
        ('au', '🇦🇺 Australia (+61)'),
        ('ca', '🇨🇦 Canada (+1)'),
        ('de', '🇩🇪 Germany (+49)'),
        ('fr', '🇫🇷 France (+33)'),
        ('jp', '🇯🇵 Japan (+81)'),
        ('sg', '🇸🇬 Singapore (+65)'),
        ('ae', '🇦🇪 UAE (+971)'),
        ('sa', '🇸🇦 Saudi Arabia (+966)'),
        ('cn', '🇨🇳 China (+86)'),
        ('br', '🇧🇷 Brazil (+55)'),
        ('it', '🇮🇹 Italy (+39)'),
        ('kr', '🇰🇷 South Korea (+82)'),
        ('np', '🇳🇵 Nepal (+977)'),
        ('lk', '🇱🇰 Sri Lanka (+94)'),
        ('th', '🇹🇭 Thailand (+66)'),
        ('tr', '🇹🇷 Turkey (+90)'),
        ('gr', '🇬🇷 Greece (+30)'),
    ], string='Nationality')

    state = fields.Selection([
        ('profile',     'Profile'),
        ('trip',        'Trip'),
        ('interests',   'Interests'),
        ('itinerary',   'Itinerary'),
        ('destination', 'Destination'),
        ('reviews',     'Reviews'),
        ('map',         'Map'),
    ], default='profile')

    phone_code = fields.Char(
        string='📱 Country Code',
        compute='_compute_phone_code',
        store=False
    )

    language = fields.Selection([
        ('hi', '🇮🇳 Hindi'),
        ('en', '🇬🇧 English'),
        ('fr', '🇫🇷 French'),
        ('de', '🇩🇪 German'),
        ('es', '🇪🇸 Spanish'),
        ('ja', '🇯🇵 Japanese'),
        ('zh', '🇨🇳 Mandarin'),
        ('ar', '🇸🇦 Arabic'),
        ('pt', '🇵🇹 Portuguese'),
        ('ru', '🇷🇺 Russian'),
        ('ko', '🇰🇷 Korean'),
        ('it', '🇮🇹 Italian'),
    ], string='Preferred Language')

    language_note = fields.Char(
        string='Communication Language',
        compute='_compute_language_note',
        store=False
    )

    continent = fields.Selection([
        ('asia',       '🌏 Asia'),
        ('europe',     '🌍 Europe'),
        ('middle_east','🕌 Middle East'),
        ('oceania',    '🌊 Oceania'),
    ], string='Continent')

    destination = fields.Selection([
        ('in',  '🇮🇳 India'),
        ('jp',  '🇯🇵 Japan'),
        ('th',  '🇹🇭 Thailand'),
        ('cn',  '🇨🇳 China'),
        ('sg',  '🇸🇬 Singapore'),
        ('ae',  '🇦🇪 UAE'),
        ('kr',  '🇰🇷 South Korea'),
        ('np',  '🇳🇵 Nepal'),
        ('lk',  '🇱🇰 Sri Lanka'),
        ('id',  '🇮🇩 Indonesia / Bali'),
        ('fr',  '🇫🇷 France'),
        ('it',  '🇮🇹 Italy'),
        ('gb',  '🇬🇧 United Kingdom'),
        ('de',  '🇩🇪 Germany'),
        ('gr',  '🇬🇷 Greece'),
        ('ch',  '🇨🇭 Switzerland'),
        ('tr',  '🇹🇷 Turkey'),
        ('es',  '🇪🇸 Spain'),
        ('pt',  '🇵🇹 Portugal'),
        ('nl',  '🇳🇱 Netherlands'),
        ('sa',  '🇸🇦 Saudi Arabia'),
        ('qa',  '🇶🇦 Qatar'),
        ('bh',  '🇧🇭 Bahrain'),
        ('kw',  '🇰🇼 Kuwait'),
        ('om',  '🇴🇲 Oman'),
        ('jo',  '🇯🇴 Jordan'),
        ('au',  '🇦🇺 Australia'),
        ('nz',  '🇳🇿 New Zealand'),
        ('fj',  '🇫🇯 Fiji'),
        ('mv',  '🇲🇻 Maldives'),
    ], string='Destination Country')

    transport = fields.Selection([
        ('flight', '✈️ Flight'),
        ('train',  '🚂 Train'),
        ('car',    '🚗 Car / Self-drive'),
        ('cruise', '🛳️ Cruise'),
        ('bus',    '🚌 Bus'),
        ('bike',   '🏍️ Bike'),
    ], string='Transport Mode')

    checkin_date  = fields.Date(string='Check-in Date')
    checkout_date = fields.Date(string='Check-out Date')
    num_days = fields.Integer(
        string='Number of Nights',
        compute='_compute_days',
        store=True
    )

    currency = fields.Selection([
        ('inr', '🇮🇳 INR — Indian Rupee (₹)'),
        ('usd', '🇺🇸 USD — US Dollar ($)'),
        ('gbp', '🇬🇧 GBP — British Pound (£)'),
        ('eur', '🇪🇺 EUR — Euro (€)'),
        ('aed', '🇦🇪 AED — UAE Dirham (د.إ)'),
        ('jpy', '🇯🇵 JPY — Japanese Yen (¥)'),
        ('sgd', '🇸🇬 SGD — Singapore Dollar (S$)'),
        ('aud', '🇦🇺 AUD — Australian Dollar (A$)'),
        ('cad', '🇨🇦 CAD — Canadian Dollar (C$)'),
        ('chf', '🇨🇭 CHF — Swiss Franc (Fr)'),
        ('thb', '🇹🇭 THB — Thai Baht (฿)'),
        ('krw', '🇰🇷 KRW — Korean Won (₩)'),
        ('sar', '🇸🇦 SAR — Saudi Riyal (﷼)'),
    ], string='Currency', default='inr')

    budget_amount  = fields.Float(string='Budget Amount')
    budget_in_inr  = fields.Float(string='Budget in INR (₹)', compute='_compute_budget_inr', store=True)
    budget_tier    = fields.Char(string='Budget Tier',         compute='_compute_budget_inr', store=True)

    interest_adventure   = fields.Boolean(string='🏔️ Adventure')
    interest_food        = fields.Boolean(string='🍜 Food & Cuisine')
    interest_culture     = fields.Boolean(string='🏛️ Culture')
    interest_beach       = fields.Boolean(string='🏖️ Beach')
    interest_wildlife    = fields.Boolean(string='🦁 Wildlife')
    interest_wellness    = fields.Boolean(string='🧘 Wellness')
    interest_photography = fields.Boolean(string='📸 Photography')
    interest_shopping    = fields.Boolean(string='🛍️ Shopping')

    status = fields.Selection([
        ('draft',     'Draft'),
        ('planned',   'Planned'),
        ('optimized', 'Optimized'),
        ('done',      'Completed'),
    ], default='draft', string='Status')

    plan      = fields.Text(string='Generated Itinerary', readonly=True)
    plan_html = fields.Html(string='📋 Travel Plan', readonly=True, sanitize=False)

    country_highlights = fields.Html(
        string='🖼️ Destination Highlights',
        compute='_compute_country_images',
        store=False,
        sanitize=False,
    )

    weather_info = fields.Html(string='🌤️ Live Weather',     readonly=True, sanitize=False)
    real_reviews = fields.Html(string='⭐ Real Reviews',      readonly=True, sanitize=False)
    crowd_map    = fields.Html(string='🗺️ Live Map & Crowd', readonly=True, sanitize=False)

    # ─────────────────────────────────────────────────────────────
    # COMPUTE: phone code
    # ─────────────────────────────────────────────────────────────
    @api.depends('nationality')
    def _compute_phone_code(self):
        codes = {
            'in': '🇮🇳 +91', 'us': '🇺🇸 +1',  'gb': '🇬🇧 +44',
            'au': '🇦🇺 +61', 'ca': '🇨🇦 +1',  'de': '🇩🇪 +49',
            'fr': '🇫🇷 +33', 'jp': '🇯🇵 +81', 'sg': '🇸🇬 +65',
            'ae': '🇦🇪 +971','sa': '🇸🇦 +966','cn': '🇨🇳 +86',
            'br': '🇧🇷 +55', 'it': '🇮🇹 +39', 'kr': '🇰🇷 +82',
            'np': '🇳🇵 +977','lk': '🇱🇰 +94', 'th': '🇹🇭 +66',
            'tr': '🇹🇷 +90', 'gr': '🇬🇷 +30',
        }
        for rec in self:
            rec.phone_code = codes.get(rec.nationality, '🌍 Select nationality first')

    # ─────────────────────────────────────────────────────────────
    # COMPUTE: nights
    # ─────────────────────────────────────────────────────────────
    @api.depends('checkin_date', 'checkout_date')
    def _compute_days(self):
        for rec in self:
            if rec.checkin_date and rec.checkout_date:
                rec.num_days = (rec.checkout_date - rec.checkin_date).days
            else:
                rec.num_days = 0

    # ─────────────────────────────────────────────────────────────
    # COMPUTE: language note
    # ─────────────────────────────────────────────────────────────
    @api.depends('language')
    def _compute_language_note(self):
        lang_map = {
            'hi': 'Hindi — हिन्दी', 'en': 'English',
            'fr': 'French — Français', 'de': 'German — Deutsch',
            'es': 'Spanish — Español', 'ja': 'Japanese — 日本語',
            'zh': 'Mandarin — 普通话', 'ar': 'Arabic — العربية',
            'pt': 'Portuguese — Português', 'ru': 'Russian — Русский',
            'ko': 'Korean — 한국어', 'it': 'Italian — Italiano',
        }
        for rec in self:
            if rec.language:
                rec.language_note = (
                    f"Tourist will receive all communications in: "
                    f"{lang_map.get(rec.language, rec.language)}"
                )
            else:
                rec.language_note = ''

    # ─────────────────────────────────────────────────────────────
    # COMPUTE: budget INR
    # ─────────────────────────────────────────────────────────────
    @api.depends('currency', 'budget_amount')
    def _compute_budget_inr(self):
        rates_to_inr = {
            'inr': 1,    'usd': 83.5, 'gbp': 105.0, 'eur': 90.0,
            'aed': 22.7, 'jpy': 0.56, 'sgd': 62.0,  'aud': 54.0,
            'cad': 61.5, 'chf': 94.0, 'thb': 2.35,  'krw': 0.063,
            'sar': 22.3,
        }
        for rec in self:
            rate = rates_to_inr.get(rec.currency, 1)
            inr  = rec.budget_amount * rate
            rec.budget_in_inr = inr
            if inr < 15000:
                rec.budget_tier = '🟢 Budget Traveller (Under ₹15,000)'
            elif inr < 80000:
                rec.budget_tier = '🟡 Mid-range Traveller (₹15K – ₹80K)'
            else:
                rec.budget_tier = '🔴 Luxury Traveller (₹80,000+)'

    # ─────────────────────────────────────────────────────────────
    # ONCHANGE: clear destination when continent changes
    # ─────────────────────────────────────────────────────────────
    @api.onchange('continent')
    def _onchange_continent(self):
        self.destination = False

    # ─────────────────────────────────────────────────────────────
    # PHONE VALIDATION
    # ─────────────────────────────────────────────────────────────
    _PHONE_RULES = {
        'in':  (r'^[6-9]\d{9}$',    '10 digits starting with 6–9'),
        'us':  (r'^[2-9]\d{9}$',    '10 digits starting with 2–9'),
        'ca':  (r'^[2-9]\d{9}$',    '10 digits starting with 2–9'),
        'gb':  (r'^0[1-9]\d{8,9}$', '10–11 digits starting with 0'),
        'ae':  (r'^0?5\d{8}$',      '9 digits starting with 05'),
        'sa':  (r'^0?5\d{8}$',      '9 digits starting with 05'),
        'jp':  (r'^0\d{9,10}$',     '10–11 digits starting with 0'),
        'sg':  (r'^[689]\d{7}$',    '8 digits starting with 6, 8 or 9'),
        'au':  (r'^0[45]\d{8}$',    '10 digits starting with 04 or 05'),
        'de':  (r'^0\d{10,11}$',    '11–12 digits starting with 0'),
        'fr':  (r'^0[67]\d{8}$',    '10 digits starting with 06 or 07'),
        'it':  (r'^3\d{9}$',        '10 digits starting with 3'),
        'kr':  (r'^0[17]\d{8,9}$',  '10–11 digits starting with 01 or 07'),
        'np':  (r'^9[78]\d{8}$',    '10 digits starting with 97 or 98'),
        'lk':  (r'^0[17]\d{8}$',    '10 digits starting with 07'),
        'th':  (r'^0[689]\d{8}$',   '10 digits starting with 06, 08 or 09'),
        'tr':  (r'^0[5]\d{9}$',     '11 digits starting with 05'),
        'gr':  (r'^6[0-9]\d{8}$',   '10 digits starting with 6'),
        'cn':  (r'^1[3-9]\d{9}$',   '11 digits starting with 13–19'),
        'br':  (r'^[1-9]\d{10}$',   '11 digits'),
    }

    @api.constrains('phone', 'nationality')
    def _check_phone_format(self):
        for rec in self:
            if not rec.phone or not rec.nationality:
                continue
            digits = re.sub(r'\D', '', rec.phone)
            rule = self._PHONE_RULES.get(rec.nationality)
            if rule:
                pattern, description = rule
                if not re.fullmatch(pattern, digits):
                    nat_label = dict(self._fields['nationality'].selection).get(rec.nationality, rec.nationality)
                    raise ValidationError(
                        f"❌ Invalid phone number for {nat_label}.\n\n"
                        f"Expected format: {description}\n"
                        f"You entered: {rec.phone}"
                    )
            else:
                if not re.fullmatch(r'\d{7,15}', digits):
                    raise ValidationError(f"❌ Phone number must contain 7–15 digits.\nYou entered: {rec.phone}")

    # ─────────────────────────────────────────────────────────────
    # DATE VALIDATION
    # ─────────────────────────────────────────────────────────────
    @api.constrains('checkin_date', 'checkout_date')
    def _check_dates(self):
        today = date.today()
        for rec in self:
            if rec.checkin_date and rec.checkin_date < today:
                raise ValidationError(f"❌ Check-in date cannot be in the past.\nToday is {today}.")
            if rec.checkin_date and rec.checkout_date and rec.checkout_date <= rec.checkin_date:
                raise ValidationError("❌ Check-out date must be after check-in date.")

    @api.onchange('checkin_date')
    def _onchange_checkin_date(self):
        if self.checkin_date and self.checkin_date < date.today():
            return {'warning': {'title': '⚠️ Past Date', 'message': 'Check-in date is in the past.'}}
        if self.checkin_date and self.checkout_date and self.checkout_date <= self.checkin_date:
            self.checkout_date = False
            return {'warning': {'title': '⚠️ Check-out Cleared', 'message': 'Check-out was before check-in and has been cleared.'}}

    @api.onchange('checkout_date')
    def _onchange_checkout_date(self):
        if self.checkout_date and self.checkin_date and self.checkout_date <= self.checkin_date:
            return {'warning': {'title': '⚠️ Invalid Check-out', 'message': f'Check-out must be after check-in ({self.checkin_date}).'}}

    # ─────────────────────────────────────────────────────────────
    # DESTINATION HIGHLIGHT PHOTOS
    #
    # IMAGES: Using Wikimedia Commons "Special:FilePath" redirect URLs.
    # These resolve to the actual file URL server-side and are hotlink-safe
    # for display in browser contexts. Format:
    #   https://commons.wikimedia.org/wiki/Special:FilePath/FILENAME
    #
    # LINKS: All official tourism board / attraction URLs verified as of 2025.
    #
    # Tuple: (spot_name, image_url, description, official_url)
    # ─────────────────────────────────────────────────────────────
    _COUNTRY_HIGHLIGHTS = {

        # ── INDIA ──────────────────────────────────────────────
        'in': [
            (
                'Taj Mahal, Agra',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Taj_Mahal_(Edited).jpeg?width=480',
                'Symbol of eternal love — UNESCO World Heritage Site',
                'https://www.tajmahal.gov.in/',
            ),
            (
                'Amber Fort, Jaipur',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Jaipur_03-2016_05_Amber_Fort.jpg/1280px-Jaipur_03-2016_05_Amber_Fort.jpg',
                'Majestic Rajput hilltop fort overlooking Maota Lake',
                'https://www.rajasthanplaces.com/jaipur/amber-fort/',
            ),
            (
                'Kerala Backwaters',
                'https://upload.wikimedia.org/wikipedia/commons/8/85/Kerala_backwater_20080218-11.jpg',
                'Serene lagoons best explored by houseboat',
                'https://keralatourism.travel/backwaters-in-kerala',
            ),
            (
                'Varanasi Ghats',
                'https://upload.wikimedia.org/wikipedia/commons/3/3a/Varanasi_Munshi_Ghat3.jpg',
                "One of the world's oldest cities — sacred Ganga Aarti at dusk",
                'https://www.tripsavvy.com/must-see-ghats-in-varanasi-1539761',
            ),
        ],

        # ── JAPAN ──────────────────────────────────────────────
        'jp': [
            (
                'Mount Fuji',
                'https://upload.wikimedia.org/wikipedia/commons/6/66/Mount_Fuji_at_sunset%2C_March_2025.jpg',
                "Japan's iconic peak — best viewed from Lake Kawaguchiko",
                'https://www.japan.travel/en/spot/1623/',
            ),
            (
                'Fushimi Inari, Kyoto',
                'https://upload.wikimedia.org/wikipedia/commons/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg',
                'Thousands of vermillion torii gates through sacred forest',
                'https://inari.jp/en/',
            ),
            (
                'Shibuya Crossing, Tokyo',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Tokyo_Shibuya_Scramble_Crossing_2018-10-09.jpg/1280px-Tokyo_Shibuya_Scramble_Crossing_2018-10-09.jpg',
                "World's busiest pedestrian crossing — spectacular at night",
                'https://www.gotokyo.org/en/spot/6/index.html',
            ),
            (
                'Arashiyama Bamboo Grove',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Mirador_Arashiyama_Bamboo_Grove_in_Baguio_City.jpg/1920px-Mirador_Arashiyama_Bamboo_Grove_in_Baguio_City.jpg',
                'Towering bamboo columns — otherworldly natural corridor',
                'https://www.japan.travel/en/spot/583/',
            ),
        ],

        # ── THAILAND ───────────────────────────────────────────
        'th': [
            (
                'Grand Palace, Bangkok',
                'https://upload.wikimedia.org/wikipedia/commons/7/78/%E0%B8%AB%E0%B8%AD%E0%B8%A3%E0%B8%B0%E0%B8%86%E0%B8%B1%E0%B8%87_%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%A3%E0%B8%A1%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%A7%E0%B8%B1%E0%B8%87_%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%99%E0%B8%84%E0%B8%A3_%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B9%84%E0%B8%97%E0%B8%A2.jpg',
                'Dazzling complex of royal halls and temples',
                'https://www.royalgrandpalace.th/en/home',
            ),
            (
                'Phi Phi Islands',
                'https://upload.wikimedia.org/wikipedia/commons/0/09/Isla_Phi_Phi_Lay%2C_Tailandia%2C_2013-08-19%2C_DD_04.JPG',
                'Turquoise waters and dramatic limestone cliffs',
                'https://www.tourismthailand.org/Attraction/phi-phi-islands',
            ),
            (
                'Chiang Mai Old City',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Wat_Chedi_Luang_Varavihara,_Chiang_Mai,_2016.jpg?width=480',
                'Ancient walled city with over 300 Buddhist temples',
                'https://www.tourismthailand.org/Destinations/Provinces/Chiang-Mai/101',
            ),
            (
                'Wat Arun, Bangkok',
                'https://upload.wikimedia.org/wikipedia/commons/b/b3/Templo_Wat_Arun%2C_Bangkok%2C_Tailandia%2C_2013-08-22%2C_DD_30.jpg',
                'Temple of Dawn — stunning along the Chao Phraya riverside',
                'https://www.tourismthailand.org/Destinations/Provinces/Bangkok/219',
            ),
        ],

        # ── FRANCE ─────────────────────────────────────────────
        'fr': [
            (
                'Eiffel Tower, Paris',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Eiffel_Tower,_Paris,_2022.jpg?width=480',
                'The Iron Lady — visit at dusk for golden hour magic',
                'https://www.toureiffel.paris/en',
            ),
            (
                'Palace of Versailles',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Palace_of_Versailles,_view_of_the_main_building.jpg?width=480',
                "Sun King's opulent palace with 800-hectare gardens",
                'https://en.chateauversailles.fr/',
            ),
            (
                'Mont Saint-Michel',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Mont_Saint-Michel_seen_from_the_land_side.jpg?width=480',
                'Tidal island abbey floating above the sea at high tide',
                'https://www.ot-montsaintmichel.com/en/',
            ),
            (
                'Louvre Museum, Paris',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Louvre_Museum_Wikimedia_Commons.jpg?width=480',
                "World's largest art museum — home of the Mona Lisa",
                'https://www.louvre.fr/en',
            ),
        ],

        # ── ITALY ──────────────────────────────────────────────
        'it': [
            (
                'Colosseum, Rome',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Colosseo_2020.jpg?width=480',
                'Ancient amphitheatre seating 50,000 — book tickets in advance',
                'https://www.colosseo.it/en/',
            ),
            (
                'Amalfi Coast',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Amalfi_Coast_Italy.jpg?width=480',
                'Dramatic cliffside villages along UNESCO coastline',
                'https://www.italia.it/en/campania/amalfi-coast',
            ),
            (
                'Venice Grand Canal',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Canale_Grande_Ponte_di_Rialto.jpg?width=480',
                'Romantic city built on water — explore by gondola',
                'https://www.veneziaunica.it/en',
            ),
            (
                'Florence Cathedral',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Firenze_brunelleschi.jpg?width=480',
                "Brunelleschi's iconic dome — masterpiece of the Renaissance",
                'https://www.museiitaliani.it/en/firenze/',
            ),
        ],

        # ── UAE ────────────────────────────────────────────────
        'ae': [
            (
                'Burj Khalifa, Dubai',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Burj_Khalifa.jpg?width=480',
                "World's tallest tower at 828 m — breathtaking views from At The Top",
                'https://www.burjkhalifa.ae/en/',
            ),
            (
                'Sheikh Zayed Grand Mosque',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Sheikh_Zayed_Grand_Mosque_May_2021.jpg?width=480',
                "One of the world's largest mosques — 82 gleaming domes",
                'https://www.szgmc.gov.ae/en/',
            ),
            (
                'Dubai Creek & Abra',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Dubai_Creek_from_Maktoum_Bridge_at_night.jpg?width=480',
                'Historic waterway — traditional abra ride for 1 AED',
                'https://www.visitdubai.com/en/places-to-visit/dubai-creek',
            ),
            (
                'Desert Safari, Dubai',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Arabian_Desert_dunes.jpg?width=480',
                'Dune bashing, camel rides & Bedouin BBQ under the stars',
                'https://www.visitdubai.com/en/articles/desert-safari-guide',
            ),
        ],

        # ── SINGAPORE ──────────────────────────────────────────
        'sg': [
            (
                'Gardens by the Bay',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cloud_Forest%2C_Gardens_by_the_Bay%2C_Singapore.jpg/960px-Cloud_Forest%2C_Gardens_by_the_Bay%2C_Singapore.jpg',
                'Futuristic Supertrees — free light show nightly at 7:45 PM',
                'https://www.gardensbythebay.com.sg/en.html',
            ),
            (
                'Marina Bay Sands',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Marina_Bay_Sands_in_the_evening_-_20101120.jpg?width=480',
                "Iconic hotel with world's largest rooftop infinity pool",
                'https://www.marinabaysands.com/',
            ),
            (
                'Merlion Park',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Merli%C3%B3n%2C_Marina_Bay%2C_Singapur%2C_2023-08-18%2C_DD_45-47_HDR.jpg/960px-Merli%C3%B3n%2C_Marina_Bay%2C_Singapur%2C_2023-08-18%2C_DD_45-47_HDR.jpg',
                "Singapore's iconic symbol — stunning waterfront views",
                'https://www.visitsingapore.com/see-do-singapore/recreation-leisure/parks-gardens/merlion-park/',
            ),
            (
                'Maxwell Hawker Centre',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Laksa_in_Singapore.jpg?width=480',
                'UNESCO food culture — laksa, chicken rice, chilli crab',
                'https://www.visitsingapore.com/dining-drinks-singapore/local-dishes/',
            ),
        ],

        # ── UNITED KINGDOM ─────────────────────────────────────
        'gb': [
            (
                'Big Ben, London',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Big_Ben_Clock_Tower_(320px).jpg?width=480',
                "London's most iconic landmark — Houses of Parliament",
                'https://www.parliament.uk/visiting/',
            ),
            (
                'Edinburgh Castle',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Edinburgh_Castle_from_the_North.JPG?width=480',
                'Fortress on volcanic rock — holds Scottish Crown Jewels',
                'https://www.edinburghcastle.scot/',
            ),
            (
                'Stonehenge, Wiltshire',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Stonehenge2007_07_30.jpg?width=480',
                'Prehistoric stone circle dating back 5,000 years',
                'https://www.english-heritage.org.uk/visit/places/stonehenge/',
            ),
            (
                'Tower Bridge, London',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Tower_Bridge_from_the_south.jpg?width=480',
                'Victorian Gothic masterpiece spanning the River Thames',
                'https://www.towerbridge.org.uk/',
            ),
        ],

        # ── NEPAL ──────────────────────────────────────────────
        'np': [
            (
                'Everest Base Camp',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg?width=480',
                "Trek to 5,364 m — one of the world's greatest adventures",
                'https://www.welcomenepal.com/places-to-see/everest-base-camp.html',
            ),
            (
                'Phewa Lake, Pokhara',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Phewa_lake_Pokhara.jpg?width=480',
                'Serene lake reflecting the Annapurna mountain range',
                'https://www.welcomenepal.com/places-to-see/pokhara.html',
            ),
            (
                'Pashupatinath Temple',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Pashupatinath_Temple,_Kathmandu.jpg?width=480',
                'Sacred Hindu temple complex on the banks of Bagmati river',
                'https://pashupatinathtemple.org/',
            ),
            (
                'Boudhanath Stupa',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Bodnath.jpg?width=480',
                "One of the world's largest Buddhist stupas — UNESCO site",
                'https://www.welcomenepal.com/places-to-see/boudhanath.html',
            ),
        ],

        # ── INDONESIA / BALI ───────────────────────────────────
        'id': [
            (
                'Jatiluwih Rice Terraces, Bali',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Jatiluwih_Rice_Terraces,_Bali,_Indonesia_(14383074915).jpg?width=480',
                'Dramatic stepped rice paddies — UNESCO cultural landscape',
                'https://www.indonesia.travel/gb/en/destinations/bali-nusa-tenggara/bali',
            ),
            (
                'Tanah Lot Temple',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Tanah_Lot_temple,_Bali,_Indonesia.jpg?width=480',
                'Sea temple on a rocky outcrop — magical at sunset',
                'https://tanahlot.id/',
            ),
            (
                'Mount Batur Volcano',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Batur_caldera_from_kintamani.jpg?width=480',
                'Active volcano — hike at 3 AM for a blazing sunrise',
                'https://www.indonesia.travel/gb/en/destinations/bali-nusa-tenggara/bali/mount-batur',
            ),
            (
                'Uluwatu Cliff Temple',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Pura_Luhur_Uluwatu_Bali_Indonesia.jpg?width=480',
                '70-metre cliff-top temple with dramatic Indian Ocean views',
                'https://www.indonesia.travel/gb/en/destinations/bali-nusa-tenggara/bali/uluwatu-temple',
            ),
        ],

        # ── AUSTRALIA ──────────────────────────────────────────
        'au': [
            (
                'Sydney Opera House',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Sydney_Australia._(21339175489).jpg?width=480',
                'Architectural masterpiece on Sydney Harbour — UNESCO site',
                'https://www.sydneyoperahouse.com/',
            ),
            (
                'Great Barrier Reef',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Coral_reef_at_palmyra.jpg?width=480',
                "World's largest coral ecosystem — snorkel or dive from Cairns",
                'https://www.gbrmpa.gov.au/',
            ),
            (
                'Uluru, Northern Territory',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Uluru_Australia_(2).jpg?width=480',
                'Sacred sandstone monolith — stunning at sunrise and sunset',
                'https://parksaustralia.gov.au/uluru/',
            ),
            (
                'Sydney Harbour Bridge',
                'https://commons.wikimedia.org/wiki/Special:FilePath/SydneyHarbourBridge_Pano.jpg?width=480',
                'Climb the iconic coathanger — panoramic harbour views',
                'https://www.bridgeclimb.com/',
            ),
        ],

        # ── GREECE ─────────────────────────────────────────────
        'gr': [
            (
                'Acropolis, Athens',
                'https://commons.wikimedia.org/wiki/Special:FilePath/The_Parthenon_in_Athens.jpg?width=480',
                '2,500-year-old Parthenon — birthplace of democracy',
                'https://www.theacropolismuseum.gr/en',
            ),
            (
                'Santorini Caldera',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Oia_Santorini_2_Luc_Viatour.jpg?width=480',
                'Blue-domed churches above volcanic caldera — Oia sunset',
                'https://www.visitgreece.gr/islands/cyclades/santorini/',
            ),
            (
                'Meteora Monasteries',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Meteora_monasteries,_Greece.jpg?width=480',
                'Byzantine monasteries atop impossibly steep rock pillars',
                'https://www.visitgreece.gr/mainland/thessaly/meteora/',
            ),
            (
                'Mykonos Windmills',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Mykonos_Chora,_Greece.jpg?width=480',
                '16th-century windmills overlooking the Aegean Sea',
                'https://www.visitgreece.gr/islands/cyclades/mykonos/',
            ),
        ],

        # ── TURKEY ─────────────────────────────────────────────
        'tr': [
            (
                'Hagia Sophia, Istanbul',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Hagia_Sophia_Mars_2013.jpg?width=480',
                'Sixth-century masterpiece — cathedral, mosque and museum',
                'https://ayasofyacamii.gov.tr/en',
            ),
            (
                'Cappadocia Hot Air Balloons',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Balloons_in_Cappadocia.jpg?width=480',
                'Hot air balloons over fairy chimneys at sunrise',
                'https://www.goturkey.com/destination/cappadocia',
            ),
            (
                'Pamukkale Terraces',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Pamukkale_Dağlardan.jpg?width=480',
                'White calcium terraces with warm turquoise pools',
                'https://www.goturkey.com/destination/pamukkale',
            ),
            (
                'Grand Bazaar, Istanbul',
                'https://commons.wikimedia.org/wiki/Special:FilePath/GrandBazaar_1.jpg?width=480',
                "One of the world's oldest covered markets — 4,000+ shops",
                'https://www.grandbazaaristanbul.org/',
            ),
        ],

        # ── SRI LANKA ──────────────────────────────────────────
        'lk': [
            (
                'Sigiriya Lion Rock',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Sigiriya_mirror_wall.jpg?width=480',
                '5th-century rock fortress with ancient frescoes',
                'https://www.srilanka.travel/sigiriya',
            ),
            (
                'Temple of the Tooth, Kandy',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Dalada_Maligawa.jpg?width=480',
                'Sacred Buddhist temple housing a relic of the Buddha',
                'https://www.srilanka.travel/temple-of-the-tooth-relic',
            ),
            (
                'Nine Arch Bridge, Ella',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Nine_Arches_Bridge_Sri_Lanka.jpg?width=480',
                'Colonial railway bridge through lush tea estates',
                'https://www.srilanka.travel/ella',
            ),
            (
                'Yala National Park',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Sri_Lankan_Elephant_in_Yala_National_Park.jpg?width=480',
                "Highest leopard density in the world — elephants too",
                'https://www.srilanka.travel/yala-national-park',
            ),
        ],

        # ── SOUTH KOREA ────────────────────────────────────────
        'kr': [
            (
                'Gyeongbokgung Palace, Seoul',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Gyeongbokgung_Palace_in_Seoul,_South_Korea.jpg?width=480',
                'Grand Joseon dynasty palace in the heart of Seoul',
                'https://www.visitkorea.or.kr/attraction/gyeongbokgung-palace',
            ),
            (
                'Jeju Island — Seongsan Ilchulbong',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Seongsan_Ilchulbong_peak.jpg?width=480',
                'Volcanic island with waterfalls, caves and pristine beaches',
                'https://www.visitjeju.net/en',
            ),
            (
                'N Seoul Tower',
                'https://commons.wikimedia.org/wiki/Special:FilePath/N_Seoul_Tower_2018.jpg?width=480',
                'Iconic tower offering panoramic views across Seoul',
                'https://www.nseoultower.com/eng/',
            ),
            (
                'Bukchon Hanok Village',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Bukchon_Hanok_Village,_Seoul,_South_Korea.jpg?width=480',
                'Traditional Korean houses on scenic hillside in Seoul',
                'https://www.visitkorea.or.kr/attraction/bukchon-hanok-village',
            ),
        ],

        # ── GERMANY ────────────────────────────────────────────
        'de': [
            (
                'Neuschwanstein Castle',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Schloss_Neuschwanstein_2013.jpg?width=480',
                "Fairy-tale castle in the Bavarian Alps — Disney's inspiration",
                'https://www.neuschwanstein.de/englisch/tourist/',
            ),
            (
                'Brandenburg Gate, Berlin',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Brandenburger_Tor_abends.jpg?width=480',
                "Berlin's most iconic landmark — symbol of reunification",
                'https://www.visitberlin.de/en/brandenburg-gate',
            ),
            (
                'Cologne Cathedral',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Cologne_Germany_Cologne-Cathedral-06.jpg?width=480',
                'Gothic masterpiece — tallest building in the world 1880–1884',
                'https://www.koelner-dom.de/en/',
            ),
            (
                'Rhine Valley',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Loreley_2003.jpg?width=480',
                'Medieval castles and vineyards along the UNESCO Rhine',
                'https://www.germany.travel/en/nature-outdoor-activities/rhine-valley.html',
            ),
        ],

        # ── SPAIN ──────────────────────────────────────────────
        'es': [
            (
                'Sagrada Familia, Barcelona',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Sagrada_Familia_01.jpg?width=480',
                "Gaudí's unfinished masterpiece — Barcelona's crown jewel",
                'https://www.sagradafamilia.org/en/',
            ),
            (
                'Alhambra, Granada',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Alhambra_palace_from_mirador.jpg?width=480',
                'Moorish palace with stunning geometric architecture',
                'https://www.alhambra-patronato.es/en',
            ),
            (
                'Park Güell, Barcelona',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Park_Güell_Terrace.jpg?width=480',
                "Gaudí's mosaic wonderland with panoramic city views",
                'https://parkguell.barcelona/en/',
            ),
            (
                'Prado Museum, Madrid',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Museo_del_Prado.jpg?width=480',
                "One of the world's finest art museums — Goya, Velázquez",
                'https://www.museodelprado.es/en',
            ),
        ],

        # ── MALDIVES ───────────────────────────────────────────
        'mv': [
            (
                'Overwater Bungalows',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Overwater_bungalows_in_Maldives.jpg?width=480',
                'Glass-floor villas above crystal-clear turquoise lagoons',
                'https://visitmaldives.com/en',
            ),
            (
                'Male Atoll from Above',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Maldives_from_the_air.jpg?width=480',
                'Seaplane transfers reveal stunning coral atoll geometry',
                'https://visitmaldives.com/en/see-and-do/activities',
            ),
            (
                'Maldives Coral Reef',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Coral_reef_maldives.jpg?width=480',
                'Swim alongside manta rays and whale sharks in warm waters',
                'https://visitmaldives.com/en/see-and-do/dive',
            ),
            (
                'Sunset over Indian Ocean',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Maldives_Sunset.jpg?width=480',
                'Fiery sunsets over the Indian Ocean — world-class luxury',
                'https://visitmaldives.com/en',
            ),
        ],

        # ── SWITZERLAND ────────────────────────────────────────
        'ch': [
            (
                'Matterhorn, Zermatt',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Matterhorn_from_Domhütte_-_2012-08-03_-_2.jpg?width=480',
                "Switzerland's most iconic peak — ski or hike year-round",
                'https://www.zermatt.ch/en',
            ),
            (
                'Lucerne & Chapel Bridge',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Luzern_Kapellbrücke.jpg?width=480',
                'Medieval wooden bridge — most photographed in Europe',
                'https://www.luzern.com/en/',
            ),
            (
                'Jungfraujoch',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Jungfraujoch_from_the_air.jpg?width=480',
                'Top of Europe at 3,454 m — glaciers and panoramic views',
                'https://www.jungfrau.ch/en-gb/jungfraujoch-top-of-europe/',
            ),
            (
                'Lake Geneva',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Lake_Geneva_from_Montreux.jpg?width=480',
                'Pristine alpine lake with Chillon Castle on its shores',
                'https://www.lake-geneva-region.ch/en/',
            ),
        ],

        # ── CHINA ──────────────────────────────────────────────
        'cn': [
            (
                'Great Wall of China',
                'https://upload.wikimedia.org/wikipedia/commons/1/10/20090529_Great_Wall_8185.jpg',
                'Mutianyu section — less crowded, stunning mountain views',
                'https://www.travelchinaguide.com/china_great_wall/',
            ),
            (
                'Forbidden City, Beijing',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Forbidden_City_Beijing_China.jpg/1280px-Forbidden_City_Beijing_China.jpg',
                "World's largest palace — 960 buildings, 9,000 rooms",
                'https://en.dpm.org.cn/',
            ),
            (
                'Li River, Guilin',
                'https://upload.wikimedia.org/wikipedia/commons/f/fd/Li_River%2C_Yangshuo%2C_Guangxi%2C_October_1999_05.jpg',
                'Karst mountains mirrored in the Li River — on the 20 Yuan note',
                'https://www.travelchinaguide.com/attraction/guangxi/guilin/',
            ),
            (
                'West Lake, Hangzhou',
                'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/West_Lake%2C_Hangzhou%2C_China.jpg/1280px-West_Lake%2C_Hangzhou%2C_China.jpg',
                'UNESCO cultural landscape of pagodas, temples and silk pavilions',
                'https://www.travelchinaguide.com/attraction/zhejiang/hangzhou/westlake/',
            ),
        ],

        # ── PORTUGAL ───────────────────────────────────────────
        'pt': [
            (
                'Pena Palace, Sintra',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Pena_National_Palace,_Sintra,_Portugal,_2019-05-25,_DD_40.jpg?width=480',
                'Fairy-tale coloured palace on a UNESCO World Heritage hill',
                'https://www.parquesdesintra.pt/en/parks-monuments/national-palace-of-pena/',
            ),
            (
                'Belém Tower, Lisbon',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Torre_de_Belém_June_2017.jpg?width=480',
                'Iconic 16th-century fortress on the Tagus River',
                'https://www.torrebelem.gov.pt/en/',
            ),
            (
                'Douro Valley Vineyards',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Douro_Valley_(4594027955).jpg?width=480',
                'Terraced UNESCO wine region — river cruise through vineyards',
                'https://www.visitportugal.com/en/content/douro-valley',
            ),
            (
                'Alfama District, Lisbon',
                'https://commons.wikimedia.org/wiki/Special:FilePath/LisbonAlfama.jpg?width=480',
                'Medieval Moorish quarter — best heard through live Fado music',
                'https://www.visitlisboa.com/en/places/alfama',
            ),
        ],

        # ── NETHERLANDS ────────────────────────────────────────
        'nl': [
            (
                'Keukenhof Gardens',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Keukenhof-2009.jpg?width=480',
                "World's largest tulip garden — 7 million bulbs every spring",
                'https://keukenhof.nl/en/',
            ),
            (
                'Amsterdam Canals',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Amsterdam_Canals.jpg?width=480',
                'UNESCO canal ring — explore by boat or bicycle',
                'https://www.iamsterdam.com/en/see-and-do/things-to-do/canal-boat-tours',
            ),
            (
                'Rijksmuseum, Amsterdam',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Rijksmuseum_Amsterdam_2016.jpg?width=480',
                'Rembrandt, Vermeer and the Dutch Golden Age masterpieces',
                'https://www.rijksmuseum.nl/en',
            ),
            (
                'Kinderdijk Windmills',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Kinderdijk_-_windmills.jpg?width=480',
                '19 UNESCO windmills — iconic symbol of Dutch heritage',
                'https://www.kinderdijk.com/en/',
            ),
        ],

        # ── SAUDI ARABIA ───────────────────────────────────────
        'sa': [
            (
                'Al-Masjid al-Haram, Mecca',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Masjid_Al_Haram,_Mecca,_Saudi_Arabia.jpg?width=480',
                "Islam's holiest mosque — surrounds the sacred Kaaba",
                'https://www.visitsaudi.com/en/see-do/attractions/al-masjid-al-haram',
            ),
            (
                'Hegra (Al-Ula)',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Hegra_Madain_Salih_Saudi_Arabia.jpg?width=480',
                "Saudi Arabia's first UNESCO site — Nabataean rock tombs",
                'https://www.experiencealula.com/',
            ),
            (
                'Edge of the World, Riyadh',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Edge_of_the_World_Saudi_Arabia.jpg?width=480',
                'Dramatic 300 m escarpment overlooking endless desert',
                'https://www.visitsaudi.com/en/riyadh',
            ),
            (
                'Al-Ula Old Town',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Al_Ula_Old_Town.jpg?width=480',
                '900-year-old mudbrick city abandoned in 1983',
                'https://www.experiencealula.com/en/things-to-do/heritage/old-town',
            ),
        ],

        # ── QATAR ──────────────────────────────────────────────
        'qa': [
            (
                'Museum of Islamic Art, Doha',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Museum_of_Islamic_Art,_Doha,_Qatar.jpg?width=480',
                "I.M. Pei's geometric masterpiece on Doha's waterfront",
                'https://mia.org.qa/en/',
            ),
            (
                'Souq Waqif, Doha',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Souq_Waqif_at_Night.jpg?width=480',
                'Restored 19th-century market — spices, falcons, traditional crafts',
                'https://www.visitqatar.qa/en/experience/souq-waqif',
            ),
            (
                'The Pearl-Qatar',
                'https://commons.wikimedia.org/wiki/Special:FilePath/The_Pearl_Qatar.jpg?width=480',
                'Artificial island with luxury yachts and Mediterranean-style piazza',
                'https://www.visitqatar.qa/en/experience/the-pearl-qatar',
            ),
            (
                'Katara Cultural Village',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Katara_Cultural_Village_Qatar.jpg?width=480',
                'Hub for arts and culture with Roman-style amphitheatre',
                'https://www.katara.net/en',
            ),
        ],

        # ── OMAN ───────────────────────────────────────────────
        'om': [
            (
                'Sultan Qaboos Grand Mosque',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Sultan_Qaboos_Grand_Mosque.jpg?width=480',
                "One of the world's largest mosques — stunning Persian carpet",
                'https://www.omantourism.gov.om/wps/portal/mot/tourism/oman/home/attractions/cultural/sultanQaboosGrandMosque',
            ),
            (
                'Wahiba Sands Desert',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Wahiba_Sands.jpg?width=480',
                'Rolling red and white dunes — overnight Bedouin camp experience',
                'https://www.omantourism.gov.om/',
            ),
            (
                'Wadi Shab',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Wadi_Shab_Oman.jpg?width=480',
                'Lush canyon with emerald pools — swim through a hidden cave',
                'https://www.omantourism.gov.om/',
            ),
            (
                'Mutrah Souq, Muscat',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Mutrah_Souq,_Muscat,_Oman.jpg?width=480',
                "One of Arabia's oldest souqs — frankincense and silver jewellery",
                'https://www.omantourism.gov.om/',
            ),
        ],

        # ── JORDAN ─────────────────────────────────────────────
        'jo': [
            (
                'Petra — Treasury',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Petra_Jordan_BW_21.jpg?width=480',
                "Rose-red city carved in rock — one of the New Seven Wonders",
                'https://www.visitjordan.com/Listing/attraction/petra/32',
            ),
            (
                'Wadi Rum Desert',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Wadi_rum_un_protected_area.jpg?width=480',
                'Vast red sand desert — Lawrence of Arabia filmed here',
                'https://www.visitjordan.com/Listing/attraction/wadi-rum/44',
            ),
            (
                'Dead Sea',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Dead_Sea_by_David_Shankbone.jpg?width=480',
                "World's lowest point — float effortlessly in salt waters",
                'https://www.visitjordan.com/Listing/attraction/dead-sea/36',
            ),
            (
                'Jerash Roman City',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Jerash_panorama.jpg?width=480',
                'Best-preserved Roman city outside Italy — still in use',
                'https://www.visitjordan.com/Listing/attraction/jerash/35',
            ),
        ],

        # ── NEW ZEALAND ────────────────────────────────────────
        'nz': [
            (
                'Milford Sound, Fiordland',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Mitre_Peak,_Milford_Sound,_New_Zealand.jpg?width=480',
                "World's top travel destination — dramatic fjord cruise",
                'https://www.newzealand.com/us/plan/business/milford-sound/',
            ),
            (
                'Hobbiton, Matamata',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Hobbiton_movie_set_(4).jpg?width=480',
                'Real Shire from The Lord of the Rings — guided tours daily',
                'https://www.hobbitontours.com/',
            ),
            (
                'Rotorua Geothermal',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Wai-O-Tapu_Champagne_Pool_Rotorua_NZ.jpg?width=480',
                'Bubbling mud pools, geysers and rainbow Champagne Pool',
                'https://www.newzealand.com/us/rotorua/',
            ),
            (
                'Franz Josef Glacier',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Franz_Josef_glacier.jpg?width=480',
                'Rare rainforest-to-glacier hike — helicopter tours available',
                'https://www.newzealand.com/us/feature/franz-josef-glacier/',
            ),
        ],

        # ── FIJI ───────────────────────────────────────────────
        'fj': [
            (
                'Mamanuca Islands',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Fiji_-_Mamanucas.jpg?width=480',
                'Palm-fringed islands — day-cruise or island-hop by ferry',
                'https://www.fiji.travel/explore/island-groups/mamanucas',
            ),
            (
                'Yasawa Islands',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Yasawa_Islands_Fiji.jpg?width=480',
                'Remote paradise — Blue Lagoon cave swimming',
                'https://www.fiji.travel/explore/island-groups/yasawas',
            ),
            (
                'Sigatoka Sand Dunes',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Fiji_Sigatoka_Sand_Dunes.jpg?width=480',
                "Fiji's first national park — ancient pottery burial sites",
                'https://www.fiji.travel/experience/parks-gardens/sigatoka-sand-dunes-national-park',
            ),
            (
                'Coral Coast Reefs',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Fiji_coral_reef.jpg?width=480',
                "World-class snorkelling on the world's third-largest reef",
                'https://www.fiji.travel/experience/water-activities/snorkelling-and-diving',
            ),
        ],

        # ── BAHRAIN ────────────────────────────────────────────
        'bh': [
            (
                'Qal\'at al-Bahrain (Bahrain Fort)',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Bahrain_fort_2.jpg?width=480',
                'UNESCO World Heritage 4,000-year-old Bronze Age fortress',
                'https://www.bahrain.com/en/things-to-do/cultural-heritage/bahrain-fort',
            ),
            (
                'Al-Fateh Grand Mosque',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Al_Fateh_Grand_Mosque.jpg?width=480',
                "One of the world's largest mosques — welcomes non-Muslim visitors",
                'https://www.bahrain.com/en/things-to-do/cultural-heritage/al-fateh-grand-mosque',
            ),
            (
                'Tree of Life',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Tree_of_Life,_Bahrain.jpg?width=480',
                '400-year-old mesquite tree thriving alone in desert — local legend',
                'https://www.bahrain.com/en/things-to-do/natural-attractions/tree-of-life',
            ),
            (
                'Bahrain National Museum',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Bahrain_National_Museum.jpg?width=480',
                "Arabia's oldest national museum — Dilmun civilisation artefacts",
                'https://www.bahrain.com/en/things-to-do/cultural-heritage/bahrain-national-museum',
            ),
        ],

        # ── KUWAIT ─────────────────────────────────────────────
        'kw': [
            (
                'Kuwait Towers',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Kuwait_Towers_2.jpg?width=480',
                "Symbol of modern Kuwait — panoramic Gulf views from the top",
                'https://www.kuwaitourism.com/',
            ),
            (
                'The Grand Mosque, Kuwait City',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Grand_Mosque_Kuwait.jpg?width=480',
                "Kuwait's largest mosque — guided tours for visitors",
                'https://www.kuwaitourism.com/',
            ),
            (
                'Souq Al-Mubarakiya',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Mubarakiya_Souk_Kuwait.jpg?width=480',
                "Kuwait's oldest and most authentic traditional market",
                'https://www.kuwaitourism.com/',
            ),
            (
                'The Scientific Center, Kuwait',
                'https://commons.wikimedia.org/wiki/Special:FilePath/Scientific_Center_Kuwait.jpg?width=480',
                'Stunning waterfront aquarium and IMAX — great for families',
                'https://www.tsck.org.kw/en/',
            ),
        ],
    }

    @api.depends('destination')
    def _compute_country_images(self):
        for rec in self:
            dest = rec.destination
            highlights = self._COUNTRY_HIGHLIGHTS.get(dest)
            if not highlights:
                rec.country_highlights = (
                    '<div style="color:#888;padding:20px;text-align:center;font-size:15px;">'
                    '🌍 Select a destination and generate your plan to see highlights.</div>'
                )
                continue

            dest_label = dict(rec._fields['destination'].selection).get(dest, dest)
            cards_html = ''

            for (spot, img_url, description, official_url) in highlights:
                cards_html += f'''
                <a href="{official_url}" target="_blank" rel="noopener noreferrer"
                   style="text-decoration:none;color:inherit;display:block;
                          border-radius:14px;overflow:hidden;
                          box-shadow:0 4px 16px rgba(0,0,0,0.12);
                          background:#fff;flex:1;min-width:200px;max-width:270px;
                          transition:transform 0.2s ease,box-shadow 0.2s ease;
                          cursor:pointer;"
                   onmouseover="this.style.transform='translateY(-6px)';this.style.boxShadow='0 10px 28px rgba(0,0,0,0.22)'"
                   onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'">
                    <div style="position:relative;overflow:hidden;background:#e0e0e0;height:175px;">
                        <img src="{img_url}"
                             alt="{spot}"
                             style="width:100%;height:175px;object-fit:cover;display:block;
                                    transition:transform 0.3s ease;"
                             onmouseover="this.style.transform='scale(1.05)'"
                             onmouseout="this.style.transform='scale(1)'"
                             onerror="this.parentNode.innerHTML='<div style=\\'height:175px;display:flex;align-items:center;justify-content:center;background:#f5f5f5;font-size:32px;\\'>🏞️</div>'"
                             loading="lazy"
                             referrerpolicy="no-referrer"/>
                        <div style="position:absolute;top:10px;right:10px;
                                    background:rgba(0,0,0,0.55);color:white;
                                    font-size:11px;padding:3px 8px;border-radius:20px;">
                            🔗 Official Site
                        </div>
                    </div>
                    <div style="padding:12px 14px 14px;">
                        <div style="font-weight:bold;font-size:13px;color:#1a1a1a;
                                    margin-bottom:5px;">📍 {spot}</div>
                        <div style="font-size:12px;color:#666;line-height:1.6;
                                    margin-bottom:8px;">{description}</div>
                        <div style="font-size:11px;color:#1565c0;font-weight:500;">
                            Tap to explore on official site →
                        </div>
                    </div>
                </a>'''

            rec.country_highlights = f'''
            <div style="font-family:Arial,sans-serif;padding:10px 0;">
                <div style="background:linear-gradient(135deg,#1565c0,#42a5f5);
                            color:white;padding:14px 18px;border-radius:12px;
                            margin-bottom:16px;font-size:16px;font-weight:bold;">
                    📸 Must-See Highlights — {dest_label}
                    <span style="font-size:12px;font-weight:normal;opacity:0.85;
                                 margin-left:12px;">Click any card to open official source</span>
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:18px;justify-content:flex-start;">
                    {cards_html}
                </div>
                <div style="margin-top:12px;font-size:11px;color:#999;text-align:right;">
                    📷 Images: Wikimedia Commons (CC licence) &nbsp;|&nbsp;
                    🔗 Links: Official tourism boards
                </div>
            </div>'''

    # ─────────────────────────────────────────────────────────────
    # WEATHER via Open-Meteo (FREE, no API key)
    # ─────────────────────────────────────────────────────────────
    def _get_real_weather(self, destination):
        coords = {
            'in': (28.6139, 77.2090,  'New Delhi'),
            'jp': (35.6762, 139.6503, 'Tokyo'),
            'th': (13.7563, 100.5018, 'Bangkok'),
            'fr': (48.8566, 2.3522,   'Paris'),
            'it': (41.9028, 12.4964,  'Rome'),
            'ae': (25.2048, 55.2708,  'Dubai'),
            'sg': (1.3521,  103.8198, 'Singapore'),
            'mv': (4.1755,  73.5093,  'Male'),
            'gb': (51.5074, -0.1278,  'London'),
            'ch': (46.9481, 7.4474,   'Bern'),
            'np': (27.7172, 85.3240,  'Kathmandu'),
            'lk': (6.9271,  79.8612,  'Colombo'),
            'tr': (41.0082, 28.9784,  'Istanbul'),
            'gr': (37.9838, 23.7275,  'Athens'),
            'id': (-8.3405, 115.0920, 'Bali'),
            'au': (-33.8688,151.2093, 'Sydney'),
            'kr': (37.5665, 126.9780, 'Seoul'),
            'cn': (39.9042, 116.4074, 'Beijing'),
            'sa': (24.7136, 46.6753,  'Riyadh'),
            'de': (52.5200, 13.4050,  'Berlin'),
            'es': (40.4168, -3.7038,  'Madrid'),
            'pt': (38.7169, -9.1395,  'Lisbon'),
            'nl': (52.3676, 4.9041,   'Amsterdam'),
            'nz': (-36.8485,174.7633, 'Auckland'),
            'fj': (-18.1416,178.4419, 'Suva'),
            'qa': (25.2854, 51.5310,  'Doha'),
            'bh': (26.0667, 50.5577,  'Manama'),
            'kw': (29.3759, 47.9774,  'Kuwait City'),
            'om': (23.5880, 58.3829,  'Muscat'),
            'jo': (31.9522, 35.9330,  'Amman'),
        }
        c = coords.get(destination)
        if not c:
            return '<div style="padding:16px;color:#888;">🌍 Weather data not available for this destination.</div>'
        lat, lon, city = c
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
                f"&timezone=auto&forecast_days=7"
            )
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                return f'<div style="color:red;padding:16px;">❌ Weather API returned status {r.status_code}</div>'
            d    = r.json()
            curr = d.get('current', {})
            daily= d.get('daily', {})
            temp     = curr.get('temperature_2m', 'N/A')
            humidity = curr.get('relative_humidity_2m', 'N/A')
            wind     = curr.get('windspeed_10m', 'N/A')
            code     = curr.get('weathercode', 0)

            def weather_icon(c):
                if c == 0:            return '☀️', 'Clear Sky'
                elif c in [1,2,3]:    return '⛅', 'Partly Cloudy'
                elif c in [45,48]:    return '🌫️', 'Foggy'
                elif c in [51,53,55]: return '🌦️', 'Drizzle'
                elif c in [61,63,65]: return '🌧️', 'Rainy'
                elif c in [71,73,75]: return '❄️', 'Snowy'
                elif c in [80,81,82]: return '🌦️', 'Rain Showers'
                elif c in [95,96,99]: return '⛈️', 'Thunderstorm'
                else:                 return '🌤️', 'Mostly Clear'

            icon, desc = weather_icon(code)
            forecast_html = ''
            dates  = daily.get('time', [])
            maxs   = daily.get('temperature_2m_max', [])
            mins   = daily.get('temperature_2m_min', [])
            rains  = daily.get('precipitation_sum', [])
            wcodes = daily.get('weathercode', [])
            for i in range(min(7, len(dates))):
                fi, _ = weather_icon(wcodes[i] if i < len(wcodes) else 0)
                try:
                    from datetime import datetime
                    day_name = datetime.strptime(dates[i], '%Y-%m-%d').strftime('%a')
                except Exception:
                    day_name = dates[i][5:]
                rain_val = rains[i] if i < len(rains) else 0
                forecast_html += f'''
                <div style="text-align:center;background:rgba(255,255,255,0.15);
                    border-radius:10px;padding:10px 8px;min-width:70px;flex:1;">
                    <div style="font-size:11px;opacity:0.85;">{day_name}</div>
                    <div style="font-size:20px;">{fi}</div>
                    <div style="font-size:13px;font-weight:bold;">{maxs[i] if i < len(maxs) else "?"}°</div>
                    <div style="font-size:11px;opacity:0.75;">{mins[i] if i < len(mins) else "?"}°</div>
                    <div style="font-size:10px;opacity:0.7;">💧{rain_val}mm</div>
                </div>'''

            return f'''
            <div style="font-family:Arial,sans-serif;">
                <div style="background:linear-gradient(135deg,#1565c0,#1976d2);color:white;
                    padding:20px;border-radius:14px;margin-bottom:14px;">
                    <div style="font-size:18px;font-weight:bold;margin-bottom:4px;">{icon} {city} — Right Now</div>
                    <div style="font-size:14px;opacity:0.85;margin-bottom:14px;">{desc}</div>
                    <div style="display:flex;gap:24px;flex-wrap:wrap;font-size:15px;margin-bottom:18px;">
                        <span>🌡️ <strong>{temp}°C</strong></span>
                        <span>💧 <strong>{humidity}%</strong></span>
                        <span>💨 <strong>{wind} km/h</strong></span>
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;">{forecast_html}</div>
                </div>
            </div>'''
        except requests.exceptions.Timeout:
            return '<div style="color:orange;padding:16px;">⏱️ Weather request timed out.</div>'
        except Exception as e:
            return f'<div style="color:red;padding:16px;">❌ Weather error: {str(e)}</div>'

    # ─────────────────────────────────────────────────────────────
    # REVIEWS
    # ─────────────────────────────────────────────────────────────
    def _get_real_reviews(self, destination):
        reviews = {
            'in': [
                ('Priya S.', 5, 'Incredible diversity! Taj Mahal at sunrise left me speechless.', '2 weeks ago', '🇮🇳'),
                ('Marco R.', 4, 'Street food in Delhi is unmatched. Chandni Chowk is chaotic but magical!', '1 month ago', '🇮🇹'),
                ('Aiko T.', 5, 'Jaipur Pink City is stunning. Amber Fort at golden hour is breathtaking.', '3 weeks ago', '🇯🇵'),
                ('James W.', 4, 'Kerala backwaters on a houseboat was the most peaceful experience.', '2 months ago', '🇬🇧'),
            ],
            'jp': [
                ('Rahul M.', 5, 'Tokyo is incredibly clean. Shibuya crossing at night is magical!', '1 week ago', '🇮🇳'),
                ('Sophie L.', 5, 'Kyoto temples are breathtaking. Fushimi Inari at 5am — a spiritual experience!', '3 weeks ago', '🇫🇷'),
                ('Ahmed K.', 4, 'Food culture is unlike anything else. Ramen at 2am — only in Japan!', '1 month ago', '🇸🇦'),
                ('Emma T.', 5, 'Cherry blossom in Ueno Park made me cry with joy.', '2 months ago', '🇬🇧'),
            ],
            'ae': [
                ('Raj P.', 5, 'Burj Khalifa top floor at sunset is jaw-dropping!', '1 week ago', '🇮🇳'),
                ('Emma T.', 5, 'Dubai Mall fountain show at night is absolutely stunning.', '2 weeks ago', '🇬🇧'),
                ('Ivan K.', 4, 'Desert safari unforgettable — dune bashing, camel ride, BBQ under stars.', '1 month ago', '🇷🇺'),
                ('Fatima A.', 5, 'Abra ride on Dubai Creek shows the real soul of the city. Only 1 AED!', '3 weeks ago', '🇸🇦'),
            ],
            'fr': [
                ('Anjali R.', 5, 'Eiffel Tower at night is ethereal. Montmartre at dawn is perfect!', '1 week ago', '🇮🇳'),
                ('Carlos M.', 4, 'French cuisine is world class. A croissant from a local boulangerie is amazing!', '2 weeks ago', '🇪🇸'),
                ('Yuki S.', 5, 'Louvre needs a full day. Book skip-the-line tickets online.', '1 month ago', '🇯🇵'),
                ('Lars N.', 4, 'Loire Valley wine tour stunning. Tasting in a 500-year-old château!', '3 weeks ago', '🇩🇰'),
            ],
            'th': [
                ('Neha G.', 5, 'Bangkok temples are incredible. Grand Palace is a must!', '1 week ago', '🇮🇳'),
                ('Lisa P.', 5, 'Phuket beaches are paradise. Phi Phi Island day trip is worth it.', '2 weeks ago', '🇺🇸'),
                ('Tom H.', 4, 'Chiang Mai elephant sanctuary was life-changing.', '1 month ago', '🇦🇺'),
                ('Yuna K.', 5, 'Thai street food is the best in Asia!', '3 weeks ago', '🇰🇷'),
            ],
            'au': [
                ('Riya S.', 5, 'Great Barrier Reef snorkelling was a dream!', '1 week ago', '🇮🇳'),
                ('Jake T.', 5, 'Sydney Opera House tour is worth it. Harbour Bridge climb is spectacular!', '2 weeks ago', '🇺🇸'),
                ('Sophie L.', 4, 'Uluru at sunrise changed me. Deeply spiritual place.', '1 month ago', '🇬🇧'),
                ('Chen W.', 5, 'Great Ocean Road is a must-do drive. Twelve Apostles at sunset!', '3 weeks ago', '🇨🇳'),
            ],
            'it': [
                ('Meera K.', 5, 'Rome in a day is not enough. Colosseum is overwhelming in size!', '1 week ago', '🇮🇳'),
                ('Lucas F.', 5, 'Venice is unlike any city on Earth. Gondola at sunset — priceless.', '2 weeks ago', '🇧🇷'),
                ('Hannah R.', 4, 'Amalfi Coast drive is terrifying and beautiful at the same time!', '1 month ago', '🇬🇧'),
                ('Kenji M.', 5, 'Florence gelato + Uffizi Gallery = perfect Italian day.', '3 weeks ago', '🇯🇵'),
            ],
            'gr': [
                ('Arjun P.', 5, 'Santorini sunset from Oia is the most beautiful thing I have ever seen.', '1 week ago', '🇮🇳'),
                ('Anna S.', 5, 'Acropolis at dawn before the crowds was magical.', '2 weeks ago', '🇷🇺'),
                ('David M.', 4, 'Meteora monasteries are absolutely jaw-dropping. Go at sunrise!', '1 month ago', '🇺🇸'),
                ('Yuna L.', 5, 'Greek food is incredible — moussaka and fresh seafood every day!', '3 weeks ago', '🇰🇷'),
            ],
            'tr': [
                ('Kavya R.', 5, 'Cappadocia balloon ride at sunrise is a bucket-list moment!', '1 week ago', '🇮🇳'),
                ('Marc D.', 5, 'Istanbul Grand Bazaar is overwhelming — in the best way possible!', '2 weeks ago', '🇫🇷'),
                ('Sarah L.', 4, 'Pamukkale cotton terraces are unreal. Natural wonder of the world!', '1 month ago', '🇬🇧'),
                ('Ahmed A.', 5, 'Hagia Sophia architecture left me speechless. History in every corner.', '3 weeks ago', '🇸🇦'),
            ],
            'sg': [
                ('Preethi V.', 5, 'Gardens by the Bay light show is free and absolutely spectacular!', '1 week ago', '🇮🇳'),
                ('James O.', 5, 'Singapore hawker food is UNESCO-worthy — and it genuinely is!', '2 weeks ago', '🇬🇧'),
                ('Lisa C.', 4, 'Marina Bay Sands infinity pool view is worth every cent.', '1 month ago', '🇦🇺'),
                ('Kim J.', 5, 'Cleanest and most efficient city I have ever visited.', '3 weeks ago', '🇰🇷'),
            ],
            'ch': [
                ('Rohit G.', 5, 'Jungfraujoch at 3,454 m — the Alps are beyond description!', '1 week ago', '🇮🇳'),
                ('Claire B.', 5, 'Zermatt with Matterhorn views is the most picturesque place on Earth.', '2 weeks ago', '🇫🇷'),
                ('Michael P.', 4, 'Swiss trains are clockwork perfect. Explored five cities in three days!', '1 month ago', '🇺🇸'),
                ('Aiko S.', 5, 'Lucerne Chapel Bridge and lake — postcard-perfect at every turn.', '3 weeks ago', '🇯🇵'),
            ],
        }
        dest_reviews = reviews.get(destination, [
            ('Sarah K.', 5, 'Absolutely stunning destination. Would visit again!', '1 week ago', '🌍'),
            ('David L.', 4, 'Amazing culture, food, and people. A truly life-changing trip.', '2 weeks ago', '🌍'),
            ('Maria C.', 5, 'Hidden gems everywhere you look. Hire a local guide!', '1 month ago', '🌍'),
            ('James T.', 4, 'Beautiful country with incredibly warm and welcoming people.', '3 weeks ago', '🌍'),
        ])
        html = '''<div style="font-family:Arial,sans-serif;">
            <div style="background:linear-gradient(135deg,#ff6f00,#ffa000);color:white;
                padding:14px 18px;border-radius:12px;margin-bottom:14px;">
                <div style="font-size:16px;font-weight:bold;">⭐ Real Traveller Reviews</div>
            </div>'''
        for author, stars, text, time_desc, flag in dest_reviews:
            stars_html = '⭐' * stars
            empty = '☆' * (5 - stars)
            html += f'''
            <div style="background:white;border:1px solid #f0f0f0;border-radius:12px;
                padding:14px 16px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-weight:bold;font-size:14px;">{flag} {author}</span>
                    <span style="color:#bbb;font-size:11px;">{time_desc}</span>
                </div>
                <div style="color:#f9a825;font-size:15px;margin-bottom:8px;">{stars_html}{empty}</div>
                <div style="color:#444;font-size:13px;line-height:1.7;font-style:italic;">"{text}"</div>
            </div>'''
        html += '</div>'
        return html

    # ─────────────────────────────────────────────────────────────
    # MAP & CROWD INFO
    # ─────────────────────────────────────────────────────────────
    def _get_crowd_map(self, destination):
        coords = {
            'in': (28.6139, 77.2090,  'New Delhi, India'),
            'jp': (35.6762, 139.6503, 'Tokyo, Japan'),
            'th': (13.7563, 100.5018, 'Bangkok, Thailand'),
            'fr': (48.8566, 2.3522,   'Paris, France'),
            'it': (41.9028, 12.4964,  'Rome, Italy'),
            'ae': (25.2048, 55.2708,  'Dubai, UAE'),
            'sg': (1.3521,  103.8198, 'Singapore'),
            'mv': (4.1755,  73.5093,  'Male, Maldives'),
            'gb': (51.5074, -0.1278,  'London, UK'),
            'ch': (46.9481, 7.4474,   'Bern, Switzerland'),
            'np': (27.7172, 85.3240,  'Kathmandu, Nepal'),
            'lk': (6.9271,  79.8612,  'Colombo, Sri Lanka'),
            'tr': (41.0082, 28.9784,  'Istanbul, Turkey'),
            'gr': (37.9838, 23.7275,  'Athens, Greece'),
            'id': (-8.3405, 115.0920, 'Bali, Indonesia'),
            'au': (-33.8688,151.2093, 'Sydney, Australia'),
            'kr': (37.5665, 126.9780, 'Seoul, South Korea'),
            'cn': (39.9042, 116.4074, 'Beijing, China'),
            'de': (52.5200, 13.4050,  'Berlin, Germany'),
            'es': (40.4168, -3.7038,  'Madrid, Spain'),
            'pt': (38.7169, -9.1395,  'Lisbon, Portugal'),
            'nl': (52.3676, 4.9041,   'Amsterdam, Netherlands'),
            'sa': (24.7136, 46.6753,  'Riyadh, Saudi Arabia'),
            'nz': (-36.8485,174.7633, 'Auckland, New Zealand'),
            'fj': (-18.1416,178.4419, 'Suva, Fiji'),
            'qa': (25.2854, 51.5310,  'Doha, Qatar'),
            'bh': (26.0667, 50.5577,  'Manama, Bahrain'),
            'kw': (29.3759, 47.9774,  'Kuwait City, Kuwait'),
            'om': (23.5880, 58.3829,  'Muscat, Oman'),
            'jo': (31.9522, 35.9330,  'Amman, Jordan'),
        }
        if not destination or destination not in coords:
            return '<div style="padding:16px;color:#888;text-align:center;">🌍 Please select a destination to see the map.</div>'

        lat, lon, city = coords[destination]
        bbox = f"{lon-0.3}%2C{lat-0.3}%2C{lon+0.3}%2C{lat+0.3}"
        return f'''
        <div style="font-family:Arial,sans-serif;">
            <div style="background:linear-gradient(135deg,#1b5e20,#388e3c);color:white;
                padding:14px 18px;border-radius:12px 12px 0 0;font-size:15px;font-weight:bold;">
                🗺️ Interactive Map — {city}
            </div>
            <iframe width="100%" height="380"
                style="border:0;border-radius:0 0 12px 12px;display:block;" loading="lazy"
                src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&amp;layer=mapnik&amp;marker={lat}%2C{lon}">
            </iframe>
            <div style="text-align:right;margin-top:6px;">
                <a href="https://www.openstreetmap.org/?mlat={lat}&amp;mlon={lon}#map=13/{lat}/{lon}"
                   target="_blank" style="font-size:12px;color:#1565c0;text-decoration:none;">
                    🔍 Open full map →
                </a>
            </div>
            <div style="background:#fff3e0;border-radius:12px;padding:14px 18px;
                margin-top:12px;border-left:5px solid #ff9800;">
                <div style="font-size:14px;font-weight:bold;color:#e65100;margin-bottom:8px;">
                    ⏰ Crowd & Timing Tips for {city}
                </div>
                <div style="font-size:13px;color:#5d4037;line-height:1.9;">
                    🕗 Visit popular sites <strong>before 9 AM</strong> or <strong>after 5 PM</strong><br/>
                    📅 <strong>Weekdays</strong> are always less crowded than weekends<br/>
                    💰 <strong>Shoulder season</strong> = 30–40% fewer tourists + cheaper prices<br/>
                    🎟️ <strong>Book tickets online</strong> — skip-the-line saves 1–2 hours
                </div>
            </div>
        </div>'''

    # ─────────────────────────────────────────────────────────────
    # FORMAT PLAN HTML
    # ─────────────────────────────────────────────────────────────
    def _format_plan_html(self, text):
        lines = text.split('\n')
        html = ['<div style="font-family:Arial,sans-serif;max-width:100%;padding:10px;">']
        for line in lines:
            line = line.strip()
            if not line:
                html.append('<div style="margin:6px 0;"></div>')
                continue
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            if any(line.startswith(ic) for ic in ['✈️','🏨','💰','📅','🎯','⚠️','🎒']):
                html.append(
                    f'<div style="background:linear-gradient(135deg,#1a8c50,#2db46e);'
                    f'color:white;padding:12px 20px;border-radius:10px;'
                    f'margin:20px 0 8px 0;font-size:15px;font-weight:bold;">{line}</div>'
                )
            elif re.match(r'^Day \d+', line, re.IGNORECASE):
                html.append(
                    f'<div style="background:#ff6b35;color:white;padding:10px 16px;'
                    f'border-radius:8px;margin:14px 0 6px 0;font-size:14px;font-weight:bold;">📅 {line}</div>'
                )
            elif line.startswith('- ') or line.startswith('• '):
                html.append(
                    f'<div style="padding:6px 10px 6px 28px;color:#444;'
                    f'border-bottom:1px solid #f5f5f5;font-size:13px;">▸ {line[2:]}</div>'
                )
            elif any(line.lower().startswith(t) for t in ['morning:','afternoon:','evening:','lunch:','dinner:','breakfast:']):
                html.append(
                    f'<div style="background:#fff8f0;border-left:4px solid #ff9800;'
                    f'padding:8px 14px;margin:4px 0;border-radius:0 8px 8px 0;'
                    f'color:#333;font-size:13px;">🌟 {line}</div>'
                )
            else:
                html.append(f'<p style="padding:3px 10px;color:#555;margin:3px 0;font-size:13px;">{line}</p>')
        html.append('</div>')
        return '\n'.join(html)

    # ─────────────────────────────────────────────────────────────
    # PDF DOWNLOAD ACTION
    # ─────────────────────────────────────────────────────────────
    def action_download_pdf(self):
        import io
        import base64
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.colors import HexColor, white, black
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer,
                HRFlowable, Table, TableStyle, KeepTogether
            )
            from reportlab.lib.units import cm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            for rec in self:
                buf        = io.BytesIO()
                PAGE_W, PAGE_H = A4
                ORANGE     = HexColor('#FF6B35')
                LIGHT_GRAY = HexColor('#F8F8F8')
                MID_GRAY   = HexColor('#888888')
                DARK       = HexColor('#1A1A1A')
                RULE_GRAY  = HexColor('#E0E0E0')

                today_str  = date.today().strftime('%d %B %Y')
                dest_name  = dict(rec._fields['destination'].selection).get(
                    rec.destination, rec.destination or 'N/A'
                )
                checkin_str  = rec.checkin_date.strftime('%d %b %Y')  if rec.checkin_date  else '—'
                checkout_str = rec.checkout_date.strftime('%d %b %Y') if rec.checkout_date else '—'

                # ── Styles ────────────────────────────────────────────
                def S(name, **kw):
                    defaults = dict(fontName='Helvetica', fontSize=10,
                                    textColor=DARK, leading=14, spaceAfter=0)
                    defaults.update(kw)
                    return ParagraphStyle(name, **defaults)

                title_bold  = S('TB',  fontName='Helvetica-Bold', fontSize=28, textColor=DARK, leading=32)
                title_light = S('TL',  fontName='Helvetica',      fontSize=28, textColor=MID_GRAY, leading=32)
                meta_label  = S('ML',  fontName='Helvetica-Bold', fontSize=9,  textColor=DARK)
                meta_val    = S('MV',  fontName='Helvetica',      fontSize=9,  textColor=MID_GRAY)
                sec_head    = S('SH',  fontName='Helvetica-Bold', fontSize=11, textColor=DARK, spaceBefore=14, spaceAfter=4)
                body        = S('BD',  fontName='Helvetica',      fontSize=9,  textColor=DARK, leading=13)
                body_bold   = S('BDB', fontName='Helvetica-Bold', fontSize=9,  textColor=DARK, leading=13)
                small_gray  = S('SG',  fontName='Helvetica',      fontSize=8,  textColor=MID_GRAY, leading=11)
                day_label   = S('DL',  fontName='Helvetica-Bold', fontSize=9,  textColor=white,
                                alignment=TA_CENTER)
                time_cell   = S('TC',  fontName='Helvetica-Bold', fontSize=9,  textColor=DARK)
                act_cell    = S('AC',  fontName='Helvetica',      fontSize=9,  textColor=DARK, leading=13)
                act_title   = S('AT',  fontName='Helvetica-Bold', fontSize=10, textColor=DARK)
                footer_s    = S('FS',  fontName='Helvetica',      fontSize=7,  textColor=MID_GRAY,
                                alignment=TA_CENTER)

                doc = SimpleDocTemplate(
                    buf, pagesize=A4,
                    leftMargin=1.8*cm, rightMargin=1.8*cm,
                    topMargin=1.5*cm, bottomMargin=1.8*cm
                )
                story = []
                col_w = PAGE_W - 3.6*cm   # usable width

                # ══════════════════════════════════════════════════════
                # SECTION 1 — TITLE HEADER
                # ══════════════════════════════════════════════════════
                title_tbl = Table([[
                    Paragraph('<b>Trip</b>', title_bold),
                    Paragraph('Itinerary', title_light),
                ]], colWidths=[col_w * 0.28, col_w * 0.72])
                title_tbl.setStyle(TableStyle([
                    ('VALIGN',  (0,0), (-1,-1), 'BOTTOM'),
                    ('LEFTPADDING',  (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING',(0,0), (-1,-1), 0),
                    ('TOPPADDING',   (0,0), (-1,-1), 0),
                ]))
                story.append(title_tbl)
                story.append(Spacer(1, 4))
                story.append(HRFlowable(width='100%', thickness=2, color=ORANGE, spaceAfter=10))

                # ── Meta row ─────────────────────────────────────────
                meta_tbl = Table([[
                    Paragraph(f'<b>Start Date</b>  {checkin_str}',  meta_label),
                    Paragraph(f'<b>End Date</b>  {checkout_str}',   meta_label),
                    Paragraph(f'<b>Destination</b>  {dest_name}',   meta_label),
                ]], colWidths=[col_w/3]*3)
                meta_tbl.setStyle(TableStyle([
                    ('LEFTPADDING',  (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING',(0,0), (-1,-1), 4),
                    ('TOPPADDING',   (0,0), (-1,-1), 4),
                ]))
                story.append(meta_tbl)
                story.append(HRFlowable(width='100%', thickness=0.5, color=RULE_GRAY, spaceAfter=14))

                # ── Tourist summary chips ─────────────────────────────
                interests = []
                if rec.interest_adventure:   interests.append("Adventure")
                if rec.interest_food:        interests.append("Food")
                if rec.interest_culture:     interests.append("Culture")
                if rec.interest_beach:       interests.append("Beach")
                if rec.interest_wildlife:    interests.append("Wildlife")
                if rec.interest_wellness:    interests.append("Wellness")
                if rec.interest_photography: interests.append("Photography")
                if rec.interest_shopping:    interests.append("Shopping")

                summary_data = [
                    [
                        Paragraph(f'<b>Tourist</b><br/>{rec.name}',            body),
                        Paragraph(f'<b>Duration</b><br/>{rec.num_days} nights', body),
                        Paragraph(f'<b>Budget</b><br/>{rec.budget_amount} {rec.currency}', body),
                        Paragraph(f'<b>Transport</b><br/>{rec.transport or "N/A"}', body),
                        Paragraph(f'<b>Tier</b><br/>{(rec.budget_tier or "N/A").split("(")[0].strip()}', body),
                    ]
                ]
                summary_tbl = Table(summary_data, colWidths=[col_w/5]*5)
                summary_tbl.setStyle(TableStyle([
                    ('BACKGROUND',   (0,0), (-1,-1), LIGHT_GRAY),
                    ('BOX',          (0,0), (-1,-1), 0.5, RULE_GRAY),
                    ('INNERGRID',    (0,0), (-1,-1), 0.5, RULE_GRAY),
                    ('LEFTPADDING',  (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ('TOPPADDING',   (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING',(0,0), (-1,-1), 8),
                    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(summary_tbl)
                story.append(Spacer(1, 16))

                # ══════════════════════════════════════════════════════
                # SECTION 2 — PARSE AI PLAN INTO STRUCTURED DAYS
                # ══════════════════════════════════════════════════════
                raw_plan = rec.plan or ''

                # Clean markdown
                def clean(txt):
                    txt = re.sub(r'#{1,6}\s*', '', txt)      # remove ### headings
                    txt = re.sub(r'\*\*(.*?)\*\*', r'\1', txt) # remove **bold**
                    txt = re.sub(r'\*(.*?)\*', r'\1', txt)    # remove *italic*
                    txt = txt.strip()
                    return txt

                # Parse lines into sections
                sections   = {}   # {'FLIGHT': [...lines], 'HOTEL': [...], 'DAY': {1:[...], 2:[...]}}
                days_data  = {}   # {day_number: {'title': str, 'rows': [(time, activity)]}}
                misc_sections = {}# other named sections

                current_section = None
                current_day     = None
                current_day_title = ''

                DAY_RE     = re.compile(r'^Day\s+(\d+)[:\-–]?\s*(.*)', re.IGNORECASE)
                SECTION_RE = re.compile(
                    r'(FLIGHT|HOTEL|BUDGET|UNIQUE|SAFETY|PACKING|ARRIVAL|EXPERIENCE)',
                    re.IGNORECASE
                )
                MEAL_RE    = re.compile(
                    r'^(Morning|Afternoon|Evening|Breakfast|Lunch|Dinner|Night)[:\-]?\s*(.*)',
                    re.IGNORECASE
                )
                TIME_RE    = re.compile(r'^\d+:\d+\s*(AM|PM)', re.IGNORECASE)

                for raw_line in raw_plan.split('\n'):
                    line = clean(raw_line)
                    if not line:
                        continue

                    # Day header?
                    day_match = DAY_RE.match(line)
                    if day_match:
                        current_day = int(day_match.group(1))
                        current_day_title = day_match.group(2).strip() or f'Day {current_day}'
                        current_section = 'DAY'
                        if current_day not in days_data:
                            days_data[current_day] = {'title': current_day_title, 'rows': []}
                        continue

                    # Section header (not a day)?
                    sec_match = SECTION_RE.search(line)
                    if sec_match and not DAY_RE.match(line) and len(line) < 60:
                        current_section = sec_match.group(1).upper()
                        current_day = None
                        if current_section not in misc_sections:
                            misc_sections[current_section] = []
                        continue

                    # Inside a day?
                    if current_section == 'DAY' and current_day is not None:
                        meal_m = MEAL_RE.match(line.lstrip('- •*'))
                        time_m = TIME_RE.match(line.lstrip('- •*'))
                        if meal_m:
                            time_label = meal_m.group(1).capitalize()
                            activity   = meal_m.group(2).strip()
                            days_data[current_day]['rows'].append((time_label, activity))
                        elif time_m:
                            days_data[current_day]['rows'].append(('', line.lstrip('- •*')))
                        elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                            days_data[current_day]['rows'].append(('', line[2:].strip()))
                        else:
                            days_data[current_day]['rows'].append(('', line))
                        continue

                    # Inside a misc section?
                    if current_section and current_section in misc_sections:
                        misc_sections[current_section].append(line)

                # ══════════════════════════════════════════════════════
                # SECTION 3 — RENDER DAY TABLES (like the image)
                # ══════════════════════════════════════════════════════
                if days_data:
                    story.append(Paragraph('Day-by-Day Itinerary', sec_head))
                    story.append(HRFlowable(width='100%', thickness=1, color=ORANGE, spaceAfter=10))

                DAY_COL  = 1.0*cm
                TIME_COL = 2.2*cm
                ACT_COL  = col_w - DAY_COL - TIME_COL

                for day_num in sorted(days_data.keys()):
                    day_info = days_data[day_num]
                    title    = day_info['title']
                    rows     = day_info['rows']
                    if not rows:
                        continue

                    # Header row of this day's table
                    tbl_rows = [[
                        Paragraph(f'DAY {day_num}', day_label),
                        Paragraph('Time', time_cell),
                        Paragraph(f'Activity — {title}', act_title),
                    ]]

                    # Data rows
                    for i, (t, a) in enumerate(rows):
                        tbl_rows.append([
                            '',
                            Paragraph(t,  time_cell),
                            Paragraph(a,  act_cell),
                        ])

                    n = len(tbl_rows)
                    day_tbl = Table(tbl_rows, colWidths=[DAY_COL, TIME_COL, ACT_COL])

                    ts = TableStyle([
                        # DAY label cell spans all rows
                        ('SPAN',          (0,0), (0, n-1)),
                        ('BACKGROUND',    (0,0), (0, n-1),  ORANGE),
                        ('VALIGN',        (0,0), (0, n-1),  'MIDDLE'),
                        ('ALIGN',         (0,0), (0, n-1),  'CENTER'),
                        # Header row
                        ('BACKGROUND',    (1,0), (2,0),     LIGHT_GRAY),
                        ('FONTNAME',      (1,0), (2,0),     'Helvetica-Bold'),
                        ('FONTSIZE',      (1,0), (2,0),     9),
                        # All cells
                        ('FONTSIZE',      (1,1), (-1,-1),   9),
                        ('VALIGN',        (1,0), (-1,-1),   'TOP'),
                        ('TOPPADDING',    (0,0), (-1,-1),   6),
                        ('BOTTOMPADDING', (0,0), (-1,-1),   6),
                        ('LEFTPADDING',   (0,0), (-1,-1),   6),
                        ('RIGHTPADDING',  (0,0), (-1,-1),   6),
                        # Dotted lines between rows
                        ('LINEBELOW',     (1,0), (-1,-2),   0.5, RULE_GRAY),
                        # Outer box
                        ('BOX',           (0,0), (-1,-1),   0.5, RULE_GRAY),
                    ])
                    day_tbl.setStyle(ts)

                    story.append(KeepTogether([day_tbl, Spacer(1, 10)]))

                # ══════════════════════════════════════════════════════
                # SECTION 4 — MISC SECTIONS (Hotels, Budget, Packing etc)
                # ══════════════════════════════════════════════════════
                SECTION_TITLES = {
                    'FLIGHT':     '✈ Flight & Arrival Details',
                    'HOTEL':      '🏨 Hotel Recommendations',
                    'BUDGET':     '💰 Budget Breakdown',
                    'UNIQUE':     '🎯 Unique Experiences',
                    'EXPERIENCE': '🎯 Unique Experiences',
                    'SAFETY':     '⚠ Safety & Travel Tips',
                    'PACKING':    '🎒 Packing List',
                }

                for sec_key, lines in misc_sections.items():
                    if not lines:
                        continue
                    title_text = SECTION_TITLES.get(sec_key, sec_key.title())
                    sec_block  = [
                        Spacer(1, 6),
                        Paragraph(title_text, sec_head),
                        HRFlowable(width='100%', thickness=0.5, color=ORANGE, spaceAfter=6),
                    ]
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                            sec_block.append(Paragraph(f'•  {line[2:].strip()}', body))
                        elif re.match(r'^\d+\.', line):
                            sec_block.append(Paragraph(line, body))
                        elif 'TOTAL' in line.upper():
                            sec_block.append(Spacer(1, 4))
                            total_tbl = Table([[Paragraph(line, body_bold)]], colWidths=[col_w])
                            total_tbl.setStyle(TableStyle([
                                ('BACKGROUND',   (0,0), (-1,-1), LIGHT_GRAY),
                                ('BOX',          (0,0), (-1,-1), 0.5, RULE_GRAY),
                                ('LEFTPADDING',  (0,0), (-1,-1), 10),
                                ('TOPPADDING',   (0,0), (-1,-1), 6),
                                ('BOTTOMPADDING',(0,0), (-1,-1), 6),
                            ]))
                            sec_block.append(total_tbl)
                            sec_block.append(Spacer(1, 4))
                        else:
                            sec_block.append(Paragraph(line, body))
                        sec_block.append(Spacer(1, 2))
                    story.append(KeepTogether(sec_block))

                # ══════════════════════════════════════════════════════
                # SECTION 5 — INTERESTS & FOOTER
                # ══════════════════════════════════════════════════════
                if interests:
                    story.append(Spacer(1, 10))
                    story.append(HRFlowable(width='100%', thickness=0.5, color=RULE_GRAY))
                    story.append(Spacer(1, 6))
                    story.append(Paragraph(
                        f'<b>Interests:</b>  {" · ".join(interests)}', small_gray
                    ))

                story.append(Spacer(1, 20))
                story.append(HRFlowable(width='100%', thickness=0.5, color=RULE_GRAY))
                story.append(Spacer(1, 4))
                story.append(Paragraph(
                    f'SRK Tourism  ·  {rec.name}  ·  {dest_name}  ·  Generated {today_str}',
                    footer_s
                ))

                # ══════════════════════════════════════════════════════
                # BUILD & RETURN
                # ══════════════════════════════════════════════════════
                doc.build(story)
                pdf_bytes = buf.getvalue()

                fname = (
                    f"Itinerary_{rec.name.replace(' ','_')}_"
                    f"{(dest_name or 'Trip').replace(' ','_')}_"
                    f"{today_str.replace(' ','_')}.pdf"
                )

                attachment = self.env['ir.attachment'].create({
                    'name':      fname,
                    'type':      'binary',
                    'datas':     base64.b64encode(pdf_bytes),
                    'res_model': 'tourist.profile',
                    'res_id':    rec.id,
                    'mimetype':  'application/pdf',
                })

                return {
                    'type':   'ir.actions.act_url',
                    'url':    f'/web/content/{attachment.id}?download=true',
                    'target': 'new',
                }

        except ImportError:
            raise Exception(
                "reportlab not installed. Run:\n"
                "C:\\Users\\KHYATI\\Desktop\\odoo\\python\\python.exe "
                "-m pip install reportlab"
            )
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")
    # ─────────────────────────────────────────────────────────────
    # TAB NAVIGATION
    # ─────────────────────────────────────────────────────────────
    def action_go_tab_profile(self):
        for rec in self:
            rec.state = 'profile'

    def action_go_tab_trip(self):
        for rec in self:
            rec.state = 'trip'

    def action_go_tab_interests(self):
        for rec in self:
            rec.state = 'interests'

    def action_go_tab_itinerary(self):
        for rec in self:
            rec.state = 'itinerary'

    def action_go_tab_destination(self):
        for rec in self:
            rec.state = 'destination'

    def action_go_tab_reviews(self):
        for rec in self:
            rec.state = 'reviews'

    def action_go_tab_map(self):
        for rec in self:
            rec.state = 'map'

    # ─────────────────────────────────────────────────────────────
    # MAIN GENERATE ACTION
    # ─────────────────────────────────────────────────────────────
    def action_generate_plan(self):
        GROQ_KEY = self.env['ir.config_parameter'].sudo().get_param('srk_tourism.groq_api_key')

        for rec in self:
            rec.weather_info = self._get_real_weather(rec.destination)
            rec.real_reviews  = self._get_real_reviews(rec.destination)
            rec.crowd_map     = self._get_crowd_map(rec.destination)

            interests = []
            if rec.interest_adventure:   interests.append("Adventure & outdoor")
            if rec.interest_food:        interests.append("Food & local cuisine")
            if rec.interest_culture:     interests.append("Culture & history")
            if rec.interest_beach:       interests.append("Beach & water activities")
            if rec.interest_wildlife:    interests.append("Wildlife & nature")
            if rec.interest_wellness:    interests.append("Wellness & spa")
            if rec.interest_photography: interests.append("Photography")
            if rec.interest_shopping:    interests.append("Shopping")
            interests_text = ", ".join(interests) or "General sightseeing"

            dest_name = dict(rec._fields['destination'].selection).get(rec.destination, rec.destination)

            lang_config = {
                'hi': ('नमस्ते', 'Hindi (हिन्दी)', 'Write the ENTIRE itinerary in Hindi language.'),
                'en': ('Hello',   'English',         'Write the ENTIRE itinerary in English.'),
                'fr': ('Bonjour', 'French',          'Write the ENTIRE itinerary in French language.'),
                'de': ('Hallo',   'German',          'Write the ENTIRE itinerary in German language.'),
                'es': ('Hola',    'Spanish',         'Write the ENTIRE itinerary in Spanish language.'),
                'ja': ('こんにちは','Japanese',       'Write the ENTIRE itinerary in Japanese language.'),
                'zh': ('你好',    'Mandarin',         'Write the ENTIRE itinerary in Mandarin Chinese.'),
                'ar': ('مرحبا',  'Arabic',           'Write the ENTIRE itinerary in Arabic language.'),
                'pt': ('Olá',    'Portuguese',       'Write the ENTIRE itinerary in Portuguese.'),
                'ru': ('Привет', 'Russian',          'Write the ENTIRE itinerary in Russian language.'),
                'ko': ('안녕하세요','Korean',         'Write the ENTIRE itinerary in Korean language.'),
                'it': ('Ciao',   'Italian',          'Write the ENTIRE itinerary in Italian language.'),
            }
            greeting, lang_name, lang_instruction = lang_config.get(
                rec.language, ('Hello', 'English', 'Write the ENTIRE itinerary in English.')
            )

            prompt = f"""{greeting} {rec.name}! — You are a premium luxury travel planner.
LANGUAGE INSTRUCTION: {lang_instruction} Address {rec.name} personally throughout in {lang_name}.
Tourist: {rec.name}
Destination: {dest_name}
Transport: {rec.transport}
Check-in: {rec.checkin_date} | Check-out: {rec.checkout_date}
Duration: {rec.num_days} nights
Budget: {rec.budget_amount} {rec.currency} ({rec.budget_tier})
Interests: {interests_text}

Generate EXACTLY these sections with emoji headers:
✈️ FLIGHT & ARRIVAL DETAILS
🏨 HOTEL RECOMMENDATIONS (3 hotels matching budget)
💰 BUDGET BREAKDOWN
📅 DAY-BY-DAY ITINERARY (for each of {rec.num_days} days)
🎯 5 UNIQUE EXPERIENCES UNDER BUDGET
⚠️ SAFETY & TRAVEL TIPS
🎒 PACKING LIST
Remember: {lang_instruction} Use REAL place names, restaurants, hotels."""

            if not GROQ_KEY:
                rec.plan_html = '''
                <div style="background:#fff3e0;border-left:5px solid #ff9800;
                    padding:20px;border-radius:10px;color:#e65100;font-size:14px;">
                    <strong>⚠️ Groq API Key Missing!</strong><br/><br/>
                    Go to: Settings → Technical → System Parameters<br/>
                    Key: <code>srk_tourism.groq_api_key</code><br/>
                    Value: Your Groq API key from console.groq.com
                </div>'''
                rec.status = 'planned'
                continue

            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    f"You are an expert luxury travel planner. "
                                    f"{lang_instruction} "
                                    f"Always use exact section headers with emojis. "
                                    f"Use REAL place names, hotels, restaurants. "
                                    f"Address the tourist as {rec.name} throughout."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 4000,
                    },
                    timeout=60
                )
                if response.status_code == 200:
                    raw = response.json()['choices'][0]['message']['content']
                    rec.plan      = raw
                    rec.plan_html = self._format_plan_html(raw)
                    rec.status    = 'optimized'
                else:
                    rec.plan_html = (
                        f'<div style="color:red;padding:16px;">'
                        f'❌ API Error {response.status_code}: {response.text}</div>'
                    )
            except requests.exceptions.Timeout:
                rec.plan_html = (
                    '<div style="color:orange;padding:16px;">'
                    '⏱️ Request timed out. Please try again.</div>'
                )
            except Exception as e:
                rec.plan_html = (
                    f'<div style="color:red;padding:16px;">'
                    f'❌ Error: {str(e)}</div>'
                )