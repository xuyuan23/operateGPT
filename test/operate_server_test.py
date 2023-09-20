import datetime

from operategpt_server import execute_task, Task


def exec_task_test():
    task = Task(
        id=1001,
        user_id=1001,
        prompt="国庆节青岛旅游三天三晚详细攻略",
        status="running",
        gmt_create=datetime.datetime,
        gmt_modified=datetime.datetime,
        lang="zh",
        result="",
    )
    ret = execute_task(task)
    return ret


result = exec_task_test()
print(f"result={result}")
