from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
import readchar
from database import (
    save_score,
    get_high_scores,
    reset_high_scores,
    create_table,
    create_profile,
    get_profiles,
    get_profile,
    profile_exists,
    save_profile,
    delete_profile
)
import random
import time
import threading
import msvcrt


TIME_LIMIT = 5.0

# ============================================================
# BANNER
# ============================================================
console = Console()

def banner():

    console.clear()

    title = r"""
     █████╗ ██████╗ ██╗████████╗██╗  ██╗ ██████╗ ███╗   ███╗ █████╗ ███╗╗  ██╗  ██████╗███████╗███████╗
    ██╔══██╗██╔══██╗██║╚══██╔══╝██║  ██║██╔═══██╗████╗ ████║██╔══██╗████╗  ██║║██╔════╝██╔════╝██╔══██╗
    ███████║██████╔╝██║   ██║   ███████║██║   ██║██╔████╔██║███████║██╔██╗ ██║║██║     █████╗  ██████╔╝
    ██╔══██║██╔══██╗██║   ██║   ██╔══██║██║   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║║██║     ██╔══╝  ██╔══██╗
    ██║  ██║██║  ██║██║   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║║╚██████╗███████╗██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═══╝ ╚═════╝╚══════╝╚═╝
    """

    subtitle = r"""
             ≋≋≋  ~~~  THE ROGUE-LIKE MULTIPLICATION GAME  ~~~  ≋≋≋
    """

    greeting = Text()

    greeting.append("━━━━━━ ", style="green")
    greeting.append("✦ ", style="green")
    greeting.append("Welcome, ", style="white")
    greeting.append(CURRENT_PROFILE_NAME, style="cyan")
    greeting.append(" ✦ ", style="green")
    greeting.append("━━━━━━", style="green")

    # Measure the width of the main title
    title_text = Text.from_markup(
        f"[bold cyan]{title}[/bold cyan]"
    )

    title_width = console.measure(title_text).maximum

    console.print(
        Panel(
            Group(
                Align.center(
                    title_text,
                    width=title_width
                ),

                Align.center(
                    Text.from_markup(
                        f"[bold yellow]{subtitle}[/bold yellow]"
                    ),
                    width=title_width
                ),

                Align.center(
                    greeting,
                    width=title_width
                )
            ),
            border_style="bright_blue",
            padding=(1, 2),
            expand=False
        )
    )
def game_rules():

    console.clear()

    rules = (
        "[bold yellow]HOW TO PLAY[/bold yellow]\n\n"
        "• Solve the multiplication problem shown on screen.\n\n"
        "• Type your answer using the number keys.\n\n"
        "• Press ENTER to submit your answer.\n\n"
        "• You begin with 5 seconds.\n\n"
        "• Correct answer → +1 second for the next question.\n\n"
        "• Wrong answer → GAME OVER.\n\n"
        "• Time runs out → GAME OVER.\n\n"
        "• Your score is the number of questions you survive.\n\n"
        "•  ☠ BOSS\n\n"
        "• Every 30 questions, face a Boss with 3 questions.\n\n"
        "• Answer each separately and press SPACE to lock it. All 3 must be correct.\n\n"
        "• Defeat the Boss: +20 seconds and +1 Arcana."
    )

    console.print(
        Panel(
            Align.center(
                rules +
                "\n\n"
                "[bold cyan]⚔  GOOD LUCK  ⚔[/bold cyan]"
            ),
            title="[bold cyan]GAME RULES[/bold cyan]",
            border_style="bright_blue",
            expand=False,
            padding=(2, 6)
        )
    )

    console.input(
        "\n[bold yellow]Press ENTER to start...[/bold yellow]"
    )

# ============================================================
# ITEM INVENTORY
# ============================================================

ITEMS = {
    "chrono_salve": {
        "name": "Chrono-Salve",
        "description": "+10 seconds when time expires",
        "quantity": 0
    },

    "survival_sigil": {
        "name": "Survival Sigil",
        "description": "Survive one wrong answer",
        "quantity": 0
    },

    "momentum_rune": {
        "name": "Momentum Rune",
        "description": "+0.5 seconds for each correct answer",
        "quantity": 0
    }
}

# ============================================================
# META CURRENCY
# ============================================================

ARCANA = 0

# ============================================================
# CURRENT PROFILE
# ============================================================

CURRENT_PROFILE_ID = None
CURRENT_PROFILE_NAME = ""

# ============================================================
# PERMANENT SHOP UPGRADES
# ============================================================

SHOP_ITEMS = {

    "runic_potion": {
        "name": "Runic Potion",
        "description": "Begin every run with 2 Chrono-Salves.",
        "cost": 3,
        "owned": False
    },

    "soul_shard": {
        "name": "Soul Shard",
        "description": "Begin every run with 2 Survival Sigils.",
        "cost": 3,
        "owned": False
    },

    "tempo_crystal": {
        "name": "Tempo Crystal",
        "description": "Begin every run with 2 Momentum Runes.",
        "cost": 3,
        "owned": False
    }
}

# ============================================================
# BUY SHOP ITEM
# ============================================================

def buy_shop_item(item_key):

    global ARCANA

    item = SHOP_ITEMS[item_key]

    console.clear()

    # --------------------------------------------------------
    # ALREADY OWNED
    # --------------------------------------------------------

    if item["owned"]:

        console.print(
            Panel(
                Align.center(
                    "[bold yellow]✦ ALREADY OWNED ✦[/bold yellow]\n\n"
                    f"[bold white]{item['name']}[/bold white]\n\n"
                    "[dim]This permanent enhancement is already yours.[/dim]\n"
                    "[dim]It cannot be purchased again.[/dim]"
                ),
                border_style="yellow",
                expand=False,
                padding=(2, 6)
            )
        )

        console.input(
            "\n[dim]Press ENTER to return to the shop...[/dim]"
        )

        return

    # --------------------------------------------------------
    # NOT ENOUGH ARCANA
    # --------------------------------------------------------

    if ARCANA < item["cost"]:

        console.print(
            Panel(
                Align.center(
                    "[bold red]✦ INSUFFICIENT ARCANA ✦[/bold red]\n\n"
                    f"[bold white]{item['name']}[/bold white]\n\n"
                    f"Cost: [bold cyan]{item['cost']} ✦[/bold cyan]\n"
                    f"You have: [bold yellow]{ARCANA} ✦[/bold yellow]\n\n"
                    "[dim]You need more Arcana.[/dim]"
                ),
                border_style="red",
                expand=False,
                padding=(2, 6)
            )
        )

        console.input(
            "\n[dim]Press ENTER to return to the shop...[/dim]"
        )

        return

    # --------------------------------------------------------
    # PURCHASE CONFIRMATION
    # --------------------------------------------------------

    console.print(
        Panel(
            Align.center(
                f"[bold yellow]PURCHASE {item['name']}?[/bold yellow]\n\n"
                f"{item['description']}\n\n"
                f"Cost: [bold cyan]{item['cost']} ✦[/bold cyan]\n"
                f"Arcana remaining after purchase: "
                f"[bold yellow]{ARCANA - item['cost']} ✦[/bold yellow]"
            ),
            border_style="cyan",
            expand=False,
            padding=(2, 6)
        )
    )

    confirm = console.input(
        "\n[bold yellow]Purchase this artifact? (Y/N) › [/bold yellow]"
    ).strip().upper()

    if confirm != "Y":

        console.print(
            "\n[dim]Purchase cancelled.[/dim]"
        )

        time.sleep(0.7)

        return

    # --------------------------------------------------------
    # COMPLETE PURCHASE
    # --------------------------------------------------------

    ARCANA -= item["cost"]

    item["owned"] = True

    # --------------------------------------------------------
    # SAVE PROFILE AFTER PURCHASE
    # --------------------------------------------------------

    save_current_profile()

    console.print(
        Panel(
            Align.center(
                "[bold green]✦ ARTIFACT ACQUIRED ✦[/bold green]\n\n"
                f"[bold white]{item['name']}[/bold white]\n\n"
                f"{item['description']}\n\n"
                f"Arcana remaining: "
                f"[bold yellow]{ARCANA} ✦[/bold yellow]"
            ),
            border_style="green",
            expand=False,
            padding=(2, 6)
        )
    )

    console.input(
        "\n[dim]Press ENTER to return to the shop...[/dim]"
    )

