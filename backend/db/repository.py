from sqlalchemy.orm import Session
from .models import GridNodeModel, GridLinkModel, TimeSeriesDataModel, PolicyModel
from ..models.schemas import InfrastructureState, EnergySource, EnergyType, EnergyDemand
from ..models.infrastructure import GridNode, GridLink, NodeType, NodeStatus, LinkStatus
from typing import List, Optional
import datetime

class GridRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_infrastructure_state(self) -> InfrastructureState:
        # Fetch all nodes from DB
        node_models = self.db.query(GridNodeModel).all()
        
        sources = []
        storage_capacity = 0.0
        current_storage = 0.0
        
        for node in node_models:
            # Convert DB model to EnergySource schema
            # This mapping needs to be careful as schemas.py is simplified
            if node.type in ["generator", "solar", "wind", "nuclear"]:
                # Mapping node type to EnergyType enum
                e_type = EnergyType.GRID # fallback
                if node.type == "solar": e_type = EnergyType.SOLAR
                elif node.type == "wind": e_type = EnergyType.WIND
                elif node.type == "nuclear": e_type = EnergyType.NUCLEAR
                elif node.type == "generator": e_type = EnergyType.GRID # thermal/gas as grid for now
                
                sources.append(EnergySource(
                    type=e_type,
                    capacity=node.capacity_mw,
                    cost_per_mwh=50.0, # This should come from DB or real-time feed
                    carbon_intensity=0.2, # This should come from DB
                    availability=1.0
                ))
            elif node.type == "storage":
                storage_capacity += node.capacity_mw
                current_storage += node.capacity_mw * 0.8 # Mock 80% charge
        
        # Pull threshold from active policy
        policy = self.get_active_policy()
        
        # Fetch all links
        link_models = self.db.query(GridLinkModel).all()
        
        # Build GridNode and GridLink lists
        grid_nodes = [GridNode(
            id=n.id, name=n.name, type=NodeType(n.type),
            capacity_mw=n.capacity_mw, location_x=n.location_x, location_y=n.location_y,
            location_z=n.location_z, status=NodeStatus(n.status),
            health_index=n.health_index, pd_activity=n.pd_activity
        ) for n in node_models]

        grid_links = [GridLink(
            id=l.id, source_id=l.source_id, target_id=l.target_id,
            capacity_mw=l.capacity_mw, current_load_mw=l.current_load_mw,
            resistance=l.resistance, reactance=l.reactance, length_km=l.length_km,
            fault_position=l.fault_position, status=LinkStatus(l.status),
            health_index=l.health_index, pd_activity=l.pd_activity,
            static_rating_mva=l.static_rating_mva, dynamic_rating_mva=l.dynamic_rating_mva,
            limiting_factor=l.limiting_factor
        ) for l in link_models]

        return InfrastructureState(
            sources=sources,
            storage_capacity_mwh=storage_capacity,
            current_storage_mwh=current_storage,
            reliability_threshold=policy.min_reliability_score if policy else 0.99,
            nodes=grid_nodes,
            links=grid_links
        )

    def get_active_policy(self) -> Optional[PolicyModel]:
        return self.db.query(PolicyModel).filter(PolicyModel.is_active == 1).first()

    def add_telemetry(self, node_id: str, demand: float, supply: float, carbon: float, reliability: float):
        telemetry = TimeSeriesDataModel(
            node_id=node_id,
            timestamp=datetime.datetime.utcnow(),
            demand_mw=demand,
            supply_mw=supply,
            carbon_intensity=carbon,
            reliability_score=reliability
        )
        self.db.add(telemetry)
        self.db.commit()

    def get_history(self, limit: int = 24) -> List[TimeSeriesDataModel]:
        return self.db.query(TimeSeriesDataModel).order_by(TimeSeriesDataModel.timestamp.desc()).limit(limit).all()

    def update_node_telem(self, node_id: str, value: float, data_type: str):
        """Updates real-time telemetry for a node."""
        node = self.db.query(GridNodeModel).filter(GridNodeModel.id == node_id).first()
        if node:
            # logic to update node model
            self.db.commit()

    def update_link_telem(self, link_id: str, load_mw: float, status: Optional[str] = None):
        """Updates real-time telemetry for a link."""
        link = self.db.query(GridLinkModel).filter(GridLinkModel.id == link_id).first()
        if link:
            link.current_load_mw = load_mw
            if status:
                link.status = status
            self.db.commit()

    def get_topology(self) -> dict:
        nodes = self.db.query(GridNodeModel).all()
        links = self.db.query(GridLinkModel).all()
        return {
            "nodes": [GridNode(
                id=n.id, 
                name=n.name, 
                type=n.type, 
                capacity_mw=n.capacity_mw, 
                location_x=n.location_x, 
                location_y=n.location_y,
                location_z=n.location_z,
                status=n.status
            ) for n in nodes],
            "links": [GridLink(
                id=l.id, 
                source_id=l.source_id, 
                target_id=l.target_id, 
                capacity_mw=l.capacity_mw, 
                current_load_mw=l.current_load_mw,
                resistance=l.resistance,
                reactance=l.reactance,
                length_km=l.length_km,
                fault_position=l.fault_position,
                status=l.status
            ) for l in links]
        }
