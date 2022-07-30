import enum
from json import JSONDecodeError
from typing import List, Any
import sys
import pypresence as drp
import time
import requests
from pypresence import DiscordNotFound
from requests.exceptions import ConnectionError

class MyPresence:
    class ScreenState:
        class BaseType(enum.Enum):
            def get_key(self):
                return self.value[0]

            def get_state(self):
                return self.value[1]

            @classmethod
            def get_keys(cls) -> List[Any]:
                return cls.__members__.values()

        class TypeTopTop(BaseType):
            Loading = "ScreenLoading", "Loading"
            Credits = "ScreenCreditsSC2", "Watching Credits"
            NewUser = "ScreenNewUser", "Creating new user"

        class TypeTop(BaseType):
            Score = "ScreenScore", "Viewing Score Screen"
            Profile = "ScreenUserProfile", "Viewing Profile"
            Group = "ScreenClubProfile", "Viewing Clan/Group"

        class TypeMid(BaseType):
            Lobby = "ScreenBattleLobby", "In Lobby"
            Cutscene = "ScreenMovie", "Watching a Cutscene"
            MapDetails = "ScreenBattleMapProfile", "Looking at Map Details"

        class TypeLow(BaseType):
            Login = "ScreenLoginUnified", "On the Login Page"
            Home = "ScreenHome", "On the Home Screen"
            Campaign = "ScreenSingle", "On the Campaign Page"
            Coop = "ScreenCoopCampaign", "On the Co-op Page"
            Multiplayer = "ScreenMultiplayer", "Browsing Versus"
            Custom = "ScreenCustom", "Browsing Custom Games"
            Collection = "ScreenCollection", "Browsing Collections"
            Replay = "ScreenReplay", "Browsing Replays"

        __screen_order = [
            TypeLow,
            TypeMid,
            TypeTop,
            TypeTopTop
        ]
        __prev_screen_type: BaseType = TypeLow.Login
        screen_type: BaseType = TypeTopTop.Loading

        @classmethod
        def is_screen_changed(cls):
            return cls.__prev_screen_type != cls.screen_type

        @classmethod
        def update_prev_screen(cls):
            cls.__prev_screen_type = cls.screen_type

        @classmethod
        def set_none(cls):
            cls.screen_type = None

        @classmethod
        def update(cls, screens):
            for screen_type in cls.__screen_order:
                for state in screen_type.get_keys():
                    if state.get_key() in screens:
                        cls.screen_type = state

        @classmethod
        def get_details(cls):
            return cls.screen_type.value[1]

    class GameState:
        class GameType(enum.Enum):
            Campaign = "Playing Campaign"
            Versus = "Playing Versus game"
            Coop = "Playing Co-op game"
            Custom = "Playing Custom game"
            Replay = "Watching Replay"

        class Player:
            __translate = {
                "Terr": "terran",
                "Terran": "terran",
                "Prot": "protoss",
                "Protoss": "protoss",
                "Zerg": "zerg",
                "random": "random",
                "InfT": "pyrifier"
            }

            def __init__(self, id, name, type, race, result):
                self.id = id
                self.name = name
                self.type = type
                try:
                    self.race = self.__translate[race]
                except KeyError:
                    self.race = "random"
                self.result = result

            def __str__(self):
                return f"({self.race[0].upper()}) {self.name}"

        players: List[Player] = []
        game_type: GameType = GameType.Versus

        @classmethod
        def update(cls, players):
            cls.players = [cls.Player(**player) for player in players]

        @classmethod
        def get_state(cls):
            return cls.game_type.value

        @classmethod
        def get_details(cls):
            if cls.game_type in [cls.GameType.Versus, cls.GameType.Custom, cls.GameType.Replay]:
                if len(cls.players) == 2:
                    return f"{cls.players[0]} vs {cls.players[1]}"
                elif len(cls.players) == 1:
                    return f"{cls.players[0]}"
                # elif len(cls.players) == 4:
                #     return f"{cls.players[0]} and {cls.players[1]} vs {cls.players[2]} and {cls.players[3]} "
                else:
                    return f"{cls.players[0]} and {len(cls.players) - 1} others"
            elif cls.game_type == cls.GameType.Coop:
                return f"{cls.players[0]} and {cls.players[1]}"
            elif cls.game_type == cls.GameType.Campaign:
                return f"{cls.players[0]}"

    main_image = {
        "large_image": "main",
        "large_text": "StarCraft II"
    }
    small_images = {
        "zerg": {
            "small_image": "zerg",
            "small_text": "Zerg",
        },
        "protoss": {
            "small_image": "protoss",
            "small_text": "Protoss",
        },
        "terran": {
            "small_image": "terran",
            "small_text": "Terran",
        },
        "random": {
            "small_image": "random",
            "small_text": "Random",
        }
    }

    client_id = "1002138908953419776"
    sc2_url = "http://127.0.0.1:6119"
    default_player_name = ""
    running = True
    game_type_screens = {
        ScreenState.TypeLow.Campaign: GameState.GameType.Campaign,
        ScreenState.TypeLow.Multiplayer: GameState.GameType.Versus,
        ScreenState.TypeLow.Coop: GameState.GameType.Coop,
        ScreenState.TypeLow.Custom: GameState.GameType.Custom,
        ScreenState.TypeMid.Lobby: GameState.GameType.Custom,
        ScreenState.TypeLow.Replay: GameState.GameType.Replay
    }
    buttons = {"buttons": [{"label": "About presence", "url": "https://github.com/ReLLoMine/SC2DirscordRichPresence"}]}
    RPC: drp.Presence = None
    is_RPC_init = False
    time_period = 0.5

    @classmethod
    def get_ui_state(cls):
        try:
            screens = list(map(lambda x: x.split("/")[0], requests.get(cls.sc2_url + "/ui").json()["activeScreens"]))

            if screens:
                cls.ScreenState.update(screens)
                if cls.ScreenState.screen_type in cls.game_type_screens:
                    cls.GameState.game_type = cls.game_type_screens[cls.ScreenState.screen_type]
            else:
                cls.ScreenState.set_none()

        except (ConnectionError, JSONDecodeError):
            print("StarCraft II client is not found")
            cls.RPC.clear()
            time.sleep(5)

    @classmethod
    def get_game_state(cls):
        try:
            game = requests.get(cls.sc2_url + "/game").json()
            if cls.default_player_name:
                for i in range(len(game["players"])):
                    players = game["players"]
                    if players[i]["name"].lower() == cls.default_player_name.lower():
                        players[i], players[0] = players[0], players[i]
                        break

            cls.GameState.update(game["players"])
        except (ConnectionError, JSONDecodeError):
            print("StarCraft II client is not found")
            cls.RPC.clear()
            time.sleep(5)

    @classmethod
    def run(cls):
        cls.init_presence()
        while cls.running:
            cls.get_ui_state()
            cls.get_game_state()
            cls.update_presence()
            time.sleep(cls.time_period)

    @classmethod
    def init_presence(cls):
        try:
            cls.RPC = drp.Presence(cls.client_id)
            cls.RPC.connect()
            cls.is_RPC_init = True
        except DiscordNotFound:
            print("Discord client not found")
            time.sleep(5)

    @classmethod
    def try_init_presence(cls):
        while not cls.is_RPC_init:
            cls.init_presence()

    @classmethod
    def close_rpc(cls):
        cls.RPC.close()

    @classmethod
    def update_presence(cls):
        if cls.ScreenState.is_screen_changed():
            if cls.ScreenState.screen_type:
                print(cls.ScreenState.get_details())
                cls.RPC.update(**cls.main_image,
                               **cls.buttons,
                               details=cls.ScreenState.get_details(),
                               state="In Menu")
            else:
                print(cls.GameState.get_details())
                print(cls.GameState.get_state())
                cls.RPC.update(**cls.main_image,
                               **cls.buttons,
                               **cls.small_images[cls.GameState.players[0].race],
                               details=cls.GameState.get_details(),
                               state=cls.GameState.get_state(),
                               start=int(time.time()))
            cls.ScreenState.update_prev_screen()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        MyPresence.default_player_name = sys.argv[1]
    MyPresence.run()