# ============================================================
# PROFIL ENGINE
# ============================================================

def save_current_profile():

    global CURRENT_PROFILE_ID

    if CURRENT_PROFILE_ID is None:
        return

    save_profile(
        CURRENT_PROFILE_ID,
        ARCANA,
        SHOP_ITEMS["runic_potion"]["owned"],
        SHOP_ITEMS["soul_shard"]["owned"],
        SHOP_ITEMS["tempo_crystal"]["owned"]
    )


# ------------------------------------------------------------
# LOAD PROFILE INTO GAME
# ------------------------------------------------------------

def load_profile_into_game(profile):

    global ARCANA
    global CURRENT_PROFILE_ID
    global CURRENT_PROFILE_NAME

    (
        profile_id,
        name,
        arcana,
        runic_potion_owned,
        soul_shard_owned,
        tempo_crystal_owned
    ) = profile

    CURRENT_PROFILE_ID = profile_id
    CURRENT_PROFILE_NAME = name

    ARCANA = arcana

    SHOP_ITEMS["runic_potion"]["owned"] = bool(
        runic_potion_owned
    )

    SHOP_ITEMS["soul_shard"]["owned"] = bool(
        soul_shard_owned
    )

    SHOP_ITEMS["tempo_crystal"]["owned"] = bool(
        tempo_crystal_owned
    )


# ------------------------------------------------------------
# CREATE NEW PROFILE
# ------------------------------------------------------------

def create_save_state(from_settings=False):

    global CURRENT_PROFILE_ID
    global CURRENT_PROFILE_NAME
    global ARCANA

    while True:

        console.clear()

        console.print(
            Panel(
                Align.center(
                    "[bold cyan]✦ CREATE PROFILE ✦[/bold cyan]\n\n"
                    "[dim]Your name will become your profile.[/dim]\n"
                    "[dim]You can change profiles later from Settings.[/dim]"
                ),
                border_style="cyan",
                expand=False,
                padding=(2, 6)
            )
        )

        name = console.input(
            "\n[bold yellow]Enter your name › [/bold yellow]"
        ).strip()

        # ----------------------------------------------------
        # EMPTY NAME
        # ----------------------------------------------------

        if not name:

            console.print(
                "\n[bold red]✗ A profile needs a name.[/bold red]"
            )

            time.sleep(1)

            continue

        # ----------------------------------------------------
        # DUPLICATE NAME
        # ----------------------------------------------------

        if profile_exists(name):

            console.print(
                "\n[bold red]✗ That profile already exists.[/bold red]"
            )

            console.input(
                "\n[dim]Press ENTER to choose another name...[/dim]"
            )

            continue

        # ----------------------------------------------------
        # CREATE PROFILE
        # ----------------------------------------------------

        profile_id = create_profile(name)

        if profile_id is None:

            console.print(
                "\n[bold red]✗ Could not create profile.[/bold red]"
            )

            time.sleep(1)

            continue

        # ----------------------------------------------------
        # RESET RUNTIME PROGRESSION
        # ----------------------------------------------------

        CURRENT_PROFILE_ID = profile_id
        CURRENT_PROFILE_NAME = name

        ARCANA = 0

        for item in SHOP_ITEMS.values():
            item["owned"] = False

        # ----------------------------------------------------
        # SAVE INITIAL STATE
        # ----------------------------------------------------

        save_current_profile()

        console.clear()

        if not from_settings:
            console.input(
                "\n[dim]Press ENTER to enter the main menu...[/dim]"
            )
        return


# ------------------------------------------------------------
# LOAD EXISTING PROFILES
# ------------------------------------------------------------

def load_save_state():

    profiles = get_profiles()

    if not profiles:

        console.clear()

        console.print(
            Panel(
                Align.center(
                    "[bold yellow]✦ NO PROFILES FOUND ✦[/bold yellow]\n\n"
                    "[dim]There are currently no Arithomancer profiles.[/dim]"
                ),
                border_style="yellow",
                expand=False,
                padding=(2, 6)
            )
        )

        console.input(
            "\n[dim]Press ENTER to return...[/dim]"
        )

        return False

    while True:

        console.clear()

        console.print(
            Panel(
                Align.center(
                    "[bold cyan]✦ LOAD PROFILE ✦[/bold cyan]\n\n"
                    "[dim]Choose the Arithomancer you wish to become.[/dim]"
                ),
                border_style="cyan",
                expand=False,
                padding=(1, 6)
            )
        )

        profile_table = Table(
            box=None,
            show_header=False,
            padding=(0, 3)
        )

        profile_table.add_column(
            "Key",
            style="bold yellow",
            justify="center"
        )

        profile_table.add_column(
            "Profile",
            style="bold white"
        )

        profile_table.add_column(
            "Arcana",
            style="bold cyan",
            justify="center"
        )

        for index, profile in enumerate(profiles, start=1):

            (
                profile_id,
                name,
                arcana,
                runic_potion_owned,
                soul_shard_owned,
                tempo_crystal_owned
            ) = profile

            profile_table.add_row(
                f"[{index}]",
                name,
                f"{arcana} ✦",
            )

        profile_table.add_row(
            "",
            "",
            "",
            ""
        )

        profile_table.add_row(
            "[B]",
            "Back",
            "",
            ""
        )

        console.print(
            Panel(
                Align.center(profile_table),
                border_style="cyan",
                expand=False,
                padding=(1, 4)
            )
        )

        choice = console.input(
            "\n[bold yellow]Choose your profile › [/bold yellow]"
        ).strip().lower()

        # ----------------------------------------------------
        # BACK
        # ----------------------------------------------------

        if choice == "b":
            return False

        # ----------------------------------------------------
        # PROFILE SELECTION
        # ----------------------------------------------------

        if choice.isdigit():

            selection = int(choice)

            if 1 <= selection <= len(profiles):

                selected_profile = profiles[selection - 1]

                load_profile_into_game(selected_profile)

                console.clear()

                console.print(
                    Panel(
                        Align.center(
                            "[bold green]✦ PROFILE LOADED ✦[/bold green]\n\n"
                            f"[bold white]{CURRENT_PROFILE_NAME}[/bold white]\n\n"
                            f"Arcana: [bold yellow]{ARCANA} ✦[/bold yellow]\n\n"
                            "[dim]Welcome back, Arithomancer.[/dim]"
                        ),
                        border_style="green",
                        expand=False,
                        padding=(2, 8)
                    )
                )

                console.input(
                    "\n[dim]Press ENTER to enter the main menu...[/dim]"
                )

                return True

        console.print(
            "\n[bold red]✗ Invalid profile.[/bold red]"
        )

        time.sleep(0.8)


