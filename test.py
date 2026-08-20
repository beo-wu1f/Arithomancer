from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
import random
import time
import threading

console = Console()


def banner():
    console.clear()

    title = r"""
     █████╗ ██████╗ ██╗████████╗██╗  ██╗ ██████╗ ███╗   ███╗ █████╗ ███╗   ██╗ ██████╗███████╗██████╗
    ██╔══██╗██╔══██╗██║╚══██╔══╝██║  ██║██╔═══██╗████╗ ████║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗
    ███████║██████╔╝██║   ██║   ███████║██║   ██║██╔████╔██║███████║██╔██╗ ██║██║     █████╗  ██████╔╝
    ██╔══██║██╔══██╗██║   ██║   ██╔══██║██║   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗
    ██║  ██║██║  ██║██║   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝
    """

    console.print(
        Panel(
            Align.center(
                f"[bold cyan]{title}[/bold cyan]\n"
                "[bold yellow]THE ROGUE-LIKE MULTIPLICATION GAME[/bold yellow]"
            ),
            border_style="bright_blue",
            padding=(1, 2),
            expand=False
        )
    )

def main_menu():
    while True:
        banner()

        menu = Table(
            box=None,
            show_header=False,
            padding=(0, 2)
        )

        menu.add_column("Key", style="bold yellow", justify="center")
        menu.add_column("Action", style="bold white")

        menu.add_row("[1]", "⚔  PLAY")
        menu.add_row("[2]", "🏆 HIGH SCORES")
        menu.add_row("[3]", "⚙  SETTINGS")
        menu.add_row("[4]", "🚪 EXIT")

        console.print(
            Panel(
                Align.center(menu),
                title="[bold cyan]MAIN MENU[/bold cyan]",
                border_style="cyan",
                expand=False,
                padding=(1, 4)
            )
        )

        choice = console.input(
            "\n[bold yellow]Choose your path › [/bold yellow]"
        )

        if choice == "1":
            play()
        elif choice == "2":
            high_scores()
        elif choice == "3":
            settings()
        elif choice == "4":
            console.clear()
            console.print(
                Panel(
                    "[bold cyan]Thanks for playing MULTIPLICATIVE.[/bold cyan]",
                    border_style="cyan",
                    expand=False
                )
            )
            break
        else:
            console.print(
                "\n[bold red]✗ Invalid choice.[/bold red] "
                "Choose 1, 2, 3, or 4."
            )
            console.input("\nPress ENTER to continue...")


def get_difficulty(question_number):

    if question_number <= 10:
        difficulty_name = "Novice"
        max_number = 5

    elif question_number <= 20:
        difficulty_name = "Acolyte"
        max_number = 7

    elif question_number <= 30:
        difficulty_name = "Apprentice"
        max_number = 9

    elif question_number <= 40:
        difficulty_name = "Adept"
        max_number = 11

    else:
        difficulty_name = "Mage"
        max_number = 13

    return difficulty_name, max_number


def generate_question(max_number, used_questions):

    while True:

        factor = random.randint(1, max_number)
        multiplier = random.randint(1, max_number)

        question_key = tuple(sorted((factor, multiplier)))

        if question_key not in used_questions:

            used_questions.add(question_key)

            break

    answer = factor * multiplier

    return factor, multiplier, answer

