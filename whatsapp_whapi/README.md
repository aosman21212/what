# WhatsApp Whapi (Odoo 19)

Standalone WhatsApp integration for Odoo 19 using [Whapi.Cloud](https://whapi.cloud) (`https://gate.whapi.cloud`).

## Features

- Channel configuration (API token, health check, QR login)
- Webhook receiver for messages, statuses, chats, contacts, groups, presences
- Standalone inbox UI (OWL)
- Send text, media, location, polls, interactive, carousel, and more
- Contacts, groups, media library, newsletters
- Business catalog: products, collections, orders
- API request logging (Manager)

## Requirements

- Odoo 19
- Python package: `requests`
- Whapi.Cloud account and channel token
- Public HTTPS URL for webhooks (use ngrok for local dev)

## Installation

1. Copy the `whatsapp_whapi` folder into your Odoo addons path.
2. Install Python dependency: `pip install requests`
3. Update `addons_path` and restart Odoo.
4. Install **WhatsApp Whapi** from Apps.
5. Assign users to **WhatsApp User** or **WhatsApp Manager** groups.

## Setup

1. Go to **WhatsApp > Configuration > Channels**.
2. Create a channel and paste your Whapi Bearer token.
3. Set **web.base.url** in Odoo (Settings > Technical > Parameters) to your public URL.
4. Click **Register Webhooks** (registers `https://your-odoo/whatsapp/whapi/webhook/<secret>`).
5. Click **QR Login**, scan with WhatsApp, then **Check Connected**.
6. Click **Sync Profile** and **Open Inbox**.

## Webhook URL

```
{web.base.url}/whatsapp/whapi/webhook/{webhook_secret}
```

The `webhook_secret` is shown on the channel form.

## Whapi panel

1. Create a channel at [panel.whapi.cloud](https://panel.whapi.cloud).
2. Copy the API token into Odoo.
3. Optionally test webhook from Whapi or Odoo **Test Webhook** button.

## Support

- **Module support:** abdzoro89@gmail.com  
- **Maintainer:** a.osman@bab.com.sa  
- **Author:** [leapai.ai](https://leapai.ai/en/)  
- **Whapi API:** [whapi.cloud](https://whapi.cloud) — care@whapi.cloud
