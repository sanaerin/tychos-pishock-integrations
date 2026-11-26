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
from pishock_api import get_account, get_shockers, operate

EVENT_FILE = Path("pishock_events.txt")
PISHOCK_ENABLED = True

shocker_id = None
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


def resource_path(relative_path):  # pyinstaller resource helper
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    return base_path / relative_path


def connect_pishock():
    global shocker_id

    shocker_id = None

    if not PISHOCK_ENABLED:
        log("PiShock is disabled")
        return

    try:
        log("Connecting to PiShock API...")

        account = get_account()  # loads api key from config and sends request

        log(f"Logged in as {account['Username']}")

        shockers = get_shockers(account["UserId"])

        if not shockers:
            log("No active V3 compatible shockers found")
            readyLbl.setText("No devices")
            readyLbl.setStyleSheet("color: orange;")
            return

        selected = shockers[0]  # use first device found, TODO: make a selector
        shocker_id = selected["Id"]

        log("PiShock connection successful!")
        log(f"Device: {selected['Name']}")
        log(f"Available devices: {len(shockers)}")

        readyLbl.setText("Ready")
        readyLbl.setStyleSheet("color: green;")

    except Exception as e:
        log(f"PiShock connection failed: {e}")

        readyLbl.setText("Not ready")
        readyLbl.setStyleSheet("color: red;")

        shocker_id = None


def handle_pishock(event):
    if not PISHOCK_ENABLED or shocker_id is None:
        log("PiShock is not connected")
        return

    # test button: vibration
    if event == "TEST":
        try:
            log("Sending PiShock test...")
            operate(
                shocker_id,
                operation=1,  # 1 = vibrate
                duration=1,
                intensity=25,
            )
            log("PiShock test successful")

        except Exception as e:
            log(f"PiShock test failed: {e}")

        return

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

        operate(
            shocker_id,
            operation=0,
            duration=duration,
            intensity=intensity,
        )

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

    if (
        event == "EVENT_HOOKS_INSTALLED"
    ):  # could add a beep here or something to detect new game?
        return

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
root.setWindowIcon(QIcon(resource_path("images/tycho-icon.ico").as_posix()))

tycho_background = QWidget()
tycho_image = resource_path("images/tycho-bg.png").as_posix()
tycho_background.setObjectName("background_widget")
tycho_background.setStyleSheet(
    "QWidget#background_widget {"
    f'background-image: url("{tycho_image}");'
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

connect_pishock_btn = QPushButton("Connect")
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
