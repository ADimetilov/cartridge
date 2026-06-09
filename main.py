import psycopg2
import uvicorn
from datetime import date
from datetime import datetime,timedelta
from fastapi import FastAPI, status
import logging
from starlette.middleware.cors import CORSMiddleware
from classes import *
conn = psycopg2.connect(dbname="cartridge",user="postgres",password="123qweR%",host = "10.4.16.7",port="5432",keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5)

filename = "log_info_" + datetime.now().strftime("%d_%m_%Y_%H_%S")+".log"
logging.basicConfig(
    level=logging.INFO,
    filename=filename,
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
    force=True   
)
logging.info("Start")

cursor = conn.cursor()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"], 
)

def execute_query(query, params=None, fetch=False):
    global conn, cursor
    try:
        # Проверяем, не отвалилось ли соединение
        if conn.closed != 0:
            logging.warning("Соединение с БД закрыто, переподключаюсь...")
            conn = psycopg2.connect(dbname="cartridge", user="postgres", password="123qweR%", host="10.4.16.7", port="5432", keepalives=1, keepalives_idle=30)
            cursor = conn.cursor()
            
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            return cursor.fetchall()
        conn.commit()
    except psycopg2.OperationalError as e:
        logging.error(f"OperationalError: {e}. Переподключаюсь...")
        conn = psycopg2.connect(dbname="cartridge", user="postgres", password="123qweR%", host="10.4.16.7", port="5432", keepalives=1, keepalives_idle=30)
        cursor = conn.cursor()
        # Рекурсивно пробуем еще раз
        return execute_query(query, params, fetch)

@app.get("/status", tags=['deveop'])
def check_status():
    logging.info(f"Проверка доступности сервера!")
    return status.HTTP_200_OK

