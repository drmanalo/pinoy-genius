"""Two simulated browsers play a full round."""
import sys

from nicegui import ui
from nicegui.testing import User


def rooms():
    # The test plugin reloads the app for every test, so an imported `manager`
    # can be stale. Look it up fresh each time.
    return sys.modules["pinoy_genius.ui"].manager.rooms


async def test_full_round(user: User, create_user):
    holder_user = create_user()

    await user.open("/")
    user.find(kind=ui.input, content="Pangalan mo").type("Kuya")
    user.find(content="Gumawa ng room").click()
    await user.should_see("Ibigay ang code", retries=20)
    code = next(iter(rooms()))
    room = rooms()[code]

    await holder_user.open("/")
    holder_user.find(kind=ui.input, content="Pangalan mo").type("Bunso")
    holder_user.find(kind=ui.input, content="Room code").type(code)
    holder_user.find(content="Sumali sa room").click()
    await holder_user.should_see("Simulan!", retries=20)

    holder_user.find(content="Simulan!").click()
    await user.should_see("GUESSER", retries=20)
    await holder_user.should_see("HOLDER", retries=20)
    await holder_user.should_see(room.game.word, retries=20)

    user.find(content="Hayop ba?").click()
    await holder_user.should_see("Hayop ba?", retries=20)
    holder_user.find(kind=ui.button, content="Yes").click()
    await user.should_see("Yes", retries=20)

    for word in list(room.game.board):
        user.find(kind=ui.input).type(word).trigger("keydown.enter")
        await user.should_see("Tama!", retries=20)
    await user.should_see("PANALO", retries=20)
    await holder_user.should_see("PANALO", retries=20)
