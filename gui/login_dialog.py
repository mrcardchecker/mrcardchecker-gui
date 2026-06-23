# gui/login_dialog.py
import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Premium Login")
        self.setFixedSize(320, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username / Email:"))
        self.username_edit = QLineEdit()
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.do_login)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)
        self.user_data = None
        self.session = requests.Session()

    def do_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields.")
            return
        try:
            resp = self.session.post('https://mrcardchecker.live/user/api_login.php',
                                     data={'username': username, 'password': password}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == 'success':
                    self.user_data = data
                    self.accept()
                else:
                    QMessageBox.critical(self, "Login Failed", data.get('msg', 'Unknown error'))
            else:
                QMessageBox.critical(self, "Error", f"Server error: {resp.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
