def init() -> None: ...

class _COLORS:
	BLACK: str
	RED: str
	GREEN: str
	YELLOW: str
	BLUE: str
	MAGENTA: str
	CYAN: str
	WHITE: str
	RESET: str

class Style:
	DIM: str
	NORMAL: str
	BRIGHT: str
	RESET_ALL: str

Fore: _COLORS
Back: _COLORS
