<!-- 
# class ConsoleApp:
#     def __init__(
#         self,
#         card_controller: CardController,
#         game_controller: GameController,
#         user_controller: UserController,
#     ) -> None:
#         self._cat_control = card_controller
#         self._game_control = game_controller
#         self._user_control = user_controller
#         self._running = True
#         self._cur_user: User = None
#         self._cur_player: Player = None
#         self._cur_game: Game = None

#     def run(self) -> None:
#         self._print_menu()
#         while self._running:
#             instr = input(": ").strip()

#             try:
#                 self._handle_instruction(instr)
#             except Exception as exc:
#                 print(f"err: {exc}")

#     def _print_menu(self) -> None:
#         print("\n TECH UI")
#         print("reg : to reg a new user")
#         # print("login : select user/player")
#         print("new : to create a new game")
#         print("gen_decks : to generate decks")
#         print("run \{game_id\} : to run game")
#         print("join \{game_id\} : to add a player to the game")
#         print("game \{game_id\} : show game status")
#         print("play \{card_id|card_title\} : to play card")
#         print("buy \{card_id|card_title\} : to buy card")
#         print("end : to end turn")
#         # print("all : to show all cards")
#         print("hand : show your hand")
#         print("market : show market cards")
#         print("users : to show all users")
#         print("player \{game_id\} : to show all players in a game")
#         print("cur_u : to show current user")
#         print("cur_p : to show current player")
#         print("cur_g : to show current game")
#         print("menu : print menu")
#         print("ext : to exit game")

#     def _handle_instruction(self, instr: str) -> None:
#         instr_arr = list(instr.strip().split())
#         instr = instr_arr[0]
#         attribute = None if len(instr_arr) == 1 else instr_arr[1]
#         match instr:
#             case "reg":
#                 username = input("your username/nickname: ")
#                 user = self._user_control.register_user(username)
#                 self._cur_user = user
#                 self._cur_player = None
#                 print(f"> user {user.id} {user.username} registered and logged")
#             case "new":
#                 game = self._game_control.create_game(self._cur_user.id)
#                 print(f"> game {game.id} was created")
#                 self._cur_game = game
#                 player = self._game_control.join_game(game.id, self._cur_user.id)
#                 self._cur_player = player
#                 print(f"> player {player.id} {player.nickname} was added")
#             case "run":
#                 if not attribute:
#                     print("!> no game id")
#                     return
#                 if if_uuid_str(attribute):
#                     self._game_control.start_game(UUID(attribute))
#                     print("> game started")
#                 else:
#                     print("!> no valid game id")
#             case "join":
#                 user_id = input("which user? id: ").strip()
#                 player = self._game_control.join_game(UUID(attribute), UUID(user_id))
#                 self._cur_player = player
#                 print(f"> player {player.id} {player.nickname} was added")
#             case "game":
#                 print(self._game_control.show_game_state(UUID(attribute)))
#             case "play":
#                 if not attribute:
#                     print("!> no game id")
#                     return
#                 if if_uuid_str(attribute):
#                     self._game_control.play_card(
#                         self._cur_game.id, self._cur_player.id, UUID(attribute)
#                     )
#                 else:
#                     card = self._cat_control.get_card_by_title(attribute)
#                     self._game_control.play_card(
#                         self._cur_game.id, self._cur_player.id, card.id
#                     )
#             case "buy":
#                 # com[1]
#                 pass
#             case "end":
#                 pass
#             case "all":
#                 cards = self._cat_control.list_cards()
#                 for card_data in cards:
#                     print(card_data)
#             case "gen_decks":
#                 if not self._cur_game:
#                     print("!> no active game")
#                     return

#                 self._game_control.generate_decks(self._cur_game.id)
#                 print("> decks generated")
#             case "ext":
#                 self._running = False

#             case "hand":
#                 if not self._cur_game or not self._cur_player:
#                     print("No game or player")
#                     return

#                 cards = self._game_control.show_hand(
#                     self._cur_game.id,
#                     self._cur_player.id,
#                 )

#                 for c in cards:
#                     print(
#                         f"{c['title']} | cost={c['cost']} | power={c['power']} | echo={c['echo']}"
#                     )

#             case "market":
#                 if not self._cur_game:
#                     print("No game")
#                     return

#                 cards = self._game_control.show_market(self._cur_game.id)

#                 for c in cards:
#                     print(
#                         f"{c['title']} | cost={c['cost']} | power={c['power']} | echo={c['echo']}"
#                     )

#             case "menu":
#                 self._print_menu()

#             case "gen_decks":
#                 if not self._cur_game:
#                     print("No active game")
#                     return

#                 self._game_control.generate_decks(self._cur_game.id)
#                 print("Decks generated")

#             case "users":
#                 users = self._user_control.list_users()
#                 for u in users:
#                     print(u)

#             case "players":
#                 if not attribute:
#                     print("!> no game_id")
#                     return

#                 players = self._game_control.list_players(UUID(attribute))
#                 for p in players:
#                     print(p)

#             case "cur_u":
#                 print(f"> {self._cur_user}")

#             case "cur_p":
#                 print(f"> {self._cur_player}")

#             case "cur_g":
#                 print(f"> {self._cur_game}")

#             case _:
#                 print("!> err: unknown instruction") -->