def play():

    console.clear()

    question_number = 1
    used_questions = set()

    time_remaining = 5.0
    running = True

    while True:

        difficulty_name, max_number = get_difficulty(question_number)

        factor, multiplier, correct_answer = generate_question(
            max_number,
            used_questions
        )

        # --------------------------------------------------
        # TIMER
        # --------------------------------------------------

        question_start = time.time()
        starting_time = time_remaining

        answer_received = False
        player_answer = None

        def timer():

            nonlocal time_remaining, running

            while running and not answer_received:

                elapsed_time = time.time() - question_start

                time_remaining = starting_time - elapsed_time

                if time_remaining <= 0:

                    time_remaining = 0
                    break

                time.sleep(0.05)

        timer_thread = threading.Thread(target=timer)

        timer_thread.start()

        # --------------------------------------------------
        # LIVE DISPLAY
        # --------------------------------------------------

        with Live(refresh_per_second=10) as live:

            while not answer_received and time_remaining > 0:

                bar_length = 25

                filled_length = int(
                    bar_length * time_remaining / 5
                )

                bar = (
                    "█" * filled_length
                    + "░" * (bar_length - filled_length)
                )

                screen = Panel(
                    Align.center(
                        f"[bold yellow]QUESTION {question_number}[/bold yellow]\n"
                        f"[bold cyan]{difficulty_name}[/bold cyan]\n\n"
                        f"[bold white]{factor} × {multiplier}[/bold white]\n\n"
                        "[bold yellow]TIME REMAINING[/bold yellow]\n"
                        f"[bold cyan]{bar}[/bold cyan]\n"
                        f"[bold white]{time_remaining:.1f}s[/bold white]"
                    ),
                    border_style="bright_blue",
                    expand=False,
                    padding=(2, 8)
                )

                live.update(screen)

                time.sleep(0.05)

                # Check whether time expired
                if time_remaining <= 0:
                    break

            # --------------------------------------------------
            # PLAYER INPUT
            # --------------------------------------------------

            if time_remaining > 0:

                player_answer = console.input(
                    "\n[bold cyan]Your answer › [/bold cyan]"
                )

                answer_received = True

        timer_thread.join()

        # --------------------------------------------------
        # TIME EXPIRED
        # --------------------------------------------------

        if time_remaining <= 0:

            console.print(
                Panel(
                    Align.center(
                        "[bold red]☠ TIME'S UP ☠[/bold red]\n\n"
                        f"{factor} × {multiplier} = {correct_answer}"
                    ),
                    border_style="red",
                    expand=False,
                    padding=(2, 6)
                )
            )

            console.input(
                "\n[dim]Press ENTER to return to the menu...[/dim]"
            )

            break

        # --------------------------------------------------
        # CHECK ANSWER
        # --------------------------------------------------

        try:
            player_answer = int(player_answer)

        except ValueError:
            player_answer = None

        if player_answer == correct_answer:

            time_remaining += 2

            console.print(
                Panel(
                    Align.center(
                        "[bold green]✓ CORRECT![/bold green]\n\n"
                        f"{factor} × {multiplier} = {correct_answer}\n\n"
                        "[yellow]+2 seconds[/yellow]\n"
                        f"[bold cyan]Time: {time_remaining:.1f}s[/bold cyan]"
                    ),
                    border_style="green",
                    expand=False
                )
            )

            question_number += 1

            console.input(
                "\n[dim]Press ENTER for the next question...[/dim]"
            )

        else:

            console.print(
                Panel(
                    Align.center(
                        "[bold red]☠ GAME OVER ☠[/bold red]\n\n"
                        f"{factor} × {multiplier} = {correct_answer}\n"
                        f"You answered: {player_answer}\n\n"
                        f"[yellow]Questions survived: "
                        f"{question_number - 1}[/yellow]"
                    ),
                    border_style="red",
                    expand=False,
                    padding=(2, 6)
                )
            )

            console.input(
                "\n[dim]Press ENTER to return to the menu...[/dim]"
            )

            break

def high_scores():
    console.clear()
    console.print(
        Panel(
            Align.center(
                "[bold yellow]🏆 HIGH SCORES[/bold yellow]\n\n"
                "[dim]No scores recorded yet.[/dim]"
            ),
            border_style="yellow",
            expand=False,
            padding=(2, 6)
        )
    )

    console.input("\nPress ENTER to return to the menu...")


def settings():
    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold cyan]⚙  SETTINGS[/bold cyan]\n\n"
                "[dim]Nothing to configure yet.[/dim]\n"
                "[dim]The run determines its own difficulty.[/dim]"
            ),
            border_style="cyan",
            expand=False,
            padding=(2, 6)
        )
    )

    console.input("\nPress ENTER to return to the menu...")

main_menu()

