import sys
import secrets
import string
import subprocess

# Reconfigure stdout to use UTF-8 to support emojis/colors cleanly on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ANSI escape codes for coloring terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

def clear_screen():
    print("\033[H\033[J", end="")

def print_banner():
    clear_screen()
    print(f"{CYAN}{BOLD}============================================")
    print("        🔐 SECURE PASSWORD GENERATOR")
    print(f"============================================{RESET}\n")

def get_yes_no(prompt, default=True):
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        val = input(f"{BOLD}{prompt}{suffix}:{RESET} ").strip().lower()
        if not val:
            return default
        if val in ('y', 'yes'):
            return True
        if val in ('n', 'no'):
            return False
        print(f"{RED}Invalid input. Please enter 'y' or 'n'.{RESET}")

def get_password_length():
    while True:
        val = input(f"{BOLD}Enter password length (default: 16, min: 4, max: 128):{RESET} ").strip()
        if not val:
            return 16
        try:
            length = int(val)
            if 4 <= length <= 128:
                return length
            print(f"{RED}Length must be between 4 and 128.{RESET}")
        except ValueError:
            print(f"{RED}Please enter a valid number.{RESET}")

def copy_to_clipboard(text):
    try:
        # Use Windows native clip command
        process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('utf-8'))
        return True
    except Exception:
        return False

def generate_password(length, use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous):
    # Base character pools
    lower_chars = string.ascii_lowercase
    upper_chars = string.ascii_uppercase
    digits_chars = string.digits
    symbols_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Exclude ambiguous characters if requested
    # Ambiguous: l, 1, I, o, 0, O, |, I, etc.
    if exclude_ambiguous:
        ambiguous = "l1Io0O|"
        lower_chars = "".join([c for c in lower_chars if c not in ambiguous])
        upper_chars = "".join([c for c in upper_chars if c not in ambiguous])
        digits_chars = "".join([c for c in digits_chars if c not in ambiguous])
        symbols_chars = "".join([c for c in symbols_chars if c not in ambiguous])

    # Build character set and ensure we have at least one character from each selected pool
    pool = ""
    mandatory_chars = []

    if use_lower:
        if not lower_chars:
            print(f"{RED}Error: Lowercase character pool is empty after exclusion!{RESET}")
            sys.exit(1)
        pool += lower_chars
        mandatory_chars.append(secrets.choice(lower_chars))
    if use_upper:
        if not upper_chars:
            print(f"{RED}Error: Uppercase character pool is empty after exclusion!{RESET}")
            sys.exit(1)
        pool += upper_chars
        mandatory_chars.append(secrets.choice(upper_chars))
    if use_digits:
        if not digits_chars:
            print(f"{RED}Error: Digits character pool is empty after exclusion!{RESET}")
            sys.exit(1)
        pool += digits_chars
        mandatory_chars.append(secrets.choice(digits_chars))
    if use_symbols:
        if not symbols_chars:
            print(f"{RED}Error: Symbols character pool is empty after exclusion!{RESET}")
            sys.exit(1)
        pool += symbols_chars
        mandatory_chars.append(secrets.choice(symbols_chars))

    if not pool:
        print(f"{RED}Error: You must select at least one character set!{RESET}")
        return None

    # Fill the remaining length with random choices from the entire selected pool
    remaining_length = length - len(mandatory_chars)
    if remaining_length < 0:
        # If password length requested is smaller than the number of active character sets,
        # we adjust mandatory_chars to fit the requested length
        mandatory_chars = mandatory_chars[:length]
        remaining_length = 0

    password_list = mandatory_chars + [secrets.choice(pool) for _ in range(remaining_length)]
    
    # Shuffle the characters cryptographically safely to make placement unpredictable
    secrets.SystemRandom().shuffle(password_list)
    
    return "".join(password_list)

def main():
    print_banner()

    # Get user configurations
    length = get_password_length()
    use_lower = get_yes_no("Include Lowercase letters (a-z)", default=True)
    use_upper = get_yes_no("Include Uppercase letters (A-Z)", default=True)
    use_digits = get_yes_no("Include Digits (0-9)", default=True)
    use_symbols = get_yes_no("Include Symbols (!@#$...)", default=True)
    exclude_ambiguous = get_yes_no("Exclude ambiguous characters (e.g., l, 1, I, o, 0, O)", default=True)

    password = generate_password(length, use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous)
    
    if password:
        print(f"\n{GREEN}{BOLD}Password successfully generated!{RESET}\n")
        print(f"{YELLOW}----------------------------------------")
        print(f" {BOLD}{password}{RESET}")
        print(f"{YELLOW}----------------------------------------{RESET}\n")
        
        # Try copying to clipboard automatically
        copied = copy_to_clipboard(password)
        if copied:
            print(f"{GREEN}📋 Password copied to your clipboard automatically!{RESET}")
        else:
            print(f"{YELLOW}⚠️  Could not copy to clipboard automatically. Please copy it manually.{RESET}")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Program interrupted. Goodbye!{RESET}")
        sys.exit(0)
