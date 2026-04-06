{
    'name': 'SRK Tourism',
    'version': '2.0',
    'category': 'Services',
    'summary': 'AI-Powered Tourism ERP',
    'author': 'SRK Tourism',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/tourist_view.xml',
        'views/booking_view.xml',
        'views/safety_view.xml',
        'views/analytics_view.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'srk_tourism_erp/static/src/css/tourism.css',
        ],
    },
}