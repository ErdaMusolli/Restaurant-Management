from pydantic import BaseModel

class AssignManager(BaseModel):
    manager_id: int       
    restaurant_id: int    
