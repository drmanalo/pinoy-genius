from nicegui import ui

from pinoy_genius.ui import register_pages

register_pages()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Pinoy Genius", host="0.0.0.0", port=8080, reload=False)
