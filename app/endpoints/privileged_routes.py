from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.tracking_modules import Module
from app.odm.dal import modules_collection

router = APIRouter()

# CREATE module
@router.post("/modules", response_model=Module, status_code=status.HTTP_201_CREATED)
async def create_module(module: Module):
    module_dict = module.model_dump(by_alias=True)
    result = await modules_collection.insert_one(module_dict)
    created_module = await modules_collection.find_one({"_id": result.inserted_id})
    
    if created_module:

        return created_module
    
    raise HTTPException(status_code=500, detail="Failed to create module")

# READ all modules
@router.get("/modules", response_model=List[Module])
async def get_all_modules():
    modules = []
    async for module in modules_collection.find():
        if module:
            modules.append(Module(**module))

    if modules:

        return modules
    
    raise HTTPException(status_code=404, detail="Module not found")

    

# READ specific module
@router.get("/modules/{module_id}", response_model=Module)
async def get_module(module_id: str):
    module = await modules_collection.find_one({"module_id": module_id})
    
    if module:

        return module
    
    raise HTTPException(status_code=404, detail="Module not found")




# UPDATE module
@router.put("/modules", response_model=Module)
async def update_module(module_id: str, module: Module):
    
    # Check if module exists
    if not await modules_collection.find_one({"module_id": module_id}):
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Update the module
    updated_data = module.model_dump(by_alias=True, exclude_unset=True)
    result = await modules_collection.update_one(
        {"module_id": module_id},
        {"$set": updated_data}
    )
    
    # Check if update was successful
    if result.modified_count != 0:
        # Return the updated module
        updated_module = await modules_collection.find_one({"module_id": module_id})

        if updated_module:

            return updated_module
        
        raise HTTPException(status_code=404, detail="Module not found")
    
    raise HTTPException(status_code=400, detail="Module update failed")
    


# DELETE module
@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(module_id: str):
    
    # Check if module exists
    if not await modules_collection.find_one({"module_id": module_id}):
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Delete the module
    await modules_collection.delete_one({"module_id": module_id})

    # Double-check the module is gone (optional but thorough)
    if await modules_collection.find_one({"module_id": module_id}):
        raise HTTPException(
            status_code=500,
            detail="Failed to delete module. It still exists in the database."
        )

    return None






