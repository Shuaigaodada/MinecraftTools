import os
import json

class Properties:
    def __init__(self) -> None:
        self.allow_flight: bool = False
        """是否允许飞行"""
        
        self.allow_nether: bool = True
        """是否允许进入地狱"""
        
        self.broadcast_console_to_ops: bool = True
        """是否将控制台消息广播给OP"""
        
        self.broadcast_rcon_to_ops: bool = True
        """是否将RCON消息广播给OP"""
        
        self.difficulty: str = "easy" # peaceful, easy, normal, hard
        """游戏难度: peaceful, easy, normal, hard"""
        
        self.enable_command_block: bool = False
        """是否启用命令方块"""
        
        self.enable_jmx_monitoring: bool = False
        """是否启用JMX监控"""
        
        self.enable_query: bool = False
        """是否启用查询"""
        
        self.enable_rcon: bool = False
        """是否启用RCON"""
        
        self.enable_status: bool = True
        """是否启用状态"""
        
        self.enforce_secure_profile: bool = True
        """是否强制安全配置文件"""
        
        self.enforce_whitelist: bool = False
        """是否强制白名单"""
        
        self.entity_broadcast_range_percentage: int = 100
        """实体广播范围百分比"""
        
        self.force_gamemode: bool = False
        """是否强制游戏模式"""
        
        self.function_permission_level: int = 2
        """功能权限等级"""
        
        self.gamemode: int = 0 # 0: survival, 1: creative, 2: adventure, 3: spectator
        """游戏模式: 0: 生存, 1: 创造, 2: 冒险, 3: 观察"""
        
        self.generate_structures: bool = True
        """是否生成结构"""
        
        self.generator_settings: dict = {}
        """结构生成器设置"""
        
        self.hardcore: bool = False
        """是否开启极限模式"""
        
        self.hide_online_players: bool = False
        """是否隐藏在线玩家"""
        
        self.initial_disabled_packs = None
        """初始禁用的包"""
        
        self.initial_enabled_packs = "vanilla"
        """初始启用的包"""
        
        self.level_name: str = "world"
        """世界名称"""
        
        self.level_seed: str = None
        """世界种子"""
        
        self.level_type: str = "minecraft\\:normal"
        """世界类型"""
        
        self.max_chained_neighbor_updates: int = 1000000
        """最大链式邻居更新"""
        
        self.max_players: int = 20
        """最大玩家数"""
        
        self.max_tick_time = 60000
        ""
        
        self.max_world_size = 29999984
        """最大世界大小"""
        
        self.motd: str = "A Minecraft Server"
        """服务器介绍"""
        
        self.network_compression_threshold: int = 256
        """网络压缩阈值"""
        
        self.online_mode: bool = True
        """是否在线模式(是否验证是正版)"""
        
        self.op_permission_level: int = 4
        """OP权限等级"""
        
        self.player_idle_timeout: int = 0
        """玩家空闲超时(-1为不限制)"""
        
        self.prevent_proxy_connections: bool = False
        """是否阻止代理连接"""
        
        self.pvp: bool = True
        """是否开启PVP"""
        
        self.query_port: int = 25565
        """查询端口"""
        
        self.rate_limit: int = 0
        """速率限制"""
        
        self.rcon_password: str = None
        """RCON密码"""
        
        self.rcon_port: int = 25575
        """RCON端口"""
        
        self.require_resource_pack: bool = False
        """是否必须加载资源包"""
        
        self.resource_pack: str = None
        """资源包文件"""
        
        self.resource_pack_prompt: str = None
        """资源包提示"""
        
        self.resource_pack_sha1: str = None
        """资源包SHA1校验值"""
        
        self.server_ip: str = ""
        """服务器IP地址"""
        
        self.server_port: int = 25565
        """服务器端口"""
        
        self.simulation_distance: int = 10
        """模拟距离"""
        
        self.spawn_animals: bool = True
        """是否生成动物"""
        
        self.spawn_monsters: bool = True
        """是否生成怪物"""
        
        self.spawn_npcs: bool = True
        """是否生成NPC"""
        
        self.spawn_protection: int = 16
        """出生点保护范围"""
        
        self.sync_chunk_writes: bool = True
        """是否同步区块写入"""
        
        self.text_filtering_config: str = None
        """文本过滤配置"""
        
        self.use_native_transport: bool = True
        """是否使用本地传输"""
        
        self.view_distance: int = 10
        """视距"""
        
        self.white_list: bool = False
        """是否启用白名单"""
    
    def save(self, path: str) -> None:
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
        with open(path, "w") as fp:
            fp.write(config)
