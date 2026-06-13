import random
import time
import sys

# Reconfigure stdout to use UTF-8 to support emojis on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older Python versions
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

# Emojis and ASCII representations
CHOICES = {
    'r': {'name': 'Rock', 'emoji': '🪨', 'beats': 's'},
    'p': {'name': 'Paper', 'emoji': '📄', 'beats': 'r'},
    's': {'name': 'Scissors', 'emoji': '✂️', 'beats': 'p'}
}

def clear_screen():
    # Clears the terminal screen for a cleaner UI
    print("\033[H\033[J", end="")

def print_banner():
    clear_screen()
    print(f"{CYAN}{BOLD}============================================")
    print("      🪨  ROCK, 📄 PAPER, ✂️  SCISSORS")
    print(f"============================================{RESET}\n")

def print_help():
    print(f"{YELLOW}How to Play:{RESET}")
    print("  - Choose (R)ock, (P)aper, or (S)cissors.")
    print("  - Rock beats Scissors.")
    print("  - Paper beats Rock.")
    print("  - Scissors beat Paper.\n")

def get_player_choice():
    while True:
        choice = input(f"{BOLD}Enter your choice [R, P, S] or (Q)uit: {RESET}").strip().lower()
        if choice == 'q':
            return 'q'
        if choice in CHOICES:
            return choice
        print(f"{RED}Invalid choice! Please choose R, P, S, or Q.{RESET}\n")

def display_countdown():
    print(f"\n{BOLD}Rock...{RESET}", end="", flush=True)
    time.sleep(0.4)
    print(f" {BOLD}Paper...{RESET}", end="", flush=True)
    time.sleep(0.4)
    print(f" {BOLD}Scissors...{RESET}", end="", flush=True)
    time.sleep(0.4)
    print(f" {BOLD}Shoot!{RESET}\n")
    time.sleep(0.2)

def main():
    player_score = 0
    computer_score = 0
    draws = 0
    round_num = 1

    print_banner()
    print_help()
    
    input(f"{GREEN}Press Enter to start the game...{RESET}")

    while True:
        print_banner()
        print(f"{MAGENTA}{BOLD}--- ROUND {round_num} ---{RESET}")
        print(f"{BLUE}Scores -> Player: {player_score} | Computer: {computer_score} | Draws: {draws}{RESET}\n")
        
        player_key = get_player_choice()
        if player_key == 'q':
            break

        computer_key = random.choice(list(CHOICES.keys()))

        display_countdown()

        player_choice = CHOICES[player_key]
        computer_choice = CHOICES[computer_key]

        print(f"{BOLD}You chose:{RESET} {player_choice['name']} {player_choice['emoji']}")
        print(f"{BOLD}Computer chose:{RESET} {computer_choice['name']} {computer_choice['emoji']}\n")

        if player_key == computer_key:
            print(f"{YELLOW}{BOLD}It's a tie! {player_choice['emoji']}  🤝  {computer_choice['emoji']}{RESET}\n")
            draws += 1
        elif player_choice['beats'] == computer_key:
            print(f"{GREEN}{BOLD}You win this round! 🎉{RESET}")
            print(f"{GREEN}{player_choice['name']} beats {computer_choice['name']}.{RESET}\n")
            player_score += 1
        else:
            print(f"{RED}{BOLD}Computer wins this round! 🤖{RESET}")
            print(f"{RED}{computer_choice['name']} beats {player_choice['name']}.{RESET}\n")
            computer_score += 1

        round_num += 1
        
        # Pause before continuing
        input(f"{CYAN}Press Enter to continue...{RESET}")

    # Final Scoreboard
    print_banner()
    print(f"{BOLD}Thank you for playing!{RESET}\n")
    print(f"{MAGENTA}{BOLD}==== FINAL SCOREBOARD ===={RESET}")
    print(f"  Total Rounds Played: {round_num - 1}")
    print(f"  {GREEN}Player Score: {player_score}{RESET}")
    print(f"  {RED}Computer Score: {computer_score}{RESET}")
    print(f"  {YELLOW}Draws: {draws}{RESET}")
    print(f"{MAGENTA}{BOLD}=========================={RESET}\n")
    
    if player_score > computer_score:
        print(f"{GREEN}{BOLD}Congratulations! You defeated the Computer! 🏆🎉{RESET}\n")
    elif computer_score > player_score:
        print(f"{RED}{BOLD}Game Over! The Computer wins this time. Better luck next time! 🤖💀{RESET}\n")
    else:
        print(f"{YELLOW}{BOLD}It's a draw game overall! Balanced forces! 🤝{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Game interrupted. Goodbye!{RESET}")
        sys.exit(0)
