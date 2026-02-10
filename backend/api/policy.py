from fastapi import APIRouter
from ..models.policy import PolicyConstraints

router = APIRouter()

# In-memory mock storage
current_policy = PolicyConstraints()

@router.get("/", response_model=PolicyConstraints)
async def get_policy():
    return current_policy

@router.post("/", response_model=PolicyConstraints)
async def update_policy(policy: PolicyConstraints):
    global current_policy
    current_policy = policy
    return current_policy
