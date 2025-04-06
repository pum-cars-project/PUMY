SUCCESS_COLOR_CODE = "\033[92m"
WARN_COLOR_CODE = "\033[93m"
ERROR_COLOR_CODE = "\033[91m"
END_COLOR_CODE = "\033[0m"


def log_info(message):
    print(f'[INFO]\t: {message}')


def log_warn(message):
    print(f'{WARN_COLOR_CODE}[WARN]{END_COLOR_CODE}\t: {message}')


def log_error(message):
    print(f'{ERROR_COLOR_CODE}[ERROR]{END_COLOR_CODE}\t: {message}')


def log_success(message):
    print(f'{SUCCESS_COLOR_CODE}[SUCCESS]{END_COLOR_CODE}\t: {message}')