@app.get("/anal/get")
def get_analitics_get(id:int,date1:str,date2:str):
    try:
        logging.info(f"Начал получение аналитики по приёму")
        if (id == 112200):
            execute_query(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Value" = 1;''')
        else:
            execute_query(f'''BEGIN TRANSACTION; SELECT "Name" from public."cartridge" where "ID" = {id};''')
            model = str(cursor.fetchone()[0])
            execute_query(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Model" = '{model}' and "Value" = 1;''')
        list_analit = cursor.fetchall()
        score=0
        for analit in list_analit:
            if (datetime.strptime(date1,"%Y-%m-%d") <= datetime.strptime(str(analit[1]),"%Y-%m-%d")) and (datetime.strptime(date2,"%Y-%m-%d") >= datetime.strptime(str(analit[1]),"%Y-%m-%d")):
                score += analit[0]
        logging.info(f"Аналитика по получениям получена")
        return score
    except Exception as Error:
        execute_query("ROLLBACK;")
        logging.error(str(Error))
        return str(Error)

@app.get("/anal/post")
def get_analitics_post(id:int,date1:str,date2:str):
    try:
        logging.info(f"Начал получение аналитики по отправкам")
        if (id == 112200):
            execute_query(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Value" = -1;''')
        else:
            execute_query(f'''BEGIN TRANSACTION; SELECT "Name" from public."cartridge" where "ID" = {id};''')
            model = str(cursor.fetchone()[0])
            execute_query(f'''BEGIN TRANSACTION;
                       SELECT "Value","Date" from public."cartridge_log" where "Model" = '{model}' and "Value" = -1;''')
        list_analit = cursor.fetchall()
        score=0
        for analit in list_analit:
            if (datetime.strptime(date1,"%Y-%m-%d") <= datetime.strptime(str(analit[1]),"%Y-%m-%d")) and (datetime.strptime(date2,"%Y-%m-%d") >= datetime.strptime(str(analit[1]),"%Y-%m-%d")):
                score += 1
        logging.info(f"Аналитика по отправкам получена")
        return score
    except Exception as Error:
        execute_query("ROLLBACK;")
        logging.error(str(Error))
        return str(Error)


@app.post("/cart/add")
def add_cart(cartridge:Cartridge_add):
    try:
        logging.info(f"Начал добавление картриджа {cartridge.name}")
        execute_query(f'''BEGIN TRANSACTION; INSERT INTO public."cartridge" (\"Name\", \"Value\") VALUES(\'{cartridge.name}\',0); COMMIT;''')
        logging.info(f"Добавил картридж {cartridge.name}")
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        execute_query("ROLLBACK;")
        logging.error(str(Error))
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }

@app.put("/cart/edit")
def edit_cart(cartridge:Cartridge_edit):
    try:
        logging.info(f"Начал изменение картриджа {cartridge.id} на {cartridge.name}")
        execute_query(f'''BEGIN TRANSACTION;
                       UPDATE public."cartridge" 
                       Set "Name" = '{cartridge.name}' 
                       WHERE "ID" = {cartridge.id};
                       COMMIT;''')
        logging.info(f"Изменил наименование картриджа {cartridge.id} на {cartridge.name}")
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        logging.error(str(Error))
        execute_query("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }
    
@app.delete("/cart/del")
def del_cart(id:int):
    try:
        logging.info(f"Начал удаление картриджа {id}")
        execute_query(f'''BEGIN TRANSACTION; 
                       DELETE FROM public."cartridge_model" where "id_cart" = {id};
                       DELETE FROM public."cartridge" WHERE "ID" = {id};
                       COMMIT;
                       ''')
        logging.info(f"Картридж {id} удалён")
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        logging.error(str(Error))
        execute_query("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }

@app.post("/cart/change")
def add_value(cart:Cartridge):
    try:
        logging.info(f"Начал изменение картриджа {cart.id} на {cart.value}")
        execute_query(f'''BEGIN TRANSACTION; SELECT "Value" from public."cartridge" WHERE "ID" = {cart.id} ;''')
        value = int(cursor.fetchone()[0])
        value+=cart.value
        execute_query(f'''
                       BEGIN TRANSACTION;
                       UPDATE public."cartridge" SET 
                       "Value" = {value}
                       WHERE "ID" = {cart.id};
                       COMMIT;''')
        execute_query(f'''BEGIN TRANSACTION; SELECT "Name" from public."cartridge" where "ID" = {cart.id};''')
        model = str(cursor.fetchone()[0])
        execute_query(f'''BEGIN TRANSACTION;
                            INSERT INTO public."cartridge_log" (\"Model\",\"Date\",\"Value\")
                            VALUES ('{model}','{datetime.now().strftime("%Y-%m-%d")}',{int(cart.value)});
                            COMMIT;''')
        logging.info(f"Успешно измененил значение {cart.id}")
        return status.HTTP_202_ACCEPTED
    except Exception as Error:
        logging.error(str(Error))
        execute_query("ROLLBACK;")
        return{
            'error': str(Error),
            'status': status.HTTP_400_BAD_REQUEST
        }


@app.get("/cart/all")
def get_all_cartridge():
    try:
        logging.info("Начал загружать список картриджей!")
        execute_query(f'''BEGIN TRANSACTION;
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
        logging.info("Список наличия картриджей выгружен!")
        return cart_list
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return {
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.post("/upload/add")
def upload_add(cart:Cartridge_upload):
    try:
        logging.info(f"Начал добавлять картридж на выгрузку!")
        execute_query(f'''BEGIN TRANSACTION;
                            INSERT INTO public."catridge_exit" (\"model\",\"date\",\"adres\",\"serial\")
                            VALUES ('{cart.model}','{datetime.now().strftime("%Y-%m-%d")}','{cart.adres}','{cart.serial}');
                            COMMIT;''')
        logging.info("Добавил картридж на выгрузку!")
        return status.HTTP_202_ACCEPTED
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return {
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.get("/upload/all")
def get_all_upload():
    try:
        logging.info(f"Начал получать все картриджи на выгрузку!")
        datenow = date.today()
        while (datenow.isoweekday()!=2 and datenow.isoweekday()!=4):
            datenow = datenow + timedelta(days=1)
        execute_query(f'''BEGIN TRANSACTION;
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
            cart_json["date"]=str(datenow).strip()
            upload_list.append(cart_json)
        logging.info(f"Список картриджей выгружен!")
        return upload_list
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.delete("/upload/delid")
def del_for_id_upload(id:int):
    try:
        logging.info(f"Начал картридж по идентификатору {id} из выгрузки!")
        execute_query(f'''BEGIN TRANSACTION;
                       DELETE FROM PUBLIC."catridge_exit" WHERE "id" = {id}; 
                       COMMIT;''')
        logging.info(f"Картридж по идентификатору {id} из выгрузки удален!")
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }
    
@app.delete("/upload/del")
def del_all_upload():
    try:
        logging.info("Начал удалять все картриджи из выгрузки!")
        execute_query(f'''BEGIN TRANSACTION;
                       DELETE FROM PUBLIC."catridge_exit"; 
                       COMMIT;''')
        logging.info("Список выгрузки пуст!")
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            "error": str(error),
            "status":status.HTTP_400_BAD_REQUEST
        }

@app.post("/model/create")
def create_model(model:Model_New):
    try:
        logging.info("Начал добавлять модель!")
        execute_query(f'''BEGIN TRANSACTION;
                       INSERT INTO public."model" (\"name\")
                       VALUES ('{model.name}');
                       COMMIT;''')
        logging.info("Модель добавлена!")
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.get("/model/list")
def get_all_model():
    try:
        logging.info("Начал получать все модели по картриджу!")
        execute_query(f'''BEGIN TRANSACTION;
                       SELECT * FROM public."model" ORDER BY "id" ASC;''')
        model_base = cursor.fetchall()
        model_list = []
        for model in model_base:
            model_json = {
                "id":int,
                "name":str,
                "model_id":int
            }
            model_json["id"] = model[0]
            model_json["name"] = str(model[1]).strip()
            model_json["model_id"] = model[0]
            model_list.append(model_json)
        logging.info("Модели получены!")
        return model_list
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }

@app.get("/model/get")
def get_model_for_cart(id:int):
    try:
        logging.info("Начал получать модели по картриджу!")
        execute_query(f'''BEGIN TRANSACTION;
                       SELECT id, id_model, (Select "name" from public."model" where "id" = "id_model") FROM public."cartridge_model" WHERE "id_cart" ={id} ORDER BY "id" ASC;''')
        model_base = cursor.fetchall()
        model_list = []
        for model in model_base:
            model_json = {
                "id":int,
                "model_id":int,
                "name":str
            }
            model_json["id"] = model[0]
            model_json["model_id"] = model[1]
            model_json["name"] = str(model[2]).strip()
            model_list.append(model_json)
        logging.info("Модели по картриджу получены!")
        return model_list
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }


@app.put("/model/edit")
def edit_model(model:Model_Edit):
    try:
        execute_query(f'''BEGIN TRANSACTION;
                       UPDATE public."model" set \"name\" = '{model.name}'
                       WHERE "id" = {model.id};
                       COMMIT;''')
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.delete("/model/delete")
def delete_model(id:int):
    try:
        execute_query(f'''BEGIN TRANSACTION;
                       DELETE FROM public."cartridge_model" where "id_model" = {id};
                       DELETE FROM public."model" where "id" = {id};
                       COMMIT;''')
        return status.HTTP_201_CREATED
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.post("/model/link")
def link_model_cart(data:Model_link):
    try:
        logging.info("Начал связывать модели и картриджи!")
        for model_id in data.id_model:
            execute_query(f'''BEGIN TRANSACTION;
                        insert into public."cartridge_model" (\"id_model\",\"id_cart\")
                        VALUES({int(model_id)},{data.id_cart});
                        COMMIT;''')
        logging.info("Связал модели и картриджи!")
        return status.HTTP_201_CREATED
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.delete("/model/unlink")
def link_model_cart(id:int):
    try:
        logging.info("Начал убирать связку!")
        execute_query(f'''BEGIN TRANSACTION;
                       delete from public."cartridge_model"
                       where "id_cart" = {id};
                       COMMIT;''')
        logging.info("Убрал связку!")
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.post("/requirement/add")
def add_requirement(requirement:Requirement):
    try:
        logging.info("Начал добавлять потребность!")
        execute_query(f'''BEGIN TRANSACTION;
                       Insert into public."requirement" (\"id_model\",\"score\")
                       VALUES({requirement.id_model},{requirement.score});
                       COMMIT;''')
        logging.info("Потребность добавлена!")
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.get("/requirement/all")
def get_all_requirement():
    try:
        logging.info("Получение всех потребностей начал!")
        execute_query(f'''BEGIN TRANSACTION;
                       SELECT "id", (Select "name" from public."model" where "id" = "id_model") as name, "score"
                       from public."requirement"
                       ORDER BY "id" ASC;''')
        list_requirement = cursor.fetchall()
        list_json_requirement = []
        for requirement in list_requirement:
            json_requirement = {
                "id":int,
                "name":str,
                "score":int
            }
            json_requirement["id"]=int(requirement[0])
            json_requirement["name"] = str(requirement[1]).strip()
            json_requirement["score"] = int(requirement[2])
            list_json_requirement.append(json_requirement)
        logging.info("Потребности получил!")
        return list_json_requirement
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }
    
@app.put("/requirement/edit")
def edit_requirement_for_id(requirement:Requirement_edit):
    try:
        logging.info("Изменение потребности начал!")
        execute_query(f'''UPDATE public."requirement" SET \"score\" = {requirement.score}
                       WHERE "id" = {requirement.id};
                       COMMIT;''')
        logging.info("Потребность изменена!")
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }

@app.delete("/requirement/delete")
def delete_requirement_for_id(id:int):
    try:
        logging.info("Удаление потребность начал!")
        execute_query(f'''BEGIN TRANSACTION;
                       DELETE FROM PUBLIC."requirement" WHERE "id" = {id};
                       COMMIT;''')
        logging.info("Потребность удалена!")
        return status.HTTP_200_OK
    except Exception as error:
        logging.error(str(error))
        execute_query("ROLLBACK;")
        return{
            'status': status.HTTP_400_BAD_REQUEST,
            'error_text':str(error)
        }

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=4433)