# 🇵🇭 Pinoy Genius

A two-player online guessing game inspired by **Pinoy Henyo**. One player (the **Guesser**) tries to work out a hidden word. The partner (the **Holder**) can see it, but may only answer **Yes**, **No** or **Maybe**. Guess all 5 words on the board before the 5-minute timer runs out, and do it in as little time as you can.

## Dependencies

| Package | Description | Tested version |
|---|---|---|
| Python | 3.11 or newer | 3.14 |
| [nicegui](https://pypi.org/project/nicegui/) | the web screens and websocket connection between the two players | 4.0.0 |
| [pytest](https://pypi.org/project/pytest/) | runs the tests | 9.2.0 |
| [pytest-asyncio](https://pypi.org/project/pytest-asyncio/) | allows pytest run the simulated-browser tests | 1.5.0 |


## Getting started

### 1. Clone

```
❯ git clone https://github.com/drmanalo/pinoy-genius.git
❯ cd pinoy-genius
```

### 2. Install dependencies

```
❯ python -m venv .venv
❯ source .venv/bin/activate
❯ pip install -r requirements.txt
```
* For `fish shell`: source .venv/bin/activate.fish
* For Windows:    .venv\Scripts\activate

### 3. Run the tests

```
❯ pytest -v
                                                                                                      
tests/test_game.py::test_is_correct_ignores_case_filler_and_punctuation PASSED                                      [  4%]
tests/test_game.py::test_holder_can_only_say_yes_no_maybe PASSED                                                    [  8%]
tests/test_game.py::test_guesser_must_wait_for_answer PASSED                                                        [ 12%]
tests/test_game.py::test_correct_guess_advances_and_all_five_wins PASSED                                            [ 16%]
tests/test_game.py::test_time_runs_out PASSED                                                                       [ 20%]
tests/test_game.py::test_still_playing_before_time_is_up PASSED                                                     [ 24%]
tests/test_game.py::test_pick_board_is_five_distinct_words PASSED                                                   [ 28%]
tests/test_game.py::test_every_word_is_unique_across_categories PASSED                                              [ 32%]
tests/test_game.py::test_rooms_join_and_swap_roles PASSED                                                           [ 36%]
tests/test_main.py::test_lobby_page_loads PASSED                                                                    [ 40%]
tests/test_main.py::test_unknown_room_shows_a_friendly_message PASSED                                               [ 44%]
tests/test_rooms.py::test_create_makes_a_four_letter_code_and_a_guesser_host PASSED                                 [ 48%]
tests/test_rooms.py::test_codes_never_use_confusing_letters PASSED                                                  [ 52%]
tests/test_rooms.py::test_create_never_reuses_a_code PASSED                                                         [ 56%]
tests/test_rooms.py::test_join_is_case_and_space_insensitive_and_makes_a_holder PASSED                              [ 60%]
tests/test_rooms.py::test_unknown_code_is_rejected PASSED                                                           [ 64%]
tests/test_rooms.py::test_third_player_is_rejected_and_not_added PASSED                                             [ 68%]
tests/test_rooms.py::test_blank_name_becomes_player PASSED                                                          [ 72%]
tests/test_rooms.py::test_player_ids_are_unique_and_looked_up PASSED                                                [ 76%]
tests/test_rooms.py::test_partner_of PASSED                                                                         [ 80%]
tests/test_rooms.py::test_partner_of_is_none_when_alone PASSED                                                      [ 84%]
tests/test_rooms.py::test_rooms_are_independent PASSED                                                              [ 88%]
tests/test_rooms.py::test_new_round_swaps_roles_and_makes_a_fresh_game PASSED                                       [ 92%]
tests/test_rooms.py::test_a_new_room_has_a_five_word_board_ready PASSED                                             [ 96%]
tests/test_ui.py::test_full_round PASSED
```

The tests cover the game rules, rooms, the pages, and a full two-player round played by two simulated browsers.

### 4. Run the game

```
❯ python main.py                                                                                                 at 21:59  
NiceGUI ready to go on http://localhost:8080, and http://192.168.x.x:8080
Opening in existing browser session.
```

Open <http://localhost:8080>. One player taps **Gumawa ng room** and shares the 4-letter code. The partner enters it and taps **Sumali sa room**. Then press **Simulan!**.

**Playing from two devices:** both must be on the same network. Open `http://<your-computer's-IP>:8080/` on the second device. Start from the home page, not a `/room/...` address.


## How the game works

### Rules of the original Pinoy Henyo

Summarised from [About Pinoy Henyo](https://pinoyhenyowords.blogspot.com/p/about-pinoy-henyo.html) and the category guides on [pinoyhenyowords.blogspot.com](https://pinoyhenyowords.blogspot.com/2025/07/).

- **Two roles.** The *guesser* (taga-hula) guesses the word. The *responder* (taga-sagot) can see it and answers.
- **Short, fixed time.** The team that guesses in the shortest time wins.
- **Limited answers.** The responder may only say **Oo** (yes), **Hindi** (no) or **Pwede** (maybe). Any other answer costs the team a 3-second penalty.
- **Questions that fit the answers.** The guesser asks yes/no/maybe questions, working from broad to narrow. For example, Tao → Bayani → Babae.
- **Words** are people, places, animals, food or things. They can be Filipino or English, single or compound words, but not phrases.
- **No body language.** In the TV version the guesser's hands are tied and they can't look around or gesture.
- **Category order.** Strategy guides suggest always asking in the same order so you don't skip one: **Tao** (people), **Hayop** (animals), **Bagay** (things), **Lugar** (places), **Pagkain** (food).
- **Tao** is wide. It covers names, professions, illnesses and body parts, inside and out, even skin and blood.
- **"Pwede"** is the honest answer when a word fits two categories or none cleanly. For example, a food that is part solid and part liquid.


The Guesser has quick-category buttons (Tao, Bagay, Lugar, Hayop, Pagkain). The Holder sees the word and its category; the Guesser sees only ❓.

## Project layout

```
main.py                 start the app
pinoy_genius/
  words.py              the word bank (categories → words) and how a board is picked
  game.py               the rules: timer, guessing, Yes/No/Maybe (no screen code!)
  rooms.py              room codes and the two players
  ui.py                 the NiceGUI screens
tests/                  one test file per module
```

Good places to start reading: `words.py`, then `game.py`. Neither imports anything from the screen code.

## Future improvements

- **Run on Kubernetes (minikube).** Add a `Dockerfile` and a `k8s/` folder with a Deployment and a Service, then try it on a local minikube cluster. Rooms live in the app's memory, so use **one replica** for now. Running more would need shared storage such as Redis. The WebSocket connection also needs the ingress timeouts raised.
- **Players' own word bank.** Let players add their own words and categories, saved per room or per account, so family and friends abroad can play with words from their own culture instead of only the default Filipino list.
- **Language support.** Translate the screen text (now Taglish), and let each room pick the language of its word bank. Answer labels could show "Oo / Hindi / Pwede" alongside Yes / No / Maybe.
