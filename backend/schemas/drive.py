from pydantic import BaseModel


class DriveFile(BaseModel):
    id: str
    name: str
    type: str


class TestDriveResponse(BaseModel):
    status: str
    message: str
    first_10_files: list[DriveFile] | None = None
