from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class NodeType(str, Enum):
    GENERATOR = "generator"
    LOAD = "load"
    STORAGE = "storage"
    SUBSTATION = "substation"

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
    status: NodeStatus = NodeStatus.ONLINE

class GridLink(BaseModel):
    id: str
    source_id: str
    target_id: str
    capacity_mw: float
    current_load_mw: float
    status: LinkStatus = LinkStatus.ACTIVE

class GridTopology(BaseModel):
    nodes: List[GridNode]
    links: List[GridLink]