# ------------------------------------------------------------
# FIRST LAUNCH / PROFILE GATE
# ------------------------------------------------------------

def save_state_screen():

    while True:

        console.clear()

        title = Text(
            "✦  A R I T H O M A N C E R  ✦\n",
            style="bold cyan"
        )

        subtitle = Text(
            "THE ROGUE-LIKE MULTIPLICATION GAME\n",
            style="bold yellow"
        )

        tagline = Text(
            "Your journey awaits.",
            style="white"
        )

        console.print(
            Panel(
                Group(
                    Align.center(title),
                    Align.center(subtitle),
                    Align.center(tagline),
                ),
                border_style="bright_blue",
                padding=(2, 6),
                expand=False
            )
        )

        menu = Table(
            box=None,
            show_header=False,
            padding=(0, 3)
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

        menu.add_row(
            "[1]",
            "✦ CREATE PROFILE"
        )

        menu.add_row(
            "[2]",
            "◈ LOAD PROFILE"
        )

        console.print()

        console.print(
            Panel(
                Align.center(menu),
                title="[bold cyan]PROFILES[/bold cyan]",
                border_style="cyan",
                expand=False,
                padding=(1, 5)
            )
        )

        choice = console.input(
            "\n[bold yellow]Choose your destiny › [/bold yellow]"
        ).strip()

        if choice == "1":

            create_save_state()
            return

        elif choice == "2":

            if load_save_state():
                return

        else:

            console.print(
                "\n[bold red]✗ Choose 1 or 2.[/bold red]"
            )

            time.sleep(0.8)

# ============================================================
# ARCANE SHOP
# ============================================================


def shop():

    while True:

        console.clear()

        # ====================================================
        # SHOP HEADER
        # ====================================================

        title = r"""
              · · ─────── ·𖥸· ─────── · ·
             A R C A N E   E M P O R I U M
              · · ─────── ·𖥸· ─────── · · 
        """

        subtitle = (
            "[dim italic]Where power is forged, "
            "and every gift carries a price.[/dim italic]"
        )

        console.print(
            Panel(
                Align.center(
                    f"[bold cyan]{title}[/bold cyan]\n"
                    f"{subtitle}"
                ),
                border_style="bright_blue",
                expand=False,
                padding=(1, 5)
            )
        )

        # ====================================================
        # ARCANA DISPLAY
        # ====================================================

        console.print(
            Align.center(
                "\n[bold yellow]✦  ARCANA  ✦[/bold yellow]\n"
                f"[bold white]{ARCANA}[/bold white]"
            )
        )

        console.print()

        # ====================================================
        # SHOP ITEMS
        # ====================================================

        shop_table = Table(
            box=None,
            show_header=False,
            padding=(1, 3),
            expand=False
        )

        shop_table.add_column(
            "Key",
            style="bold yellow",
            justify="center",
            width=5
        )

        shop_table.add_column(
            "Artifact",
            style="bold white",
            width=25
        )

        shop_table.add_column(
            "Description",
            style="dim white",
            width=42
        )

        shop_table.add_column(
            "Price",
            justify="center",
            width=12
        )

        # ----------------------------------------------------
        # RUNIC POTION
        # ----------------------------------------------------

        if SHOP_ITEMS["runic_potion"]["owned"]:

            runic_artifact = (
                "[dim]⏳  Runic Potion[/dim]"
            )

            runic_description = (
                "[dim]Already claimed.\n"
                "This artifact is permanently yours.[/dim]"
            )

            runic_price = "[dim]SOLD[/dim]"

        else:

            runic_artifact = (
                "[bold cyan]⏳  Runic Potion[/bold cyan]"
            )

            runic_description = (
                "Begin every run with\n"
                "[cyan]2 Chrono-Salves[/cyan]"
            )

            runic_price = "[bold yellow]✦ 3[/bold yellow]"

        shop_table.add_row(
            "[1]",
            runic_artifact,
            runic_description,
            runic_price
        )

        # ----------------------------------------------------
        # SOUL SHARD
        # ----------------------------------------------------

        if SHOP_ITEMS["soul_shard"]["owned"]:

            soul_artifact = (
                "[dim]🔮  Soul Shard[/dim]"
            )

            soul_description = (
                "[dim]Already claimed.\n"
                "This artifact is permanently yours.[/dim]"
            )

            soul_price = "[dim]SOLD[/dim]"

        else:

            soul_artifact = (
                "[bold purple]🔮  Soul Shard[/bold purple]"
            )

            soul_description = (
                "Begin every run with\n"
                "[purple]2 Survival Sigils[/purple]"
            )

            soul_price = "[bold yellow]✦ 3[/bold yellow]"

        shop_table.add_row(
            "[2]",
            soul_artifact,
            soul_description,
            soul_price
        )

        # ----------------------------------------------------
        # TEMPO CRYSTAL
        # ----------------------------------------------------

        if SHOP_ITEMS["tempo_crystal"]["owned"]:

            tempo_artifact = (
                "[dim]⚡  Tempo Crystal[/dim]"
            )

            tempo_description = (
                "[dim]Already claimed.\n"
                "This artifact is permanently yours.[/dim]"
            )

            tempo_price = "[dim]SOLD[/dim]"

        else:

            tempo_artifact = (
                "[bold yellow]⚡  Tempo Crystal[/bold yellow]"
            )

            tempo_description = (
                "Begin every run with\n"
                "[yellow]2 Momentum Runes[/yellow]"
            )

            tempo_price = "[bold yellow]✦ 3[/bold yellow]"

        shop_table.add_row(
            "[3]",
            tempo_artifact,
            tempo_description,
            tempo_price
        )

        # ====================================================
        # SHOP FRAME
        # ====================================================

        console.print(
            Panel(
                Align.center(shop_table),
                border_style="cyan",
                expand=False,
                padding=(1, 2)
            )
        )

        # ====================================================
        # FOOTER
        # ====================================================

        console.print(
            Align.center(
                "\n[bold yellow][1][/bold yellow] "
                "Purchase    "
                "[bold yellow][2][/bold yellow] "
                "Purchase    "
                "[bold yellow][3][/bold yellow] "
                "Purchase    "
                "[bold yellow][4][/bold yellow] "
                "Return"
            )
        )

        choice = console.input(
            "\n[bold cyan]Choose your artifact › [/bold cyan]"
        ).strip()

        # ====================================================
        # RETURN
        # ====================================================

        if choice == "4":

            return

        # ====================================================
        # PURCHASE
        # ====================================================

        elif choice == "1":

            buy_shop_item("runic_potion")

        elif choice == "2":

            buy_shop_item("soul_shard")

        elif choice == "3":

            buy_shop_item("tempo_crystal")

        else:

            console.print(
                "\n[bold red]✗ The Emporium recognizes only 1, 2, 3, or 4.[/bold red]"
            )

            time.sleep(1)

# ============================================================
# BOSS BATTLE
# ============================================================

def boss_battle(time_limit):

    global ARCANA

    # --------------------------------------------------------
    # GENERATE 3 QUESTIONS
    # --------------------------------------------------------

    boss_questions = []

    for _ in range(3):

        factor, multiplier, correct_answer = generate_question(30)

        boss_questions.append({
            "factor": factor,
            "multiplier": multiplier,
            "answer": correct_answer,
            "input": "",
            "locked": False
        })

    # --------------------------------------------------------
    # BOSS TIMER
    # --------------------------------------------------------

    start_time = time.monotonic()

    # --------------------------------------------------------
    # CURRENT QUESTION
    # --------------------------------------------------------

    current_question = 0

    # --------------------------------------------------------
    # DRAW BOSS SCREEN
    # --------------------------------------------------------

    def draw_boss():

        elapsed = time.monotonic() - start_time

        remaining = max(
            0,
            time_limit - elapsed
        )

        # ====================================================
        # QUESTION TABLE
        # ====================================================

        boss_table = Table(
            box=None,
            show_header=False,
            padding=(1, 3),
            expand=False
        )

        boss_table.add_column(
            "STATUS",
            justify="center",
            width=8
        )

        boss_table.add_column(
            "QUESTION",
            justify="center",
            width=15
        )

        boss_table.add_column(
            "ANSWER",
            justify="center",
            width=18
        )

        for index, question in enumerate(
            boss_questions
        ):

            # ----------------------------------------------
            # CURRENT QUESTION
            # ----------------------------------------------

            if index == current_question:

                status = "[bold yellow]▶[/bold yellow]"

            # ----------------------------------------------
            # ALREADY SOLVED
            # ----------------------------------------------

            elif question["locked"]:

                status = "[bold green]✓[/bold green]"

            # ----------------------------------------------
            # NOT YET REACHED
            # ----------------------------------------------

            else:

                status = "[dim]○[/dim]"

            # ----------------------------------------------
            # ANSWER DISPLAY
            # ----------------------------------------------

            if question["locked"]:

                answer_display = (
                    f"[bold green]"
                    f"{question['input']}"
                    f" ✓"
                    f"[/bold green]"
                )

            elif index == current_question:

                answer_display = (
                    f"[bold cyan]"
                    f"{question['input']}"
                    f"█"
                    f"[/bold cyan]"
                )

            else:

                answer_display = "[dim]—[/dim]"

            boss_table.add_row(
                status,
                (
                    f"[bold white]"
                    f"{question['factor']} × "
                    f"{question['multiplier']}"
                    f"[/bold white]"
                ),
                answer_display
            )

        # ====================================================
        # TIMER BAR
        # ====================================================

        bar_length = 36

        if time_limit > 0:

            filled = int(
                bar_length *
                remaining /
                time_limit
            )

        else:

            filled = 0

        filled = max(
            0,
            min(
                bar_length,
                filled
            )
        )

        timer_bar = (
            "█" * filled
            +
            "░" * (bar_length - filled)
        )

        # ====================================================
        # ITEMS
        # ====================================================

        item_lines = []

        if ITEMS["chrono_salve"]["quantity"] > 0:

            item_lines.append(
                f"[cyan]⏳ Chrono-Salve ×"
                f"{ITEMS['chrono_salve']['quantity']}[/cyan]"
            )

        if ITEMS["survival_sigil"]["quantity"] > 0:

            item_lines.append(
                f"[magenta]🔮 Survival Sigil ×"
                f"{ITEMS['survival_sigil']['quantity']}[/magenta]"
            )

        if ITEMS["momentum_rune"]["quantity"] > 0:

            item_lines.append(
                f"[yellow]⚡ Momentum Rune ×"
                f"{ITEMS['momentum_rune']['quantity']}[/yellow]"
            )

        items_text = "   ".join(item_lines)

        # ====================================================
        # SCREEN
        # ====================================================

        content_parts = [
            "[bold red]☠  B O S S   B A T T L E  ☠[/bold red]\n\n",

            "[bold yellow]"
            "Solve all three equations."
            "[/bold yellow]\n",

            "[dim]"
            "Type each answer separately and press SPACE to lock it."
            "[/dim]\n\n",

            boss_table,

            "\n[bold yellow]TIME REMAINING[/bold yellow]\n",

            f"[bold cyan]{timer_bar}[/bold cyan]\n",

            f"[bold white]{remaining:.1f}s[/bold white]"
        ]

        if items_text:
            content_parts.append(
                f"\n\n{items_text}"
            )

        content = Group(*content_parts)

        return Panel(
            Align.center(content),
            border_style="red",
            expand=False,
            padding=(2, 5)
        ), remaining

    # ========================================================
    # BOSS LOOP
    # ========================================================

    with Live(
            draw_boss()[0],
            console=console,
            refresh_per_second=20
    ) as live:

        while True:
            # ------------------------------------------------
            # TIMER CHECK
            # ------------------------------------------------

            screen, remaining = draw_boss()

            live.update(
                screen,
                refresh=True
            )

            # ----------------------------------------------------
            # TIME UP
            # ----------------------------------------------------

            if remaining <= 0:

                # ================================================
                # CHRONO-SALVE
                # ================================================

                if ITEMS["chrono_salve"]["quantity"] > 0:

                    ITEMS["chrono_salve"]["quantity"] -= 1

                    live.update(
                        Panel(
                            Align.center(
                                "[bold cyan]"
                                "⏳ CHRONO-SALVE ACTIVATED!"
                                "[/bold cyan]\n\n"

                                "[bold white]"
                                "+10 seconds"
                                "[/bold white]\n\n"

                                f"Chrono-Salves remaining: "
                                f"[bold cyan]"
                                f"{ITEMS['chrono_salve']['quantity']}"
                                f"[/bold cyan]"
                            ),
                            border_style="cyan",
                            expand=False,
                            padding=(2, 6)
                        ),
                        refresh=True
                    )

                    # --------------------------------------------
                    # ADD TIME
                    # --------------------------------------------

                    time_limit += 10

                    # Restart timer from current moment.
                    start_time = time.monotonic()

                    time.sleep(1)

                    continue

                # ================================================
                # GAME OVER
                # ================================================

                live.update(
                    Panel(
                        Align.center(
                            "[bold red]"
                            "☠ BOSS BATTLE FAILED ☠"
                            "[/bold red]\n\n"

                            "[white]"
                            "Time ran out."
                            "[/white]"
                        ),
                        border_style="red",
                        expand=False,
                        padding=(2, 6)
                    ),
                    refresh=True
                )

                time.sleep(1.5)

                return False, time_limit

                return False

            # ====================================================
            # ALL THREE SOLVED
            # ====================================================

            if current_question >= 3:

                # -----------------------------------------------
                # BOSS DEFEATED
                # -----------------------------------------------

                ARCANA += 1
                save_current_profile()


                time_limit += 20

                console.clear()

                live.update(
                    Panel(
                        Align.center(
                            "[bold green]"
                            "⚔  B O S S   D E F E A T E D  ⚔"
                            "[/bold green]\n\n"

                            "[bold yellow]"
                            "✦ +20 seconds"
                            "[/bold yellow]\n"

                            "[bold cyan]"
                            "✦ +1 Arcana"
                            "[/bold cyan]\n\n"

                            f"[dim]"
                            f"Arcana: {ARCANA}"
                            f"[/dim]"
                        ),
                        border_style="green",
                        expand=False,
                        padding=(2, 8)
                    ),
                    refresh=True
                )

                time.sleep(1.5)

                return True, time_limit

            # ====================================================
            # READ KEY
            # ====================================================

            if not msvcrt.kbhit():
                time.sleep(0.05)
                continue

            key = readchar.readkey()

            # ====================================================
            # NUMBER
            # ====================================================

            if key.isdigit():

                # -----------------------------------------------
                # ONLY CURRENT QUESTION ACCEPTS INPUT
                # -----------------------------------------------

                boss_questions[current_question]["input"] += key

            # ====================================================
            # BACKSPACE
            # ====================================================

            elif key == readchar.key.BACKSPACE:

                boss_questions[current_question]["input"] = (
                    boss_questions[current_question]["input"][:-1]
                )

            # ====================================================
            # SPACE = LOCK ANSWER
            # ====================================================

            elif key == " ":

                answer_text = (
                    boss_questions[current_question]["input"]
                )

                # ------------------------------------------------
                # BLANK ANSWER
                # ------------------------------------------------

                if answer_text == "":

                    continue

                # ------------------------------------------------
                # CHECK ANSWER
                # ------------------------------------------------

                try:

                    player_answer = int(
                        answer_text
                    )

                except ValueError:

                    continue

                correct_answer = (
                    boss_questions[current_question]["answer"]
                )

                # =================================================
                # CORRECT
                # =================================================

                if player_answer == correct_answer:

                    boss_questions[current_question]["locked"] = True

                    current_question += 1

                    continue

                # =================================================
                # WRONG
                # =================================================

                else:

                    # --------------------------------------------
                    # SURVIVAL SIGIL
                    # --------------------------------------------

                    if ITEMS["survival_sigil"]["quantity"] > 0:

                        ITEMS["survival_sigil"]["quantity"] -= 1

                        console.clear()

                        live.update(
                            Panel(
                                Align.center(
                                    "[bold magenta]"
                                    "🔮 SURVIVAL SIGIL ACTIVATED!"
                                    "[/bold magenta]\n\n"

                                    "[bold white]"
                                    "The wrong answer has been forgiven!"
                                    "[/bold white]\n\n"

                                    f"Survival Sigils remaining: "
                                    f"[bold magenta]"
                                    f"{ITEMS['survival_sigil']['quantity']}"
                                    f"[/bold magenta]"
                                ),
                                border_style="magenta",
                                expand=False,
                                padding=(2, 6)
                            ),
                            refresh=True
                        )

                        # ----------------------------------------
                        # RESET CURRENT ANSWER
                        # ----------------------------------------

                        boss_questions[current_question][
                            "input"
                        ] = ""

                        time.sleep(1)

                        continue

                    # --------------------------------------------
                    # NO SIGIL
                    # --------------------------------------------

                    console.clear()

                    console.print(
                        Panel(
                            Align.center(
                                "[bold red]"
                                "☠ BOSS BATTLE FAILED ☠"
                                "[/bold red]\n\n"
    
                                "[white]"
                                "Your answer was incorrect."
                                "[/white]\n\n"
    
                                "[dim]"
                                "The boss remains undefeated."
                                "[/dim]"
                            ),
                            border_style="red",
                            expand=False,
                            padding=(2, 6)
                        )
                    )

                time.sleep(1.5)

                return False, time_limit


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
        menu.add_row("[2]", "⚙  SETTINGS")
        menu.add_row("[3]", "⚗  SHOP")
        menu.add_row("[4]", "🏆 HIGH SCORES")
        menu.add_row("[5]", "📜 CREDITS")
        menu.add_row("[6]", "🚪 EXIT")


        menu_panel = Panel(
            Align.center(menu),
            title="[bold cyan]MAIN MENU[/bold cyan]",
            border_style="cyan",
            expand=False,
            padding=(1, 4)
        )


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
            game_rules()
            play()

        elif choice == "2":

            settings()

        elif choice == "3":

            shop()

        elif choice == "4":

            high_scores()

        elif choice == "5":

            credits()

        elif choice == "6":

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
    time_limit,
    time_remaining
):

    bar_length = 20

    filled = int(
        bar_length * time_remaining / time_limit
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
        width=80,
        padding=(2, 8)
    )

