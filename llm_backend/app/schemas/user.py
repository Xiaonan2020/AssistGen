from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """
    用户响应模型类
    
    用于定义用户信息响应的数据结构，继承自UserBase基类
    包含用户的基本信息、状态和时间戳等字段
    """
    id: int
    status: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        """
        模型配置类
        
        配置Pydantic模型的行为参数
        """
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 