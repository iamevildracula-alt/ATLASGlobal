from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class NodeType(str, Enum):
    GENERATOR = "generator"
    LOAD = "load"
    STORAGE = "storage"
    SUBSTATION = "substation"
    NUCLEAR = "nuclear"

class LinkStatus(str, Enum):
    ACTIVE = "active"
    FAILED = "failed"
    CONGESTED = "congested"

class NodeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class GridNode(BaseModel):
    id: str
    name: str
    type: NodeType
    capacity_mw: float
    location_x: float  # 0-100 relative position
    location_y: float  # 0-100 relative position
    location_z: float = 0.0 # elevation
    status: NodeStatus = NodeStatus.ONLINE
    health_index: float = 1.0
    pd_activity: float = 0.0

class GridLink(BaseModel):
    id: str
    source_id: str
    target_id: str
    capacity_mw: float
    current_load_mw: float
    resistance: float = 0.1
    reactance: float = 0.5
    length_km: float = 10.0
    fault_position: Optional[float] = None # 0.0 to 1.0 along the link
    status: LinkStatus = LinkStatus.ACTIVE
    health_index: float = 1.0
    pd_activity: float = 0.0
    static_rating_mva: float = 500.0
    dynamic_rating_mva: float = 500.0
    limiting_factor: str = "Static"

class GridTopology(BaseModel):
    nodes: List[GridNode]
    links: List[GridLink]
