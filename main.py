import psycopg2
import uvicorn
from datetime import datetime
from fastapi import FastAPI, status
from starlette.middleware.cors import CORSMiddleware
from classes import *
conn = psycopg2.connect(dbname="cartridge",user="postgres",password="123qweR%",host = "localhost",port="5432")

cursor = conn.cursor()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или укажите конкретный домен: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],      # разрешаем все методы (GET, POST и др.)
    allow_headers=["*"],     # разрешаем все заголовки
)

@app.get("/status", tags=['deveop'])
def check_status():
    return status.HTTP_200_OK

@app.get("/anal/get")
def get_analitics_get(id:int,date1:str,date2:str):
    try:
        if (id == 112200):
            cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Value" = 1;''')
        else:
            cursor.execute(f'''BEGIN TRANSACTION; SELECT "Name" from public."cartridge" where "ID" = {id};''')
            model = str(cursor.fetchone()[0])
            cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Model" = '{model}' and "Value" = 1;''')
        list_analit = cursor.fetchall()
        score=0
        for analit in list_analit:
            if (datetime.strptime(date1,"%Y-%m-%d") <= datetime.strptime(str(analit[1]),"%Y-%m-%d")) and (datetime.strptime(date2,"%Y-%m-%d") >= datetime.strptime(str(analit[1]),"%Y-%m-%d")):
                score += analit[0]
        return score
    except Exception as Error:
        cursor.execute("ROLLBACK;")
        return str(Error)

@app.get("/anal/post")
def get_analitics_post(id:int,date1:str,date2:str):
    try:
        if (id == 112200):
            cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Value" = -1;''')
        else:
            cursor.execute(f'''BEGIN TRANSACTION; SELECT "Name" from public."cartridge" where "ID" = {id};''')
            model = str(cursor.fetchone()[0])
            cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Model" = '{model}' and "Value" = -1;''')
        list_analit = cursor.fetchall()
        score=0
        for analit in list_analit:
            if (datetime.strptime(date1,"%Y-%m-%d") <= datetime.strptime(str(analit[1]),"%Y-%m-%d")) and (datetime.strptime(date2,"%Y-%m-%d") >= datetime.strptime(str(analit[1]),"%Y-%m-%d")):
                score += 1
        return score
    except Exception as Error:
        cursor.execute("ROLLBACK;")
        return str(Error)


