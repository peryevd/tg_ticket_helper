from email_utils import check_mail
import time


def main():
    while True:
        check_mail()
        time.sleep(1)


if __name__ == "__main__":
    main()
