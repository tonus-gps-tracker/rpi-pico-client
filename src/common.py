def lpad(data: str, width: int, char: str) -> str:
	return char * (width - len(data)) + data