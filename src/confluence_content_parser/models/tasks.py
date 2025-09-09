from pydantic import BaseModel, Field


class DecisionItem(BaseModel):
    local_id: str = Field("", alias="local-id")
    state: str
    content: str
    model_config = {"populate_by_name": True}


class DecisionList(BaseModel):
    local_id: str = Field(..., alias="local-id")
    items: list[DecisionItem] = Field(default_factory=list)
    model_config = {"populate_by_name": True}


class TaskItem(BaseModel):
    local_id: str = Field(..., alias="ac:local-id")
    task_id: str = Field(..., alias="ac:task-id")
    completed: bool = False
    content: str = ""
    model_config = {"populate_by_name": True}


class TaskList(BaseModel):
    local_id: str = Field(..., alias="ac:local-id")
    items: list[TaskItem] = Field(default_factory=list)
    model_config = {"populate_by_name": True}


class TaskElement(BaseModel):
    task_id: str = ""
    task_uuid: str = ""
    status: str = "incomplete"
    body: str = ""


class TaskListContainer(BaseModel):
    tasks: list[TaskElement] = Field(default_factory=list)
