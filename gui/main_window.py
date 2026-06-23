# gui/main_window.py
import sys
import re
import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QPushButton, QProgressBar, QLabel, QLineEdit,
    QGroupBox, QSpinBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QByteArray

from gui.worker import CheckerWorker
from gui.login_dialog import LoginDialog
from core.checker import get_card_brand, generate_luhn_number, parse_cc_line

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MrCardChecker – Premium CC Validator")
        self.setGeometry(100, 100, 1000, 780)
        self.setMinimumSize(950, 750)

        # Load logo from URL
        self.load_logo_from_url("https://img.icons8.com/fluency/96/bank-card-back-side.png")

        self.worker = None
        self.is_running = False
        self.logged_in = False
        self.session = None
        self.user_plan = 'none'
        self.plan_active = False

        self.init_ui()

    def load_logo_from_url(self, url):
        """Load application icon from URL and set as window icon."""
        try:
            import urllib.request
            from PyQt5.QtGui import QPixmap, QIcon
            import io

            response = urllib.request.urlopen(url)
            image_data = response.read()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            if not pixmap.isNull():
                self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            print(f"Could not load logo from URL: {e}")

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------- HEADER (Premium Design) ----------
        header = QFrame()
        header.setObjectName("premiumHeader")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Logo + Title
        logo_label = QLabel()
        logo_label.setFixedSize(50, 50)
        try:
            import urllib.request
            from PyQt5.QtGui import QPixmap
            import io
            response = urllib.request.urlopen("https://img.icons8.com/fluency/96/bank-card-back-side.png")
            pixmap = QPixmap()
            pixmap.loadFromData(response.read())
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            logo_label.setText("💳")
            logo_label.setStyleSheet("font-size: 32px;")

        title_layout = QVBoxLayout()
        title_label = QLabel("MrCardChecker")
        title_label.setObjectName("appTitle")
        subtitle_label = QLabel("Advanced Credit Card Validator & BIN Tool Suite")
        subtitle_label.setObjectName("appSubtitle")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Links (Website & Telegram)
        links_layout = QHBoxLayout()
        links_layout.setSpacing(15)

        website_btn = QPushButton("🌐 Website")
        website_btn.setObjectName("linkBtn")
        website_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://mrcardchecker.live")))
        links_layout.addWidget(website_btn)

        telegram_btn = QPushButton("✈️ Telegram")
        telegram_btn.setObjectName("linkBtn")
        telegram_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/mrcardcheckeradmin_new")))
        links_layout.addWidget(telegram_btn)

        header_layout.addLayout(links_layout)

        main_layout.addWidget(header)

        # ---------- TABS ----------
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.free_tab = self.create_free_tab()
        self.premium_tab = self.create_premium_tab()
        self.bin_tab = self.create_bin_tab()
        self.gen_tab = self.create_gen_tab()

        self.tabs.addTab(self.free_tab, "🔓 CCN Gate 1 (Free)")
        self.tabs.addTab(self.premium_tab, "🔒 CCN3 Gate (Premium)")
        self.tabs.addTab(self.bin_tab, "🔍 BIN Checker")
        self.tabs.addTab(self.gen_tab, "⚙️ BIN Generator")

        main_layout.addWidget(self.tabs)

        # ---------- STATUS BAR ----------
        status_frame = QFrame()
        status_frame.setObjectName("statusBarFrame")
        status_frame.setFixedHeight(35)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 5, 15, 5)

        self.status_label = QLabel("🟢 Ready")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # Version info
        version_label = QLabel("v2.0 | © 2026 MrCardChecker")
        version_label.setObjectName("versionLabel")
        status_layout.addWidget(version_label)

        main_layout.addWidget(status_frame)

    # ---------- FREE CHECKER TAB ----------
    def create_free_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        input_group = QGroupBox("📝 Card Input (NUMBER|MM|YY|CVV)")
        input_group.setObjectName("inputGroup")
        input_layout = QVBoxLayout()
        self.free_input = QTextEdit()
        self.free_input.setPlaceholderText("Example:\n4532015112830366|12|26|123\n5105105105105100|01|25|456")
        self.free_input.setObjectName("inputConsole")
        input_layout.addWidget(self.free_input)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Control buttons
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.free_start_btn = QPushButton("▶️ Start Checking")
        self.free_start_btn.setObjectName("startBtn")
        self.free_start_btn.clicked.connect(self.start_free_check)

        self.free_stop_btn = QPushButton("⏹️ Stop")
        self.free_stop_btn.setObjectName("stopBtn")
        self.free_stop_btn.clicked.connect(self.stop_check)
        self.free_stop_btn.setEnabled(False)

        # Clear buttons
        self.free_clear_log_btn = QPushButton("🗑️ Clear Log")
        self.free_clear_log_btn.setObjectName("clearBtn")
        self.free_clear_log_btn.clicked.connect(lambda: self.free_output.clear())

        self.free_clear_cards_btn = QPushButton("🧹 Clear Cards")
        self.free_clear_cards_btn.setObjectName("clearBtn")
        self.free_clear_cards_btn.clicked.connect(lambda: self.free_input.clear())

        ctrl_layout.addWidget(self.free_start_btn)
        ctrl_layout.addWidget(self.free_stop_btn)
        ctrl_layout.addWidget(self.free_clear_log_btn)
        ctrl_layout.addWidget(self.free_clear_cards_btn)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        self.free_progress = QProgressBar()
        self.free_progress.setVisible(False)
        layout.addWidget(self.free_progress)

        output_group = QGroupBox("📋 Output Log")
        output_group.setObjectName("outputGroup")
        out_layout = QVBoxLayout()
        self.free_output = QTextEdit()
        self.free_output.setReadOnly(True)
        self.free_output.setObjectName("outputConsole")
        out_layout.addWidget(self.free_output)
        output_group.setLayout(out_layout)
        layout.addWidget(output_group)

        return tab

    def start_free_check(self):
        text = self.free_input.toPlainText().strip()
        if not text:
            self.free_output.append("❌ Please enter card numbers.")
            return
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            self.free_output.append("❌ No valid lines found.")
            return

        self.free_output.clear()
        self.free_progress.setVisible(True)
        self.free_progress.setMaximum(len(lines))
        self.free_progress.setValue(0)
        self.free_start_btn.setEnabled(False)
        self.free_stop_btn.setEnabled(True)
        self.is_running = True
        self.status_label.setText("🔄 Processing free check...")

        self.worker = CheckerWorker(lines, premium=False, session=None)
        self.worker.progress.connect(self.free_progress.setValue)
        self.worker.result.connect(self.free_output.append)
        self.worker.finished.connect(self.free_check_finished)
        self.worker.start()

    def free_check_finished(self):
        self.is_running = False
        self.free_start_btn.setEnabled(True)
        self.free_stop_btn.setEnabled(False)
        self.free_progress.setVisible(False)
        self.status_label.setText("✅ Free check finished.")

    # ---------- PREMIUM TAB ----------
    def create_premium_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Status row
        status_layout = QHBoxLayout()
        self.premium_status_label = QLabel("🔐 Not logged in")
        self.premium_status_label.setObjectName("premiumStatus")
        self.premium_login_btn = QPushButton("🔑 Login")
        self.premium_login_btn.setObjectName("loginBtn")
        self.premium_login_btn.clicked.connect(self.show_login_dialog)

        status_layout.addWidget(self.premium_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.premium_login_btn)
        layout.addLayout(status_layout)

        input_group = QGroupBox("💳 Premium Card Input")
        input_group.setObjectName("inputGroup")
        input_layout = QVBoxLayout()
        self.premium_input = QTextEdit()
        self.premium_input.setPlaceholderText("4532015112830366|12|26|123")
        self.premium_input.setObjectName("inputConsole")
        input_layout.addWidget(self.premium_input)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.premium_start_btn = QPushButton("▶️ Start Checking")
        self.premium_start_btn.setObjectName("startBtn")
        self.premium_start_btn.clicked.connect(self.start_premium_check)
        self.premium_start_btn.setEnabled(False)

        self.premium_stop_btn = QPushButton("⏹️ Stop")
        self.premium_stop_btn.setObjectName("stopBtn")
        self.premium_stop_btn.clicked.connect(self.stop_check)
        self.premium_stop_btn.setEnabled(False)

        # Clear buttons
        self.premium_clear_log_btn = QPushButton("🗑️ Clear Log")
        self.premium_clear_log_btn.setObjectName("clearBtn")
        self.premium_clear_log_btn.clicked.connect(lambda: self.premium_output.clear())

        self.premium_clear_cards_btn = QPushButton("🧹 Clear Cards")
        self.premium_clear_cards_btn.setObjectName("clearBtn")
        self.premium_clear_cards_btn.clicked.connect(lambda: self.premium_input.clear())

        ctrl_layout.addWidget(self.premium_start_btn)
        ctrl_layout.addWidget(self.premium_stop_btn)
        ctrl_layout.addWidget(self.premium_clear_log_btn)
        ctrl_layout.addWidget(self.premium_clear_cards_btn)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        self.premium_progress = QProgressBar()
        self.premium_progress.setVisible(False)
        layout.addWidget(self.premium_progress)

        output_group = QGroupBox("📋 Output Log")
        output_group.setObjectName("outputGroup")
        out_layout = QVBoxLayout()
        self.premium_output = QTextEdit()
        self.premium_output.setReadOnly(True)
        self.premium_output.setObjectName("outputConsole")
        out_layout.addWidget(self.premium_output)
        output_group.setLayout(out_layout)
        layout.addWidget(output_group)

        return tab

    def show_login_dialog(self):
        dlg = LoginDialog(self)
        if dlg.exec_():
            data = dlg.user_data
            if data:
                self.session = dlg.session
                self.logged_in = True
                self.user_plan = data.get('plan', 'none')
                self.plan_active = data.get('plan_active', False)
                status_text = f"✅ Logged in: {self.user_plan.upper()}"
                if self.plan_active:
                    status_text += " (ACTIVE)"
                else:
                    status_text += " (EXPIRED / FREE)"
                self.premium_status_label.setText(status_text)
                self.premium_status_label.setStyleSheet("color: #73d216;")
                self.premium_login_btn.setText("🚪 Logout")
                self.premium_login_btn.clicked.disconnect()
                self.premium_login_btn.clicked.connect(self.do_logout)
                self.premium_start_btn.setEnabled(True)

    def do_logout(self):
        self.logged_in = False
        self.session = None
        self.user_plan = 'none'
        self.plan_active = False
        self.premium_status_label.setText("🔐 Not logged in")
        self.premium_status_label.setStyleSheet("color: #ff5555;")
        self.premium_login_btn.setText("🔑 Login")
        self.premium_login_btn.clicked.disconnect()
        self.premium_login_btn.clicked.connect(self.show_login_dialog)
        self.premium_start_btn.setEnabled(False)
        self.premium_output.append("✅ Logged out.")

    def start_premium_check(self):
        if not self.logged_in:
            self.premium_output.append("❌ Please login first.")
            return
        text = self.premium_input.toPlainText().strip()
        if not text:
            self.premium_output.append("❌ Enter card numbers.")
            return
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            self.premium_output.append("❌ No valid lines.")
            return

        self.premium_output.clear()
        self.premium_progress.setVisible(True)
        self.premium_progress.setMaximum(len(lines))
        self.premium_progress.setValue(0)
        self.premium_start_btn.setEnabled(False)
        self.premium_stop_btn.setEnabled(True)
        self.status_label.setText("🔄 Processing premium check...")

        self.worker = CheckerWorker(lines, premium=True, session=self.session)
        self.worker.progress.connect(self.premium_progress.setValue)
        self.worker.result.connect(self.premium_output.append)
        self.worker.finished.connect(self.premium_check_finished)
        self.worker.start()

    def premium_check_finished(self):
        self.premium_start_btn.setEnabled(True)
        self.premium_stop_btn.setEnabled(False)
        self.premium_progress.setVisible(False)
        self.status_label.setText("✅ Premium check finished.")

    # ---------- STOP CHECK (Common) ----------
    def stop_check(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.quit()
            self.worker.wait()
        self.free_check_finished()
        self.premium_check_finished()

    # ---------- BIN CHECKER TAB ----------
    def create_bin_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(QLabel("🔢 BIN (first 6 digits):"))
        self.bin_input = QLineEdit()
        self.bin_input.setPlaceholderText("453201")
        self.bin_input.setObjectName("binInput")
        top.addWidget(self.bin_input)
        self.bin_lookup_btn = QPushButton("🔍 Lookup")
        self.bin_lookup_btn.setObjectName("lookupBtn")
        self.bin_lookup_btn.clicked.connect(self.bin_lookup)
        top.addWidget(self.bin_lookup_btn)
        self.bin_clear_btn = QPushButton("🧹 Clear")
        self.bin_clear_btn.setObjectName("clearBtn")
        self.bin_clear_btn.clicked.connect(lambda: self.bin_output.clear())
        top.addWidget(self.bin_clear_btn)
        top.addStretch()
        layout.addLayout(top)

        self.bin_output = QTextEdit()
        self.bin_output.setReadOnly(True)
        self.bin_output.setObjectName("outputConsole")
        layout.addWidget(self.bin_output)

        return tab

    def bin_lookup(self):
        raw = self.bin_input.text().strip()
        if len(raw) < 6:
            self.bin_output.append("❌ Please enter at least 6 digits.")
            return
        bin_num = re.sub(r'\D', '', raw)[:6]
        brand = get_card_brand(bin_num)
        card_type = "CREDIT" if random.random() > 0.5 else "DEBIT"
        level = random.choice(["CLASSIC", "GOLD", "PLATINUM", "INFINITE"])
        self.bin_output.append("=" * 50)
        self.bin_output.append(f"📊 BIN: {bin_num}")
        self.bin_output.append(f"🏷️  Brand: {brand}")
        self.bin_output.append(f"💳 Type: {card_type}")
        self.bin_output.append(f"⭐ Level: {level}")
        self.bin_output.append("=" * 50)

    # ---------- BIN GENERATOR TAB ----------
    def create_gen_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(QLabel("🔢 BIN:"))
        self.gen_bin = QLineEdit()
        self.gen_bin.setPlaceholderText("453201")
        self.gen_bin.setObjectName("genInput")
        top.addWidget(self.gen_bin)
        top.addWidget(QLabel("Count:"))
        self.gen_count = QSpinBox()
        self.gen_count.setRange(1, 50)
        self.gen_count.setValue(10)
        self.gen_count.setObjectName("genSpin")
        top.addWidget(self.gen_count)
        self.gen_btn = QPushButton("⚡ Generate")
        self.gen_btn.setObjectName("startBtn")
        self.gen_btn.clicked.connect(self.generate_cards)
        top.addWidget(self.gen_btn)
        self.gen_clear_btn = QPushButton("🧹 Clear")
        self.gen_clear_btn.setObjectName("clearBtn")
        self.gen_clear_btn.clicked.connect(lambda: self.gen_output.clear())
        top.addWidget(self.gen_clear_btn)
        top.addStretch()
        layout.addLayout(top)

        self.gen_output = QTextEdit()
        self.gen_output.setReadOnly(True)
        self.gen_output.setObjectName("outputConsole")
        layout.addWidget(self.gen_output)

        return tab

    def generate_cards(self):
        raw = self.gen_bin.text().strip()
        if len(raw) < 6:
            self.gen_output.append("❌ Enter at least 6 digits.")
            return
        bin_num = re.sub(r'\D', '', raw)[:6]
        count = self.gen_count.value()
        self.gen_output.clear()
        self.gen_output.append("=" * 55)
        self.gen_output.append(f"📊 Generated {count} cards from BIN {bin_num}")
        self.gen_output.append("=" * 55)
        for i in range(count):
            card = generate_luhn_number(bin_num, 16)
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(2026, 2032))
            cvv = str(random.randint(100, 999))
            self.gen_output.append(f"{i+1:2d}. {card}|{month}|{year}|{cvv}")
        self.gen_output.append("=" * 55)
