from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live

import random
import time
import threading


console = Console()


# ============================================================
# BANNER
# ============================================================

def banner():

    console.clear()

    title = r"""
     █████╗ ██████╗ ██╗████████╗██╗  ██╗ ██████╗ ███╗   ███╗ █████╗ ███╗   ██╗ ██████╗███████╗╚██████╗
    ██╔══██╗██╔══██╗██║╚══██╔══╝██║  ██║██╔═══██╗████╗ ████║██╔══██╗████╗  ██║██╔════╝██╔════╝  ██╔══╝
    ███████║██████╔╝██║   ██║   ███████║██║   ██║██╔████╔██║███████║██╔██╗ ██║██║     █████╗    ██║
    ██╔══██║██╔══██╗██║   ██║   ██╔══██║██║   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║██║     ██╔══╝    ██║
    ██║  ██║██║  ██║██║   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║╚██████╗███████╗   ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝   ╚═╝
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


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():

    while True:

        banner()

        menu = Table(
            box=None,
            show_header=False,
            padding=(0, 2)
        )

        menu.add_column(
            "Key",
            style="bold yellow",
            justify="center"
        )

        menu.add_column(
            "Action",
            style="bold white"
        )

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
                    "[bold cyan]Thanks for playing ARITHOMANCER.[/bold cyan]",
                    border_style="cyan",
                    expand=False
                )
            )

            break

        else:

            console.print(
                "\n[bold red]✗ Invalid choice.[/bold red]"
            )

            console.input(
                "\nPress ENTER to continue..."
            )


# ============================================================
# QUESTION GENERATOR
# ============================================================

def generate_question(question_number):

    min_number = round(1 + question_number * 0.20)
    max_number = round(5 + question_number * 0.30)

    factor = random.randint(
        min_number,
        max_number
    )

    multiplier = random.randint(
        min_number,
        max_number
    )

    answer = factor * multiplier

    return factor, multiplier, answer


# ============================================================
# TIMER PANEL
# ============================================================

def make_panel(
    question_number,
    factor,
    multiplier,
    time_remaining
):

    bar_length = 20

    filled = int(
        bar_length * time_remaining / 5
    )

    bar = (
        "█" * filled
        +
        "░" * (bar_length - filled)
    )

    return Panel(
        Align.center(
            f"[bold yellow]QUESTION {question_number}[/bold yellow]\n\n"
            f"[bold white]{factor} × {multiplier}[/bold white]\n\n"
            "[bold yellow]TIME REMAINING[/bold yellow]\n\n"
            f"[bold cyan]{bar}[/bold cyan]\n"
            f"{time_remaining:.1f}s"
        ),
        border_style="bright_blue",
        expand=False,
        padding=(2, 8)
    )


# ============================================================
# PLAY
# ============================================================

def play():

    question_number = 1

    while True:

        # ----------------------------------------------------
        # Generate question
        # ----------------------------------------------------

        factor, multiplier, correct_answer = generate_question(
            question_number
        )


        # ----------------------------------------------------
        # State for this question
        # ----------------------------------------------------

        time_up = threading.Event()

        answer_received = threading.Event()

        player_answer = None


        # ----------------------------------------------------
        # INPUT THREAD
        # ----------------------------------------------------

        def get_input():

            nonlocal player_answer

            player_answer = console.input(
                "\n[bold cyan]Your answer › [/bold cyan]"
            )

            answer_received.set()


        # ----------------------------------------------------
        # TIMER THREAD
        # ----------------------------------------------------

        def timer(live):

            start_time = time.monotonic()

            while True:

                elapsed = (
                    time.monotonic()
                    -
                    start_time
                )

                time_remaining = 5.0 - elapsed


                # Time expired
                if time_remaining <= 0:

                    live.update(
                        make_panel(
                            question_number,
                            factor,
                            multiplier,
                            0
                        ),
                        refresh=True
                    )

                    time_up.set()

                    break


                # Update timer display
                live.update(
                    make_panel(
                        question_number,
                        factor,
                        multiplier,
                        time_remaining
                    ),
                    refresh=True
                )

                time.sleep(0.05)


        # ----------------------------------------------------
        # LIVE DISPLAY
        # ----------------------------------------------------

        console.clear()

        with Live(
            make_panel(
                question_number,
                factor,
                multiplier,
                5.0
            ),
            console=console,
            refresh_per_second=20
        ) as live:


            # Create timer thread
            timer_thread = threading.Thread(
                target=timer,
                args=(live,)
            )


            # Create input thread
            input_thread = threading.Thread(
                target=get_input,
                daemon=True
            )


            # Start both
            timer_thread.start()

            input_thread.start()


            # ------------------------------------------------
            # MAIN THREAD = REFEREE
            # ------------------------------------------------

            while True:

                # Timer won
                if time_up.is_set():

                    break


                # Player won
                if answer_received.is_set():

                    break


                time.sleep(0.05)


        # ====================================================
        # TIMER WON
        # ====================================================

        if time_up.is_set():

            console.print(
                Panel(
                    Align.center(
                        "[bold red]☠ TIME'S UP ☠[/bold red]\n\n"
                        f"{factor} × {multiplier} = "
                        f"{correct_answer}\n\n"
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


        # ====================================================
        # PLAYER ANSWER
        # ====================================================

        try:

            player_answer = int(player_answer)

        except (ValueError, TypeError):

            player_answer = None


        # ====================================================
        # CORRECT
        # ====================================================

        if player_answer == correct_answer:

            console.print(
                Panel(
                    Align.center(
                        "[bold green]✓ CORRECT![/bold green]\n\n"
                        f"{factor} × {multiplier} = "
                        f"{correct_answer}"
                    ),
                    border_style="green",
                    expand=False
                )
            )

            question_number += 1

            console.input(
                "\n[dim]Press ENTER for the next question...[/dim]"
            )


        # ====================================================
        # WRONG
        # ====================================================

        else:

            console.print(
                Panel(
                    Align.center(
                        "[bold red]☠ GAME OVER ☠[/bold red]\n\n"
                        f"{factor} × {multiplier} = "
                        f"{correct_answer}\n"
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


# ============================================================
# HIGH SCORES
# ============================================================

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

    console.input(
        "\nPress ENTER to return to the menu..."
    )


# ============================================================
# SETTINGS
# ============================================================

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

    console.input(
        "\nPress ENTER to return to the menu..."
    )


# ============================================================
# START GAME
# ============================================================

main_menu()