def make_game_screen(
    question_number,
    factor,
    multiplier,
    time_limit,
    time_remaining,
    player_answer
):

    game_panel = make_panel(
        question_number,
        factor,
        multiplier,
        time_limit,
        time_remaining
    )

    # ------------------------------------------------
    # ITEM HUD
    # ------------------------------------------------

    item_lines = []

    chrono_salve_count = ITEMS["chrono_salve"]["quantity"]
    survival_sigil_count = ITEMS["survival_sigil"]["quantity"]
    momentum_rune_count = ITEMS["momentum_rune"]["quantity"]

    if chrono_salve_count > 0:
        item_lines.append(
            f"[bold cyan]⏳ Chrono-Salve ×{chrono_salve_count}[/bold cyan]"
        )

    if survival_sigil_count > 0:
        item_lines.append(
            f"[bold purple]🔮 Survival Sigil ×{survival_sigil_count}[/bold purple]"
        )

    if momentum_rune_count > 0:
        item_lines.append(
            f"[bold yellow]⚡ Momentum Rune ×{momentum_rune_count}[/bold yellow]"
        )

    item_text = "\n".join(item_lines)

    input_content = (
        f"[bold cyan]Your answer › [/bold cyan]"
        f"[bold white]{player_answer}█[/bold white]"
    )

    if item_text:
        input_content += f"\n\n{item_text}"

    input_panel = Panel(
        Align.left(input_content),
        border_style="cyan",
        expand=False,
        width=80
    )

    return Group(
        game_panel,
        input_panel
    )
