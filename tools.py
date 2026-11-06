from langchain_core.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Умножает два целых числа и возвращает результат."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Складывает два целых числа и возвращает результат."""
    return a + b

if __name__ == "__main__":
    result = multiply.invoke({"a": 125, "b": 37})
    print(result)