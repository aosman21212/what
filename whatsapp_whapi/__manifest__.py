# -*- coding: utf-8 -*-
# =============================================================================
#  WhatsApp Whapi
# -----------------------------------------------------------------------------
#  Location  : King Abdulaziz Branch Road, Riyadh, Saudi Arabia
#  Email     : sales@leapai.ai
#  Phone     : +966 53 553 3627
#  Website   : https://leapai.ai
#  Developer : Abdulkaraim Osman — Tech Manager | Backend Engineer | DevOps Engineer
#              at Bab International Corp For Specialized Services
#  LinkedIn  : https://www.linkedin.com/in/abdulkaraim-o-385b7a110/
# =============================================================================
{
    'name': 'WhatsApp Whapi',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'WhatsApp integration via Whapi.Cloud API',
    'description': """
Standalone WhatsApp inbox for Odoo 19 using Whapi.Cloud (gate.whapi.cloud).
Send and receive messages, manage chats, contacts, groups, media, newsletters,
and business catalog via REST API and webhooks.

**Author:** leapai.ai
**Website:** https://leapai.ai/en/
**Support:** abdzoro89@gmail.com
**Maintainer:** a.osman@bab.com.sa
    """,
    'author': 'leapai.ai',
    'maintainer': 'Abdulkaraim Osman',
    'support': 'sales@leapai.ai',
    'website': 'https://leapai.ai/en/',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/whatsapp_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/whatsapp_channel_views.xml',
        'views/whatsapp_chat_views.xml',
        'views/whatsapp_message_views.xml',
        'views/whatsapp_contact_views.xml',
        'views/whatsapp_group_views.xml',
        'views/whatsapp_media_views.xml',
        'views/whatsapp_newsletter_views.xml',
        'views/whatsapp_product_views.xml',
        'views/whatsapp_collection_views.xml',
        'views/whatsapp_order_views.xml',
        'views/whatsapp_api_log_views.xml',
        'views/whatsapp_inbox_action.xml',
        'views/whatsapp_menus.xml',
        'wizards/whatsapp_qr_login_views.xml',
        'wizards/whatsapp_send_message_views.xml',
        'wizards/whatsapp_check_phones_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'whatsapp_whapi/static/src/components/whapi_inbox/whapi_inbox.js',
            'whatsapp_whapi/static/src/components/whapi_inbox/whapi_inbox.xml',
            'whatsapp_whapi/static/src/components/whapi_inbox/whapi_inbox.scss',
        ],
    },
    'installable': True,
    'application': True,
}
