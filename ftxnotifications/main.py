import collections
import logging
from time import sleep

from ftxnotifications import ftx_utils
from ftxnotifications.telegram_utils import send_telegram
from ftxnotifications.markdown_utils import escape_markdown

# Some lines are static and not relevant for including in the notifications
LINES_TO_IGNORE = [
    "To view the rest of your fills, please visit ftx.com/wallet.",
    "Withdrawals are processed within a few hours. You can find more information at "
    "https://help.ftx.com/hc/en-us/articles/360034865571-Deposits-and-Withdrawals.",
    "If you did not make this request, please change your password and contact customer support immediately.",
    "FTX"
]

log = logging.getLogger("")

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")


def get_lines(notification):
    """
    Get lines within a notification
    """
    lines = []
    for line in notification.splitlines():
        line = line.strip()
        line = line.replace("  ", " ")
        if line:
            lines.append(line)
    return lines


def get_lines_to_print(new_notification, old_notification):
    """
    Gets new lines that appeared in the new notification and not in the old copy of it
    """
    lines_to_print = []
    new_lines = get_lines(new_notification)
    old_lines = get_lines(old_notification)
    # Oldest notifications first, reverse
    for new_line in new_lines[::-1]:
        if new_line in old_lines:
            continue
        if new_line in LINES_TO_IGNORE:
            continue
        lines_to_print.append(new_line)
    return lines_to_print


def run():
    # Get current state of notifications
    notification_state = collections.defaultdict(str)
    notifications = ftx_utils.get_notifications()
    for notification in notifications:
        new_notification = notification["body"]
        notification_id = notification["id"]
        notification_state[notification_id] = new_notification
    # Poll for notifications in loop
    while True:
        try:
            sleep(0.1)
            notifications = ftx_utils.get_notifications()
            notifications.sort(key=lambda n: n["created_at"])
            for notification in notifications:
                # Only send notification for unread notifications
                if notification["unread"]:
                    new_notification = notification["body"]
                    notification_id = notification["id"]
                    # Get old copy of notification
                    old_notification = notification_state[notification_id]
                    lines_to_print = get_lines_to_print(new_notification, old_notification)
                    subaccount = notification["subaccount"]
                    # Send notification for new line within the notification
                    for line in lines_to_print:
                        notification = f"Subaccount: *{subaccount}*\n{escape_markdown(line)}"
                        logging.info(notification)
                        send_telegram(notification)
                    notification_state[notification_id] = new_notification
        except KeyboardInterrupt:
            exit()
        except:
            log.exception("Could not process notification poll")


if __name__ == "__main__":
    run()
