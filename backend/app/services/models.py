from datetime import datetime
from typing import Optional
from .. import app_factory
 
db = app_factory.main_controller.db
 

# Define the UserInfoEntry model
class UserInfo(db.Model):
    user_id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str = db.Column(db.String(100), nullable=False)
    hashed_password: str = db.Column(db.String(200), nullable=False)
    points: int = db.Column(db.Integer, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "points": self.points,
            "created_on": self.created_on
        }
 
    def __repr__(self) -> str:
        return f"<UserInfo(user_id={self.user_id}, username={self.username}, hashed_password={self.hashed_password}, created_on={self.created_on}, points={self.points})>"

