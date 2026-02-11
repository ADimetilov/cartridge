from pydantic import BaseModel
from datetime import date

class Cartridge(BaseModel):
    id:int
    value:int

class Cartridge_upload(BaseModel):
    model:str
    value:int
    serial:str
    adres:str
    dram:int

class Cartridge_add(BaseModel):
    name:str

class Cartridge_edit(BaseModel):
    id:int
    name:str

class Anal_config(BaseModel):
    id:int
    date1:str
    date2:str

class Model_New(BaseModel):
    name:str

class Model_Edit(BaseModel):
    id:int
    name:str

class Model_link(BaseModel):
    id_model:list
    id_cart:int
