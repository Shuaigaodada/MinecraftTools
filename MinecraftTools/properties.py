import os
import json

PROPERTIES_PATH = \
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "cache", "server.properties"
    )
class Properties:
    def __init__(self) -> None:
        self.allow_flight: bool = False
        self.allow_nether: bool = True
        self.broadcast_console_to_ops: bool = True
        self.broadcast_rcon_to_ops: bool = True
        self.difficulty: str = "easy" # peaceful, easy, normal, hard
        self.enable_command_block: bool = False
        self.enable_jmx_monitoring: bool = False
        self.enable_query: bool = False
        self.enable_rcon: bool = False
        self.enable_status: bool = True
        self.enforce_secure_profile: bool = True
        self.enforce_whitelist: bool = False
        self.entity_broadcast_range_percentage: int = 100
        self.force_gamemode: bool = False
        self.function_permission_level: int = 2
        self.gamemode: int = "survival" # 0: survival, 1: creative, 2: adventure, 3: spectator
        self.generate_structures: bool = True
        self.generator_settings: dict = {}
        self.hardcore: bool = False
        self.hide_online_players: bool = False
        self.initial_disabled_packs = None
        self.initial_enabled_packs = "vanilla"
        self.level_name: str = "world"
        self.level_seed: str = None
        self.level_type: str = "minecraft\:normal"
        self.max_chained_neighbor_updates: int = 1000000
        self.max_players: int = 20
        self.max_tick_time = 60000
        self.max_world_size = 29999984
        self.motd: str = "A Minecraft Server"
        self.network_compression_threshold: int = 256
        self.online_mode: bool = True
        self.op_permission_level: int = 4
        self.player_idle_timeout: int = 0
        self.prevent_proxy_connections: bool = False
        self.pvp: bool = True
        self.query_port: int = 25565
        self.rate_limit: int = 0
        self.rcon_password: str = None
        self.rcon_port: int = 25575
        self.require_resource_pack: bool = False
        self.resource_pack: str = None
        self.resource_pack_prompt: str = None
        self.resource_pack_sha1: str = None
        self.server_ip: str = ""
        self.server_port: int = 25565
        self.simulation_distance: int = 10
        self.spawn_animals: bool = True
        self.spawn_monsters: bool = True
        self.spawn_npcs: bool = True
        self.spawn_protection: int = 16
        self.sync_chunk_writes: bool = True
        self.text_filtering_config: str = None
        self.use_native_transport: bool = True
        self.view_distance: int = 10
        self.white_list: bool = False
    
    def save(self) -> None:
        global PROPERTIES_PATH
        config: str = ""
        for name in dir(self):
            if name.startswith("__"):
                continue
            attr, val = name, getattr(self, name)
            if callable(val):
                continue
            
            if attr not in ("query_port","rcon_port","rcon_password"):
                attr = attr.replace("_", "-")
            else:
                attr = attr.replace("_", ".")
            
            if type(val) == bool:
                val = "true" if val else "false"
            elif type(val) == dict:
                val = json.dumps(val)
            elif val is None:
                val = ""
            config += f"{attr}={val}\n"

        config = config[:-1]
        with open(PROPERTIES_PATH, "w") as fp:
            fp.write(config)
    
if __name__ == "__main__":
    p = Properties()
    p.save()

    with open(PROPERTIES_PATH, "r") as fp:
        copys = fp.read()
    
    PATH = \
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "prefile", "server.properties"
        )
    with open(PATH, "r") as fp:
        origin = fp.read()
    print(copys == origin)
    