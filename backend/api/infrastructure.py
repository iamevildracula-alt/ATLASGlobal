from fastapi import APIRouter
from ..models.infrastructure import GridTopology, GridNode, GridLink, NodeType, NodeStatus, LinkStatus

router = APIRouter()

# Mock Data
MOCK_NODES = [
    GridNode(id="n1", name="Solar Farm Alpha", type=NodeType.GENERATOR, capacity_mw=150, location_x=10, location_y=20, status=NodeStatus.ONLINE),
    GridNode(id="n2", name="Wind Park Beta", type=NodeType.GENERATOR, capacity_mw=200, location_x=80, location_y=15, status=NodeStatus.ONLINE),
    GridNode(id="n3", name="Thermal Plant Gamma", type=NodeType.GENERATOR, capacity_mw=500, location_x=20, location_y=80, status=NodeStatus.ONLINE),
    GridNode(id="n4", name="Main City Substation", type=NodeType.LOAD, capacity_mw=0, location_x=50, location_y=50, status=NodeStatus.ONLINE),
    GridNode(id="n5", name="Industrial Zone", type=NodeType.LOAD, capacity_mw=0, location_x=70, location_y=70, status=NodeStatus.ONLINE),
    GridNode(id="n6", name="Grid Battery Storage", type=NodeType.STORAGE, capacity_mw=100, location_x=40, location_y=40, status=NodeStatus.ONLINE),
]

MOCK_LINKS = [
    GridLink(id="l1", source_id="n1", target_id="n4", capacity_mw=200, current_load_mw=120),
    GridLink(id="l2", source_id="n2", target_id="n4", capacity_mw=250, current_load_mw=180),
    GridLink(id="l3", source_id="n3", target_id="n4", capacity_mw=600, current_load_mw=400),
    GridLink(id="l4", source_id="n4", target_id="n5", capacity_mw=400, current_load_mw=300),
    GridLink(id="l5", source_id="n6", target_id="n4", capacity_mw=100, current_load_mw=0),
]

@router.get("/topology", response_model=GridTopology)
async def get_topology():
    return GridTopology(nodes=MOCK_NODES, links=MOCK_LINKS)
