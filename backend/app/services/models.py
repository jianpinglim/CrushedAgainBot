from datetime import datetime
from typing import Optional
from .. import app_factory
 
db = app_factory.main_controller.db
 

# Define the UserInfoEntry model
class UserInfo(db.Model):
    user_id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_telegram_id: str = db.Column(db.String(10), nullable=False)
    username: str = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_telegram_id": self.user_telegram_id,
            "username": self.username,
        }
 
    def __repr__(self) -> str:
        return f"<UserInfo(user_id={self.user_id}, user_telegram_id={self.user_telegram_id}, username={self.username})>"

# Define the CrushEntry model
class Crush(db.Model):
    crush_id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_telegram_id: str = db.Column(db.String(10), nullable=False)
    crush_user_id: str = db.Column(db.String(10), nullable=False)
    
    def to_dict(self):
        return {
            "crush_id": self.crush_id,
            "user_telegram_id": self.user_telegram_id,
            "crush_user_id": self.crush_user_id,
        }
 
    def __repr__(self) -> str:
        return f"<Crush(crush_id={self.crush_id}, user_telegram_id={self.user_telegram_id}, crush_user_id={self.crush_user_id})>"

