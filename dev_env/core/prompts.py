import sys
import os
if os.name == 'nt':
    os.system("color")


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    MAGENTA = '\033[35m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Prompt:

    @staticmethod
    def error(message, close=False):
        print(f"{Colors.FAIL}[x]{message}{Colors.ENDC}")
        if close:
            sys.exit(1)

    @staticmethod
    def banner(items, prevent_all_option=False):
        for i, item in enumerate(items):
            print(f"{Colors.WARNING}{i+1}. {Colors.CYAN}{item}{Colors.ENDC}")
        if not prevent_all_option and len(items) > 1:
            print(f"{Colors.WARNING}{len(items) + 1}. All{Colors.ENDC}")
        return items

    @staticmethod
    def get_response(prompt, items, prevent_all_option=False):
        print()
        value = input(prompt)
        if value not in [str(x + 1) for x in range(len(items) + 1 if (not prevent_all_option and len(items) > 1)
                                                   else len(items))] or int(value) == len(items) + 1:
            Prompt.error(f"{value} is not a valid choice.")
            return Prompt.get_response(prompt, items)
        return int(value)

    @staticmethod
    def title_banner(title, first=False):
        if not first:
            print()
        print(f"{Colors.HEADER}[-]{title}{Colors.ENDC}")
        print("="*70)

    @staticmethod
    def warning(message):
        print(f"{Colors.WARNING}[-]{message}{Colors.ENDC}")

    @staticmethod
    def notice(message):
        print(f"{Colors.YELLOW}[*]{message}{Colors.ENDC}")

    @staticmethod
    def success(message):
        print(f"{Colors.GREEN}[+]{message}{Colors.ENDC}")
