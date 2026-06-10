from langchain_community.chat_models.tongyi import ChatTongyi
from utils.config_loader import settings

_model = None


def get_model() -> ChatTongyi:
    global _model
    if _model is None:
        _model = ChatTongyi(
            model=settings["model_name"],
            max_tokens=settings.get("max_tokens", 4096),
            temperature=settings.get("temperature", 0.5),
        )
    return _model
