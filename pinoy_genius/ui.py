"""Each screen builds its widgets once and returns an update() function
that the page timer calls twice a second to keep the widgets in sync with the Game."""
from nicegui import ui

from .game import FINISHED, PLAYING, WAITING
from .rooms import GUESSER, RoomManager
from .words import CATEGORIES, category_of

manager = RoomManager()


def later(func, arg):
    """Make a click handler that calls func(arg). NiceGUI passes the click event to any
    handler that takes a parameter, so the argument has to be captured in a closure."""
    return lambda: func(arg)


def clock_text(seconds):
    seconds = int(seconds + 0.999)
    return f"{seconds // 60}:{seconds % 60:02d}"


def timer_label(game):
    label = ui.label().classes("text-6xl font-bold")

    def update():
        label.set_text(clock_text(game.remaining()))
        label.classes(add="text-red-600" if game.remaining() < 30 else "",
                      remove="" if game.remaining() < 30 else "text-red-600")
    return update


def progress_label(game):
    label = ui.label().classes("text-xl")

    def update():
        dots = "".join("🟢" if i < game.guessed else "⚪" for i in range(len(game.board)))
        label.set_text(f"{dots}  Salita {min(game.guessed + 1, len(game.board))} / {len(game.board)}")
    return update


def chat_log(game):
    """A list of messages that is rebuilt only when something new was said."""
    box = ui.column().classes("w-full gap-1 max-h-72 overflow-auto")
    shown = {"count": -1}

    def update():
        if shown["count"] == len(game.log):
            return
        shown["count"] = len(game.log)
        box.clear()
        with box:
            for m in game.log:
                if m.kind == "ask":
                    ui.label(f"🗣️ {m.text}").classes("text-lg")
                elif m.kind == "answer":
                    color = {"Yes": "text-green-600", "No": "text-red-600"}.get(m.text, "text-orange-500")
                    ui.label(f"➡️ {m.text}").classes(f"text-lg font-bold ml-6 {color}")
                else:
                    ui.label(f"🎉 {m.text}").classes("text-lg font-bold text-green-700")
    return update


def waiting_view(room, player):
    game = room.game
    ui.label("Pinoy Genius").classes("text-3xl font-bold")
    ui.label(f"Room code: {room.code}").classes("text-4xl font-mono")
    ui.label("Ibigay ang code sa partner mo.").classes("text-gray-500")
    for p in room.players:
        ui.label(f"{p.name} — {p.role}" + ("  (ikaw)" if p is player else "")).classes("text-xl")
    if not room.ready:
        ui.label("Naghihintay ng partner...")
        return lambda: None
    ui.label(f"Ikaw ang {player.role}. 5 salita, 5 minuto!").classes("text-lg")
    ui.button("Simulan!", on_click=game.start).props("size=xl color=green")
    return lambda: None


def guesser_view(room, player):
    game = room.game
    update_timer, update_progress = timer_label(game), progress_label(game)
    ui.label("Ikaw ang GUESSER 🕵️ — hulaan ang salita!").classes("text-lg")
    ui.label("❓ ❓ ❓").classes("text-5xl")
    update_log = chat_log(game)

    def ask(text):
        try:
            game.ask(text)
        except (ValueError, RuntimeError) as e:
            ui.notify(str(e))
        entry.set_value("")

    with ui.row().classes("gap-2"):
        for category in CATEGORIES:
            ui.button(f"{category} ba?", on_click=later(ask, f"{category} ba?")).props("outline dense")
    with ui.row().classes("w-full items-center"):
        entry = ui.input(placeholder="Magtanong o manghula...").classes("grow").on("keydown.enter", lambda: ask(entry.value))
        send = ui.button("Send", on_click=lambda: ask(entry.value))

    def update():
        update_timer()
        update_progress()
        update_log()
        send.set_enabled(game.pending is None)
    return update


def holder_view(room, player):
    game = room.game
    update_timer, update_progress = timer_label(game), progress_label(game)
    ui.label("Ikaw ang HOLDER 🤐 — Yes, No o Maybe lang!").classes("text-lg")
    word = ui.label().classes("text-5xl font-bold text-blue-700")
    hint = ui.label().classes("text-gray-500")
    update_log = chat_log(game)
    question = ui.label().classes("text-2xl")

    def reply(answer):
        try:
            game.answer(answer)
        except (ValueError, RuntimeError) as e:
            ui.notify(str(e))

    with ui.row().classes("gap-4"):
        buttons = [ui.button(a, on_click=later(reply, a)).props(f"size=xl color={c}")
                   for a, c in (("Yes", "green"), ("No", "red"), ("Maybe", "orange"))]

    def update():
        update_timer()
        update_progress()
        update_log()
        if game.state == PLAYING:
            word.set_text(game.word)
            hint.set_text(f"Kategorya: {category_of(game.word)}")
        question.set_text(f"🗣️ {game.pending}" if game.pending else "Naghihintay ng tanong...")
        for b in buttons:
            b.set_enabled(game.pending is not None)
    return update


def finished_view(room, player):
    game = room.game
    if game.won:
        ui.label("🏆 PANALO!").classes("text-5xl font-bold text-green-700")
        ui.label(f"Nahulaan lahat ng {len(game.board)} salita sa {clock_text(game.elapsed())}!").classes("text-2xl")
    else:
        ui.label("⏰ Tapos na ang oras!").classes("text-4xl font-bold text-red-600")
        ui.label(f"Nahulaan: {game.guessed} / {len(game.board)}").classes("text-2xl")
    for i, w in enumerate(game.board):
        ui.label(("✅ " if i < game.guessed else "❌ ") + w).classes("text-xl")

    def play_again():
        if room.game is game:  # only the first click makes a new round
            room.new_round()
    ui.button("Maglaro ulit (palit ng role)", on_click=play_again).props("size=lg color=green")
    return lambda: None


def room_page(code, pid):
    room = manager.rooms.get(code)
    player = room.player(pid) if room else None
    if player is None:
        ui.label("Hindi nahanap ang room.")
        ui.link("Bumalik", "/")
        return
    body = ui.column().classes("items-center w-full max-w-xl mx-auto gap-3 p-4")
    view = {"key": None, "update": lambda: None}

    def refresh():
        game = room.game
        game.tick()
        key = (id(game), game.state, player.role, room.ready)
        if key != view["key"]:
            view["key"] = key
            body.clear()
            with body:
                builder = {WAITING: waiting_view, FINISHED: finished_view,
                           PLAYING: guesser_view if player.role == GUESSER else holder_view}[game.state]
                view["update"] = builder(room, player)
        view["update"]()

    ui.timer(0.5, refresh)


def lobby_page():
    with ui.column().classes("items-center w-full max-w-md mx-auto gap-3 p-4"):
        ui.label("🇵🇭 Pinoy Genius").classes("text-4xl font-bold")
        ui.label("Hulaan ang 5 salita sa loob ng 5 minuto!")
        name = ui.input("Pangalan mo").classes("w-full")
        code = ui.input("Room code").classes("w-full")

        def go(room, player):
            ui.navigate.to(f"/room/{room.code}/{player.id}")

        def create():
            go(*manager.create(name.value))

        def join():
            try:
                go(*manager.join(code.value, name.value))
            except ValueError as e:
                ui.notify(str(e), type="negative")

        ui.button("Gumawa ng room", on_click=create).classes("w-full")
        ui.button("Sumali sa room", on_click=join).classes("w-full").props("outline")


def register_pages():
    ui.page("/")(lobby_page)
    ui.page("/room/{code}/{pid}")(room_page)