@app.post("/cart/add")
def add_cart(cartridge:Cartridge_add):
    try:
        cursor.execute(f'''BEGIN TRANSACTION; INSERT INTO public."cartridge" (\"Name\", \"Value\") VALUES(\'{cartridge.name}\',0); COMMIT;''')
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        cursor.execute("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }

@app.put("/cart/edit")
def edit_cart(cartridge:Cartridge_edit):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       UPDATE public."cartridge" 
                       Set "Name" = '{cartridge.name}' 
                       WHERE "ID" = {cartridge.id};
                       COMMIT;''')
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        cursor.execute("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }
    
@app.delete("/cart/del")
def del_cart(id:int):
    try:
        cursor.execute(f'''BEGIN TRANSACTION; DELETE FROM public."cartridge" WHERE "ID" = {id};COMMIT;''')
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        cursor.execute("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }

@app.post("/cart/change")
def add_value(cart:Cartridge):
    try:
        cursor.execute(f'''BEGIN TRANSACTION; SELECT "Value" from public."cartridge" WHERE "ID" = {cart.id} ;''')
        value = int(cursor.fetchone()[0])
        value+=cart.value
        cursor.execute(f'''
                       BEGIN TRANSACTION;
                       UPDATE public."cartridge" SET 
                       "Value" = {value}
                       WHERE "ID" = {cart.id};
                       COMMIT;''')
        cursor.execute(f'''BEGIN TRANSACTION; SELECT "Name" from public."cartridge" where "ID" = {cart.id};''')
        model = str(cursor.fetchone()[0])
        cursor.execute(f'''BEGIN TRANSACTION;
                            INSERT INTO public."cartridge_log" (\"Model\",\"Date\",\"Value\")
                            VALUES ('{model}','{datetime.now().strftime("%Y-%m-%d")}',{int(cart.value)});
                            COMMIT;''')
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        cursor.execute("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }


@app.get("/cart/all")
def get_all_cartridge():
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT * FROM public."cartridge" ORDER BY "ID" ASC;''')
        cart_base = cursor.fetchall()
        cart_list = []
        for cart in cart_base:
            cart_json = {
                "id":int,
                "name":str,
                "value":int
            }
            cart_json["id"] = cart[0]
            cart_json["name"] = str(cart[1]).strip()
            cart_json["value"] = int(cart[2])
            cart_list.append(cart_json)
        return cart_list
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return {
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.post("/upload/add")
def upload_add(cart:Cartridge_upload):
    try:
        if (cart.dram == 1):
            cart.model = cart.model+" (Драм.)"
        cursor.execute(f'''BEGIN TRANSACTION;
                            INSERT INTO public."catridge_exit" (\"model\",\"date\",\"adres\",\"serial\")
                            VALUES ('{cart.model}','{datetime.now().strftime("%Y-%m-%d")}','{cart.adres}','{cart.serial}');
                            COMMIT;''')
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return {
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.get("/upload/all")
def get_all_upload():
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT * from public."catridge_exit" ORDER BY id DESC;''')
        upload_base = cursor.fetchall()
        upload_list = []
        for cart in upload_base:
            cart_json = {
                "id":int,
                "model":str,
                "serial":str,
                "adres":str,
                "date":str
           }
            cart_json["id"]=int(cart[0])
            cart_json["model"]=str(cart[1]).strip()
            cart_json["serial"]=str(cart[2]).strip()
            cart_json["adres"]=str(cart[3]).strip()
            cart_json["date"]=str(cart[4]).strip()
            upload_list.append(cart_json)
        return upload_list
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.delete("/upload/delid")
def del_for_id_upload(id:int):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       DELETE FROM PUBLIC."catridge_exit" WHERE "id" = {id}; 
                       COMMIT;''')
        return status.HTTP_200_OK
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.delete("/upload/del")
def del_all_upload():
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       DELETE FROM PUBLIC."catridge_exit"; 
                       COMMIT;''')
        return status.HTTP_200_OK
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }

@app.post("/model/create")
def create_model(model:Model_New):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       INSERT INTO public."model" (\"name\")
                       VALUES ('{model.name}');
                       COMMIT;''')
        return status.HTTP_200_OK
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.get("/model/list")
def get_all_model():
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT * FROM public."model" ORDER BY "id" ASC;''')
        model_base = cursor.fetchall()
        model_list = []
        for model in model_base:
            model_json = {
                "id":int,
                "name":str,
            }
            model_json["id"] = model[0]
            model_json["name"] = str(model[1]).strip()
            model_list.append(model_json)
        return model_list
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }

@app.get("/model/get")
def get_model_for_cart(id:int):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       SELECT id, (Select "name" from public."model" where "id" = "id_model") FROM public."cartridge_model" WHERE "id_cart" ={id} ORDER BY "id" ASC;''')
        model_base = cursor.fetchall()
        model_list = []
        for model in model_base:
            model_json = {
                "id":int,
                "name":str,
            }
            model_json["id"] = model[0]
            model_json["name"] = str(model[1]).strip()
            model_list.append(model_json)
        return model_list
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }


@app.put("/model/edit")
def edit_model(model:Model_Edit):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       UPDATE public."model" set \"name\" = '{model.name}'
                       WHERE "id" = {model.id};
                       COMMIT;''')
        return status.HTTP_200_OK
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.delete("/model/delete")
def delete_model(id:int):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       DELETE * FROM public."model" where "id" = {id};
                       COMMIT;''')
        return status.HTTP_201_CREATED
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.post("/model/link")
def link_model_cart(data:Model_link):
    try:
        for model_id in data.id_model:
            cursor.execute(f'''BEGIN TRANSACTION;
                        insert into public."cartridge_model" (\"id_model\",\"id_cart\")
                        VALUES({int(model_id)},{data.id_cart});
                        COMMIT;''')
        return status.HTTP_201_CREATED
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.delete("/model/unlink")
def link_model_cart(id:int):
    try:
        cursor.execute(f'''BEGIN TRANSACTION;
                       delete from public."cartridge_model"
                       where "id_cart" = {id};
                       COMMIT;''')
        return status.HTTP_200_OK
    except Exception as error:
        cursor.execute("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=4433)