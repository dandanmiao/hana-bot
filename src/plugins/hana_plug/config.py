from pydantic import  BaseModel, field_validator

class Config(BaseModel):
    """Plugin Config Here"""
    loliconurl: str = 'https://api.lolicon.app/setu/v2?r18=0&size=regular'
    loliconurl_size: str = 'regular'
    lolicon_r18: bool = False
    temp_img_path: str = "D:/ideaProject/bot/img"

    # @field_validator("weather_command_priority")
    # @classmethod
    # def check_priority(cls, v: int) -> int:
    #     if v >= 1:
    #         return v
    #     raise ValueError("weather command priority must greater than 1")