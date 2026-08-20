from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

console = Console()


def banner():
    console.clear()

    title = """
    title = r"""
     █████╗ ██████╗ ██╗████████╗██╗  ██╗ ██████╗ ███╗   ███╗ █████╗ ███╗   ██╗ ██████╗███████╗██████╗
    ██╔══██╗██╔══██╗██║╚══██╔══╝██║  ██║██╔═══██╗████╗ ████║██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗
    ███████║██████╔╝██║   ██║   ███████║██║   ██║██╔████╔██║███████║██╔██╗ ██║██║     █████╗  ██████╔╝
    ██╔══██║██╔══██╗██║   ██║   ██╔══██║██║   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗
    ██║  ██║██║  ██║██║   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝
    """

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


def play():
    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold yellow]⚔  NEW RUN  ⚔[/bold yellow]\n\n"
                "[dim]The game itself comes next...[/dim]"
            ),
            border_style="yellow",
            expand=False,
            padding=(2, 6)
        )
    )

    console.input("\nPress ENTER to return to the menu...")


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