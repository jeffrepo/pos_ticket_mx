# -*- coding: utf-8 -*-
{
    'name': "Ticket POS MX",

    'summary': """ Desarrollo de ticket """,

    'description': """
        Ticket personalizado para el punto de venta
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['point_of_sale'],

    'data': [
        # 'views/templates.xml',
    ],
    'assets':{
        'point_of_sale.assets': [
            'pos_ticket_mx/static/src/css/pos_ticket_mx.css',
            'pos_ticket_mx/static/src/js/qrcode.js',
            # 'pos_ticket_mx/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'pos_ticket_mx/static/src/js/Screens/ReceiptScreen/OrderReceipt.js',
            'pos_ticket_mx/static/src/js/models.js',
        ],
        'web.assets_qweb':[
            'pos_ticket_mx/static/src/xml/**/*',
        ],
    },
    'license': 'LGPL-3',

    'installable': True,
    'auto_install': False,
}