# ===========================================================
# INPUT NAME LOOP
# ===========================================================
def get_player_name():

    while True:

        player_name = console.input(
            "\n[bold cyan]Enter your name › [/bold cyan]"
        ).strip()

        if player_name:
            return player_name

        choice = console.input(
            "\n[bold yellow]Do you want to continue without a name? (Y/N) › [/bold yellow]"
        ).strip().upper()

        if choice == "Y":
            return ""

        elif choice == "N":
            continue

        else:
            console.print(
                "\n[bold red]Please enter Y or N.[/bold red]"
            )

# ============================================================
# ITEM REWARD
# ============================================================

def choose_item_reward():

    console.clear()

    reward_table = Table(
        title="[bold yellow]⚗  ARITHOMANCER REWARD  ⚗[/bold yellow]",
        border_style="bright_blue",
        padding=(0, 3)
    )

    reward_table.add_column(
        "KEY",
        style="bold cyan",
        justify="center"
    )

    reward_table.add_column(
        "ITEM",
        style="bold white"
    )

    reward_table.add_column(
        "EFFECT",
        style="dim white"
    )

    reward_table.add_row(
        "[1]",
        "⏳ Chrono-Salve",
        "+10 seconds when time expires"
    )

    reward_table.add_row(
        "[2]",
        "🔮 Survival Sigil",
        "Survive one wrong answer"
    )

    reward_table.add_row(
        "[3]",
        "⚡ Momentum Rune",
        "+0.5 seconds for each correct answer"
    )

    console.print(
        Panel(
            Align.center(
                "[bold yellow]✦ MILESTONE REACHED ✦[/bold yellow]\n\n"
                "Choose one item to add to your inventory.\n"
            ),
            border_style="yellow",
            expand=False,
            padding=(1, 4)
        )
    )

    console.print(reward_table)

    while True:

        choice = console.input(
            "\n[bold yellow]Choose your reward › [/bold yellow]"
        ).strip()

        if choice == "1":

            ITEMS["chrono_salve"]["quantity"] += 1

            console.print(
                Panel(
                    Align.center(
                        "[bold cyan]⏳ CHRONO-SALVE ACQUIRED![/bold cyan]\n\n"
                        "+1 Chrono-Salve\n\n"
                        f"Inventory: "
                        f"{ITEMS['chrono_salve']['quantity']}"
                    ),
                    border_style="cyan",
                    expand=False,
                    padding=(2, 6)
                )
            )

            break

        elif choice == "2":

            ITEMS["survival_sigil"]["quantity"] += 1

            console.print(
                Panel(
                    Align.center(
                        "[bold purple]🔮 SURVIVAL SIGIL ACQUIRED![/bold purple]\n\n"
                        "+1 Survival Sigil\n\n"
                        f"Inventory: "
                        f"{ITEMS['survival_sigil']['quantity']}"
                    ),
                    border_style="purple",
                    expand=False,
                    padding=(2, 6)
                )
            )

            break

        elif choice == "3":

            ITEMS["momentum_rune"]["quantity"] += 1

            console.print(
                Panel(
                    Align.center(
                        "[bold yellow]⚡ MOMENTUM RUNE ACQUIRED![/bold yellow]\n\n"
                        "+1 Momentum Rune\n\n"
                        f"Inventory: "
                        f"{ITEMS['momentum_rune']['quantity']}"
                    ),
                    border_style="yellow",
                    expand=False,
                    padding=(2, 6)
                )
            )

            break

        else:

            console.print(
                "\n[bold red]✗ Choose 1, 2, or 3.[/bold red]"
            )

    time.sleep(1.2)

