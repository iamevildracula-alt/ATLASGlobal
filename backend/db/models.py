from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .database import Base
from ..models.schemas import EnergyType, ScenarioType
from ..models.infrastructure import NodeType, NodeStatus, LinkStatus
import datetime

class GridNodeModel(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    type = Column(String) # generator, load, storage, substation
    capacity_mw = Column(Float)
    location_x = Column(Float)
    location_y = Column(Float)
    location_z = Column(Float, default=0.0)
    status = Column(String, default="online")
    
    # Physics/Engineering Fields
    voltage_level_kv = Column(Float, default=220.0)
    health_index = Column(Float, default=1.0) # 0.0 to 1.0 (1.0 = New)
    pd_activity = Column(Float, default=0.0) # pC (PicoCoulombs)
    
    timeseries = relationship("TimeSeriesDataModel", back_populates="node")

class GridLinkModel(Base):
    __tablename__ = "links"

    id = Column(String, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("nodes.id"))
    target_id = Column(String, ForeignKey("nodes.id"))
    capacity_mw = Column(Float)
    current_load_mw = Column(Float)
    resistance = Column(Float, default=0.1)
    reactance = Column(Float, default=0.5)
    length_km = Column(Float, default=10.0)
    fault_position = Column(Float, nullable=True)
    status = Column(String, default="active")
    
    # Engineering Fields (Impedance/Ratings as per roadmap)
    resistance_ohms = Column(Float, default=0.1)
    reactance_ohms = Column(Float, default=0.5)
    max_thermal_rating_mva = Column(Float, default=500.0) # Deprecated? Or keep as absolute max
    static_rating_mva = Column(Float, default=500.0) # Nameplate
    dynamic_rating_mva = Column(Float, default=500.0) # Real-time DLR
    limiting_factor = Column(String, default="Static") # e.g. "Sag", "Temp", "Static"
    
    health_index = Column(Float, default=1.0)
    pd_activity = Column(Float, default=0.0)

class TimeSeriesDataModel(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("nodes.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    demand_mw = Column(Float)
    supply_mw = Column(Float)
    carbon_intensity = Column(Float) # kgCO2/MWh
    reliability_score = Column(Float)
    
    node = relationship("GridNodeModel", back_populates="timeseries")

class PolicyModel(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    max_cost_per_mwh = Column(Float, default=100.0)
    max_carbon_per_mwh = Column(Float, default=0.5)
    min_reliability_score = Column(Float, default=0.99)
    risk_tolerance = Column(String, default="neutral")
    is_active = Column(Integer, default=1) # 1 for active
class NuclearStatsModel(Base):
    __tablename__ = "nuclear_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("nodes.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    core_temperature = Column(Float)
    coolant_pressure = Column(Float)
    control_rod_insertion = Column(Float)
    reactivity_index = Column(Float)
    thermal_margin = Column(Float)
    
    node = relationship("GridNodeModel")
