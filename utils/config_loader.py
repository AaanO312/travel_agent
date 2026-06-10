import yaml
import os


def load_config():
    path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{name}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


settings = load_config()