# ============================================================
# PLAY
# ============================================================

def play():

    # ========================================================
    # PREPARE STARTING INVENTORY
    # ========================================================

    # Every new run starts with an empty inventory.
    for item in ITEMS.values():
        item["quantity"] = 0

    # ========================================================
    # APPLY PERMANENT SHOP UPGRADES
    # ========================================================

    if SHOP_ITEMS["runic_potion"]["owned"]:
        ITEMS["chrono_salve"]["quantity"] = 2

    if SHOP_ITEMS["soul_shard"]["owned"]:
        ITEMS["survival_sigil"]["quantity"] = 2

    if SHOP_ITEMS["tempo_crystal"]["owned"]:
        ITEMS["momentum_rune"]["quantity"] = 2

    # ========================================================
    # START RUN
    #
    question_number = 1
    time_limit = 5.0

    while True:

        # ----------------------------------------------------
        # GENERATE NEW QUESTION
        # ----------------------------------------------------

        factor, multiplier, correct_answer = generate_question(
            question_number
        )

        # ----------------------------------------------------
        # FIGHT THIS QUESTION
        # ----------------------------------------------------

        while True:

            # ------------------------------------------------
            # STATE FOR THIS TIMER ATTEMPT
            # ------------------------------------------------

            time_up = threading.Event()
            stop_timer = threading.Event()
            player_answer = ""
            remaining_time = time_limit

            # ------------------------------------------------
            # TIMER THREAD
            # ------------------------------------------------

            def timer(live, current_time_limit):

                start_time = time.monotonic()

                while not stop_timer.is_set():

                    elapsed = time.monotonic() - start_time
                    time_remaining = current_time_limit - elapsed
                    nonlocal remaining_time
                    remaining_time = time_remaining

                    if time_remaining <= 0:

                        live.update(
                            make_game_screen(
                                question_number,
                                factor,
                                multiplier,
                                current_time_limit,
                                0,
                                player_answer
                            ),
                            refresh=True
                        )

                        time_up.set()
                        break

                    live.update(
                        make_game_screen(
                            question_number,
                            factor,
                            multiplier,
                            current_time_limit,
                            time_remaining,
                            player_answer
                        ),
                        refresh=True
                    )

                    time.sleep(0.05)

            # ------------------------------------------------
            # LIVE DISPLAY
            # ------------------------------------------------

            console.clear()

            with Live(
                make_game_screen(
                    question_number,
                    factor,
                    multiplier,
                    time_limit,
                    time_limit,
                    player_answer
                ),
                console=console,
                refresh_per_second=20
            ) as live:

                timer_thread = threading.Thread(
                    target=timer,
                    args=(live, time_limit)
                )

                timer_thread.start()

                # --------------------------------------------
                # MAIN THREAD = REFEREE
                # --------------------------------------------

                while True:

                    if time_up.is_set():
                        break

                    if msvcrt.kbhit():

                        key = readchar.readkey()

                        if key == readchar.key.ENTER:

                            # Blank input is NOT an answer.
                            # Keep the timer running.
                            if not player_answer:
                                continue

                            stop_timer.set()
                            break

                        elif key == readchar.key.BACKSPACE:

                            player_answer = player_answer[:-1]

                        elif key.isdigit():

                            player_answer += key

                    time.sleep(0.01)

                timer_thread.join()

            # ------------------------------------------------
            # PLAYER ANSWER RECEIVED
            # ------------------------------------------------

            if not time_up.is_set():

                if not player_answer:
                    continue

                try:
                    player_answer = int(player_answer)

                except (ValueError, TypeError):
                    continue

                # ============================================
                # CORRECT
                # ============================================

                if player_answer == correct_answer:

                    momentum_bonus = ITEMS["momentum_rune"]["quantity"] * 0.5

                    time_limit += 1.0 + momentum_bonus

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

                    # ------------------------------------------------
                    # QUESTIONS COMPLETED
                    # ------------------------------------------------

                    completed_questions = question_number

                    # ------------------------------------------------
                    # MILESTONE REWARD
                    # ------------------------------------------------

                    if completed_questions % 10 == 0:
                        choose_item_reward()

                    # ------------------------------------------------
                    # BOSS BATTLE
                    # ------------------------------------------------

                    if completed_questions % 30 == 0:

                        boss_won, time_limit = boss_battle(time_limit)

                        if not boss_won:
                            player_name = get_player_name()

                            save_score(
                                player_name,
                                completed_questions
                            )

                            high_scores()
                            return
                    # ------------------------------------------------
                    # MOVE TO NEXT QUESTION
                    # ------------------------------------------------

                    question_number += 1

                    time.sleep(1)

                    break

                # ============================================
                # WRONG
                # ============================================

                else:

                    if ITEMS["survival_sigil"]["quantity"] > 0:
                        ITEMS["survival_sigil"]["quantity"] -= 1

                        console.print(
                            Panel(
                                Align.center(
                                    "[bold purple]🔮 SURVIVAL SIGIL ACTIVATED![/bold purple]\n\n"
                                    "[white]Your mistake has been forgiven.[/white]\n\n"
                                    f"Survival Sigils remaining: "
                                    f"{ITEMS['survival_sigil']['quantity']}"
                                ),
                                border_style="purple",
                                expand=False,
                                padding=(2, 6)
                            )
                        )

                        # The timer has already been stopped.
                        # Preserve exactly how much time was left.
                        time_limit = max(0.1, remaining_time)

                        # The next inner-loop iteration gets
                        # a fresh input field.
                        time.sleep(0.5)

                        continue

                    # ----------------------------------------
                    # NO SURVIVAL SIGIL → GAME OVER
                    # ----------------------------------------

                    console.print(
                        Panel(
                            Align.center(
                                "[bold red]☠ GAME OVER ☠[/bold red]\n\n"
                                f"{factor} × {multiplier} = "
                                f"{correct_answer}\n\n"
                                f"You answered: {player_answer}\n\n"
                                f"[yellow]Questions survived: "
                                f"{question_number - 1}[/yellow]"
                            ),
                            border_style="red",
                            expand=False,
                            padding=(2, 6)
                        )
                    )

                    player_name = get_player_name()

                    save_score(
                        player_name,
                        question_number - 1
                    )
                    high_scores()
                    return
            # ------------------------------------------------
            # TIMER EXPIRED
            # ------------------------------------------------

            if time_up.is_set():

                if ITEMS["chrono_salve"]["quantity"] > 0:

                    ITEMS["chrono_salve"]["quantity"] -= 1

                    console.print(
                        Panel(
                            Align.center(
                                "[bold cyan]⏳ CHRONO-SALVE ACTIVATED![/bold cyan]\n\n"
                                "[yellow]+10 seconds![/yellow]\n\n"
                                f"Chrono-Salves remaining: "
                                f"{ITEMS['chrono_salve']['quantity']}"
                            ),
                            border_style="cyan",
                            expand=False,
                            padding=(2, 6)
                        )
                    )

                    time_limit = 10.0

                    time.sleep(1)

                    continue

                # --------------------------------------------
                # NO CHRONO-SALVE → GAME OVER
                # --------------------------------------------

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

                player_name = get_player_name()

                save_score(
                    player_name,
                    question_number - 1
                )
                high_scores()
                return


