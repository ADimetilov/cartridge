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

class Cartridge_add(BaseModel):
    name:str

class Cartridge_edit(BaseModel):
    id:int
    name:str

class Anal_config(BaseModel):
    id:int
    date1:str
    date2:str

