from pydantic import BaseModel
from datetime import date

class Cartridge(BaseModel):
    id:int
    value:int

class Cartridge_upload(BaseModel):
    id:int
    value:int
    serial:str
    adres:str