# ============================================================
# CREDITS
# ============================================================

def credits():

    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold cyan]ARITHOMANCER[/bold cyan]\n\n"
                "[bold yellow]Version 1.0[/bold yellow]\n\n"
                "Programmed by [bold green]beo-wu1f[/bold green]"
            ),
            title="[bold cyan]CREDITS[/bold cyan]",
            border_style="cyan",
            expand=False,
            padding=(2, 8)
        )
    )

    console.input(
        "\n[dim]Press ENTER to return to the menu...[/dim]"
    )


# ======================================================
# HIGH SCORES
# ======================================================
def high_scores():

    console.clear()

    scores = get_high_scores()

    table = Table(
        title="🏆 HIGH SCORES",
        border_style="cyan"
    )

    table.add_column("#", justify="center")
    table.add_column("PLAYER")
    table.add_column("QUESTIONS SURVIVED", justify="center")
    table.add_column("DATE", justify="center")

    for position, score in enumerate(scores, start=1):

        player, questions, played_date = score

        table.add_row(
            str(position),
            player,
            str(questions),
            played_date
        )

    console.print(table)

    console.input(
        "\n[dim]Press ENTER to return to the menu...[/dim]"
    )

# ============================================================
# REMOVE CURRENT PROFILE
# ============================================================

