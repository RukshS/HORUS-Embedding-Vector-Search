from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.tracking_modules import Module, ModuleQuery
from app.odm.dal import modules_collection
import app.models.atlas_vector_search as vs
import pprint

router = APIRouter()


# Request module recommendations
@router.post("/recommend", response_model=List[Module])
async def get_suggested_modules(module_query: ModuleQuery):
        
    return vs.get_query_results(module_query.query)