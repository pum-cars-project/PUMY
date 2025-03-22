from datetime import datetime

SUCCESS_COLOR_CODE = "\033[92m"
WARN_COLOR_CODE = "\033[93m"
ERROR_COLOR_CODE = "\033[91m"
END_COLOR_CODE = "\033[0m"


def log_info(message):
    print(f'[{get_time()}][INFO]\t: {message}')


def log_warn(message):
    print(f'[{get_time()}]{WARN_COLOR_CODE}[WARN]{END_COLOR_CODE}\t: {message}')


def log_error(message):
    print(f'[{get_time()}]{ERROR_COLOR_CODE}[ERROR]{END_COLOR_CODE}\t: {message}')


def log_success(message):
    print(f'[{get_time()}]{SUCCESS_COLOR_CODE}[SUCCESS]{END_COLOR_CODE}\t: {message}')


def log_debug(message):
    print(f'[{get_time()}][DEBUG]\t: {message}')

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
