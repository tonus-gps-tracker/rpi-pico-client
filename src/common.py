from libs.Dotenv import Dotenv

env = Dotenv()

def lpad(data: str, width: int, char: str) -> str:
	return char * (width - len(data)) + data

def debug() -> bool:
	return bool(int(env.get('DEBUG')))