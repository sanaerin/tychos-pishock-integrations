import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFontDatabase, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import get_config, open_config, set_event_enabled

EVENT_FILE = Path("pishock_events.txt")
PISHOCK_ENABLED = True

shocker = None
api = None
event_file = None
event_timer = None
event_log = None
readyLbl = None
ingameLbl = None


def close_event_file():
    global event_file

    if event_file:
        event_file.close()
        event_file = None


def log(message):
    event_log.appendPlainText(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    cursor = event_log.textCursor()
    cursor.movePosition(cursor.MoveOperation.End)
    event_log.setTextCursor(cursor)
    event_log.ensureCursorVisible()


def connect_pishock():
    global api, shocker

    config = get_config()

    username = config["username"]
    api_key = config["api_key"]
    sharecode = config["sharecode"]

    if not PISHOCK_ENABLED:
        log("PiShock is disabled")
        return

    try:
        from pishock import PiShockAPI

        if not any([api_key, sharecode, username]):
            log("PiShock: Configuration empty, please configure!")
            return

        log("Connecting to PiShock API...")

        api = PiShockAPI(username, api_key)
        shocker = api.shocker(sharecode)

        info = shocker.info()

        log("PiShock: Credentials and share code accepted")
        log(f"Device: {info.name}")
        log(f"Paused: {info.is_paused}")

        if info.is_paused:
            log("PiShock is paused")
            readyLbl.setText("Paused")
            readyLbl.setStyleSheet("color: yellow;")
        else:
            log("PiShock is ready")
            readyLbl.setText("Ready")
            readyLbl.setStyleSheet("color: green;")

    except Exception as e:
        log(f"PiShock connection failed: {e}")
        readyLbl.setText("Not ready")
        readyLbl.setStyleSheet("color: red;")
        shocker = None


def handle_pishock(event):
    if not PISHOCK_ENABLED or shocker is None:
        log("PiShock is not connected")
        return

    if event == "TEST":
        shocker.vibrate(1, 25)

    config = get_config()

    event_config = config["events"].get(event)

    if event_config is None:
        return

    if not event_config["enabled"]:
        log(f"{event} is disabled")
        return

    intensity = event_config["intensity"]
    duration = event_config["duration"]

    try:
        log(f"Sending PiShock command for {event}...")
        shocker.shock(intensity, duration)
        log("PiShock command submitted")

    except Exception as e:
        log(f"PiShock action failed: {e}")


def handle_event(event):
    messages = {
        "PLAYER_BUSTED": "Player busted",
        "PLAYER_LOST_ALL_IN": "Player lost all-in",
        "PLAYER_LOST": "Player lost the hand",
        "EVENT_HOOKS_INSTALLED": "New table detected",
    }

    message = messages.get(event, f"{event}")
    log(f"Event: {message}")

    if messages.get(event):
        ingameLbl.setText("In-game")
        ingameLbl.setStyleSheet(
            "color: green;"
        )  # detects game activity from pishock_events.txt file

    handle_pishock(event)


def update_event_setting(event, variable):
    set_event_enabled(event, variable.isChecked())


def check_events():
    if event_file is None:
        return

    line = event_file.readline()

    while line:
        event = line.strip()

        if event:
            handle_event(event)

        line = event_file.readline()


def listen():
    EVENT_FILE.touch(exist_ok=True)

    global event_file
    event_file = EVENT_FILE.open("r", encoding="utf-8")
    event_file.seek(0, 2)  # check end of file

    log("Listening for events...")

    check_events()
    event_timer.start(100)  # 100ms refresh for new events


app = QApplication(sys.argv)

root = QMainWindow()
root.setWindowTitle("Tycho's PiShock Integrations")
root.setMinimumSize(600, 400)
root.setWindowIcon(QIcon("images/tycho-icon.ico"))

tycho_background = QWidget()
tycho_background.setObjectName("background_widget")
tycho_background.setStyleSheet(
    "QWidget#background_widget {"
    'background-image: url("images/tycho-bg.png");'
    "background-position: bottom right;"
    "background-repeat: no-repeat;"
    "}"
)
root.setCentralWidget(tycho_background)

main_layout = QHBoxLayout(tycho_background)
main_layout.setContentsMargins(10, 10, 10, 10)
main_layout.setSpacing(10)

left_frame = QWidget()
left_frame.setFixedWidth(150)
main_layout.addWidget(left_frame, 0)

left_layout = QVBoxLayout(left_frame)
left_layout.setContentsMargins(0, 0, 0, 0)
left_layout.setSpacing(0)

status_frame = QFrame()
left_layout.addWidget(status_frame, 0, Qt.AlignmentFlag.AlignTop)

status_layout = QVBoxLayout(status_frame)
status_layout.setContentsMargins(10, 10, 10, 10)
status_layout.setSpacing(3)

# status panel
titleLbl = QLabel("PiShock status")
titleLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
status_layout.addWidget(titleLbl)

readyLbl = QLabel("Not ready")
readyLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
readyLbl.setStyleSheet("color: red;")
status_layout.addWidget(readyLbl)

connect_pishock_btn = QPushButton("Check connection")
connect_pishock_btn.clicked.connect(connect_pishock)
status_layout.addWidget(connect_pishock_btn)

configtest_frame = QWidget()
status_layout.addWidget(configtest_frame)

configtest_layout = QHBoxLayout(configtest_frame)
configtest_layout.setContentsMargins(0, 3, 0, 3)
configtest_layout.setSpacing(4)

configure_pishock_btn = QPushButton("Configure")
configure_pishock_btn.clicked.connect(lambda: open_config())
configtest_layout.addWidget(configure_pishock_btn, 12)

test_pishock_btn = QPushButton("Test")
test_pishock_btn.clicked.connect(lambda: handle_event("TEST"))
configtest_layout.addWidget(test_pishock_btn, 5)

status_layout.addSpacing(5)
game_status_title = QLabel("Game status")
game_status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
status_layout.addWidget(game_status_title)

ingameLbl = QLabel("Waiting for change")
ingameLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
ingameLbl.setStyleSheet("color: grey;")
status_layout.addWidget(ingameLbl)


# shock conditions panel
config = get_config()

buttons_frame = QFrame()
left_layout.addWidget(buttons_frame, 0, Qt.AlignmentFlag.AlignTop)

buttons_layout = QVBoxLayout(buttons_frame)
buttons_layout.setContentsMargins(10, 10, 10, 10)
buttons_layout.setSpacing(5)

shock_conditions_title = QLabel("Shock conditions")
shock_conditions_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
buttons_layout.addWidget(shock_conditions_title)

hand_loss_enabled = QCheckBox("Lose hand")
hand_loss_enabled.setChecked(config["events"]["PLAYER_LOST"]["enabled"])
hand_loss_enabled.clicked.connect(
    lambda: update_event_setting("player_lost", hand_loss_enabled)
)
buttons_layout.addWidget(hand_loss_enabled, 0, Qt.AlignmentFlag.AlignLeft)

all_in_loss_enabled = QCheckBox("Lose all-in")
all_in_loss_enabled.setChecked(config["events"]["PLAYER_LOST_ALL_IN"]["enabled"])
all_in_loss_enabled.clicked.connect(
    lambda: update_event_setting("player_lost_all_in", all_in_loss_enabled)
)
buttons_layout.addWidget(all_in_loss_enabled, 0, Qt.AlignmentFlag.AlignLeft)

busted_loss_enabled = QCheckBox("Busted")
busted_loss_enabled.setChecked(config["events"]["PLAYER_BUSTED"]["enabled"])
busted_loss_enabled.clicked.connect(
    lambda: update_event_setting("player_busted", busted_loss_enabled)
)
buttons_layout.addWidget(busted_loss_enabled, 0, Qt.AlignmentFlag.AlignLeft)

right_frame = QWidget()
right_frame.setAutoFillBackground(True)
right_palette = right_frame.palette()
right_palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255, 128))
right_frame.setPalette(right_palette)
main_layout.addWidget(right_frame, 1)

# event logs
events_layout = QVBoxLayout(right_frame)
events_layout.setContentsMargins(0, 10, 0, 10)
events_layout.setSpacing(0)

event_log = QPlainTextEdit()
event_log.setReadOnly(True)
event_log.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
event_log.setFrameShape(QFrame.Shape.NoFrame)
event_log.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
event_log.setCursorWidth(1)
event_log.setBackgroundVisible(False)
event_log.setAutoFillBackground(False)
event_log.viewport().setAutoFillBackground(False)

events_layout.addWidget(event_log, 1)


event_timer = QTimer(root)
event_timer.timeout.connect(check_events)

app.aboutToQuit.connect(close_event_file)

root.show()
listen()
app.exec()