def delete_current_profile():

    global CURRENT_PROFILE_ID
    global CURRENT_PROFILE_NAME
    global ARCANA

    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold red]✦ REMOVE PROFILE ✦[/bold red]\n\n"
                f"[bold white]{CURRENT_PROFILE_NAME}[/bold white]\n\n"
                "[yellow]This will permanently delete this profile.[/yellow]\n"
                "[dim]Arcana and permanent shop progress will be lost.[/dim]\n\n"
                "[bold red]This action cannot be undone.[/bold red]"
            ),
            border_style="red",
            expand=False,
            padding=(2, 8)
        )
    )

    choice = console.input(
        "\n[bold yellow]Remove this profile? (Y/N) › [/bold yellow]"
    ).strip().lower()

    if choice != "y":

        console.print(
            "\n[bold cyan]✦ Profile removal cancelled.[/bold cyan]"
        )

        time.sleep(0.8)

        return False

    # --------------------------------------------------------
    # DELETE FROM DATABASE
    # --------------------------------------------------------

    delete_profile(CURRENT_PROFILE_ID)

    # --------------------------------------------------------
    # CLEAR CURRENT PROFILE
    # --------------------------------------------------------

    CURRENT_PROFILE_ID = None
    CURRENT_PROFILE_NAME = ""
    ARCANA = 0

    # --------------------------------------------------------
    # RESET PERMANENT SHOP STATE
    # --------------------------------------------------------

    for item in SHOP_ITEMS.values():

        item["owned"] = False

    # --------------------------------------------------------
    # CONFIRM DELETION
    # --------------------------------------------------------

    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold green]✦ PROFILE REMOVED ✦[/bold green]\n\n"
                "[white]The profile has been permanently deleted.[/white]"
            ),
            border_style="green",
            expand=False,
            padding=(2, 8)
        )
    )

    console.input(
        "\n[dim]Press ENTER to continue...[/dim]"
    )

    return True

# ============================================================
# SETTINGS
# ============================================================

def settings():

    while True:

        console.clear()

        settings_table = Table(
            box=None,
            show_header=False,
            padding=(0, 2)
        )

        settings_table.add_column(
            "Key",
            style="bold yellow",
            justify="center"
        )

        settings_table.add_column(
            "Action",
            style="bold white"
        )

        settings_table.add_row(
            "[1]",
            "Create Profile"
        )

        settings_table.add_row(
            "[2]",
            "Change Profile"
        )

        settings_table.add_row(
            "[3]",
            "Remove Profile"
        )

        settings_table.add_row(
            "[4]",
            "Reset High Scores"
        )

        settings_table.add_row(
            "[5]",
            "Back"
        )

        console.print(
            Panel(
                Align.center(settings_table),
                title="[bold cyan]SETTINGS[/bold cyan]",
                border_style="cyan",
                expand=False,
                padding=(1, 4)
            )
        )

        choice = console.input(
            "\n[bold yellow]Choose an option › [/bold yellow]"
        ).strip()

        # ----------------------------------------------------
        # CREATE PROFILE
        # ----------------------------------------------------

        if choice == "1":

            create_save_state(from_settings=True)

            # Return to main menu after creating profile
            break

        # ----------------------------------------------------
        # CHANGE PROFILE
        # ----------------------------------------------------

        elif choice == "2":

            if load_save_state():

                # Return to main menu after changing profile
                break

        # ----------------------------------------------------
        # REMOVE PROFILE
        # ----------------------------------------------------

        elif choice == "3":

            if delete_current_profile():

                # No active profile remains.
                # Send player back to profile selection.
                save_state_screen()

                # After creating/loading a new profile,
                # return to the main menu.
                break

        # ----------------------------------------------------
        # RESET HIGH SCORES
        # ----------------------------------------------------

        elif choice == "4":

            reset_high_scores_confirmation()

        # ----------------------------------------------------
        # BACK
        # ----------------------------------------------------

        elif choice == "5":

            break

        else:

            console.print(
                "\n[bold red]✗ Invalid choice.[/bold red]"
            )

            console.input(
                "\nPress ENTER to continue..."
            )

# ============================================================
# DELETE PROFILE
# ============================================================

def delete_profile_confirmation():

    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold red]✦ DELETE PROFILE ✦[/bold red]\n\n"
                f"[bold white]{CURRENT_PROFILE_NAME}[/bold white]\n\n"
                "[yellow]This will permanently delete this profile.[/yellow]\n"
                "[dim]Arcana and permanent shop progress will be lost.[/dim]\n\n"
                "[bold red]Are you absolutely sure?[/bold red]"
            ),
            border_style="red",
            expand=False,
            padding=(2, 8)
        )
    )

    choice = console.input(
        "\n[bold yellow]Delete this profile? [Y/N] › [/bold yellow]"
    ).strip().lower()

    if choice != "y":
        console.print(
            "\n[bold cyan]✦ Profile deletion cancelled.[/bold cyan]"
        )
        time.sleep(1)
        return

# =================================================
# RESET HIGH SCORES
# ===========================================================
def reset_high_scores_confirmation():

    console.clear()

    console.print(
        Panel(
            Align.center(
                "[bold red]⚠ RESET HIGH SCORES[/bold red]\n\n"
                "This will permanently delete\n"
                "all high scores.\n\n"
                "[bold yellow]Are you sure?[/bold yellow]"
            ),
            border_style="red",
            expand=False,
            padding=(2, 6)
        )
    )

    choice = console.input(
        "\n[bold yellow]Type YES to confirm › [/bold yellow]"
    )

    if choice == "YES":

        reset_high_scores()

        console.print(
            Panel(
                Align.center(
                    "[bold green]✓ HIGH SCORES RESET[/bold green]\n\n"
                    "The leaderboard is now empty."
                ),
                border_style="green",
                expand=False,
                padding=(2, 6)
            )
        )

    else:

        console.print(
            Panel(
                Align.center(
                    "[bold cyan]Reset cancelled.[/bold cyan]"
                ),
                border_style="cyan",
                expand=False
            )
        )

    console.input(
        "\n[dim]Press ENTER to continue...[/dim]"
    )

# ===========================================================
# SHOW INVENTORY
# ==========================================================
def show_inventory():

    console.clear()

    inventory = Table(
        title="⚗  ARITHOMANCER INVENTORY",
        border_style="cyan"
    )

    inventory.add_column("ITEM", style="bold yellow")
    inventory.add_column("QUANTITY", justify="center", style="bold cyan")
    inventory.add_column("EFFECT")

    for item in ITEMS.values():

        inventory.add_row(
            item["name"],
            str(item["quantity"]),
            item["description"]
        )

    console.print(inventory)

    console.input(
        "\n[dim]Press ENTER to return...[/dim]"
    )


# ============================================================
# START GAME
# ============================================================
create_table()
save_state_screen()
main_menu()