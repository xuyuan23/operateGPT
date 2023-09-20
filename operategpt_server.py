import os
from datetime import datetime
import time

import uuid
import uvicorn
from fastapi import FastAPI, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, asc, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from starlette.middleware.cors import CORSMiddleware

from operate import generate_md_file
from operategpt.api.Result import Result

from dotenv import load_dotenv

from operategpt.prompt.lang import Language

load_dotenv(verbose=True, override=True)

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWD = os.getenv("DB_PASSWD", "123456")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "operategpt")


engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

Session = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()
origins = ["*"]

# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

router = APIRouter()


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    prompt = Column(String(65535))
    status = Column(String(10), default="init")
    gmt_create = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    gmt_modified = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    result = Column(String(65535))
    uuid = Column(String(36))
    lang = Column(String(36))


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(255))
    email = Column(String(255))


@router.post("/operate/task/create")
def create_task(user_id: int, prompt: str, lang: str = "en"):
    try:
        if lang not in Language.get_all_langs():
            return {"success": False, "msg": f"create task failed: lang {lang} is not supported!"}
        task_uuid = generate_uuid()
        session = Session()
        task = Task(user_id=user_id, prompt=prompt, status="init", uuid=task_uuid, gmt_create=datetime.now(), gmt_modified=datetime.now(), lang=lang)
        session.add(task)
        session.commit()
        session.close()
        return {"success": True, "msg": f"create task success, please remember taskid for query result! uuid= {task_uuid}"}
    except Exception as e:
        return {"success": False, "msg": f"create task failed: {str(e)}"}


@router.get("/operate/task/by-uuid")
def list_tasks(task_uuid: str):
    session = Session()
    task = session.query(Task).filter(Task.uuid == task_uuid).first()
    init_task_count = session.query(func.count(Task.id)).filter(Task.id < task.id, Task.status == 'init').scalar()
    session.close()
    task_dict = {
        "id": task.id,
        "user_id": task.user_id,
        "prompt": task.prompt,
        "status": task.status,
        "gmt_create": str(task.gmt_create),
        "gmt_modified": str(task.gmt_modified),
        "lang": str(task.lang),
        "result": task.result,
        "queue_count": init_task_count
    }
    return Result.success(task_dict)


@router.get("/operate/task/list")
def list_tasks(user_id: int):
    session = Session()
    tasks = session.query(Task).filter(Task.user_id == user_id).all()
    session.close()
    task_list = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "prompt": task.prompt,
            "status": task.status,
            "gmt_create": str(task.gmt_create),
            "gmt_modified": str(task.gmt_modified),
            "lang": str(task.lang),
            "result": task.result,
        }
        task_list.append(task_dict)
    return Result.success(task_list)


def process_tasks():
    while True:
        try:
            session = Session()
            task = (
                session.query(Task)
                .filter(Task.status == "init")
                .order_by(asc(Task.id))
                .first()
            )
            if task:
                task.status = "running"
                task.gmt_modified = datetime.now()
                session.commit()
                try:
                    result = execute_task(task)
                    task.status = "success"
                    task.gmt_modified = datetime.now()
                    task.result = result
                except Exception as e:
                    print("Error executing task:", str(e))
                    task.status = "failed"
                    task.gmt_modified = datetime.now()
                    task.result = str(e)[:65530]
            else:
                print("No tasks found.")
            session.commit()
            session.close()
        except Exception as ex:
            print(f"周期任务执行失败，{str(ex)}")
        time.sleep(1)


def execute_task(task):
    print(f"execute task(id={task.id}), prompt={task.prompt}, lang={task.lang}")
    return generate_md_file(task.prompt, task.lang)


def start_task_processing():
    import threading
    thread = threading.Thread(target=process_tasks)
    thread.start()


def generate_uuid():
    return uuid.uuid4().hex


app.include_router(router, prefix="/api")


if __name__ == "__main__":
    start_task_processing()
    uvicorn.run(app, host="0.0.0.0", port=8671, log_level="info")
