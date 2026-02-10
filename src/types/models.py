from pydantic import BaseModel, Field


class SetTokenInput(BaseModel):
    token: str = Field(description="GitHub Personal Access Token")


class CreateRepoInput(BaseModel):
    name: str = Field(description="Repository name")
    description: str = Field(default="", description="Repository description")
    private: bool = Field(default=True, description="Whether the repo should be private")


class DeleteRepoInput(BaseModel):
    name: str = Field(description="Repository name to delete")
