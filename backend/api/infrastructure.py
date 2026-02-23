from fastapi import APIRouter, Depends
from ..models.infrastructure import GridTopology, GridNode, GridLink, NodeType, NodeStatus, LinkStatus
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.repository import GridRepository

router = APIRouter()

@router.get("/topology", response_model=GridTopology)
async def get_topology(db: Session = Depends(get_db)):
    repo = GridRepository(db)
    data = repo.get_topology()
    
    # Map DB models to Pydantic schemas
    nodes = [
        GridNode(
            id=n.id, 
            name=n.name, 
            type=n.type, 
            capacity_mw=n.capacity_mw, 
            location_x=n.location_x, 
            location_y=n.location_y, 
            status=n.status
        ) for n in data["nodes"]
    ]
    
    links = [
        GridLink(
            id=l.id, 
            source_id=l.source_id, 
            target_id=l.target_id, 
            capacity_mw=l.capacity_mw, 
            current_load_mw=l.current_load_mw, 
            status=l.status
        ) for l in data["links"]
    ]
    
    return GridTopology(nodes=nodes, links=links)
