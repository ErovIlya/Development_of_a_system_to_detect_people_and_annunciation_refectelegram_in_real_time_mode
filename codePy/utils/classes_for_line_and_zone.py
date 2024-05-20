class Point:
    """
    Класс Point - точка для Line
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_list(self) -> list:
        """
        Перевод класса в список
        """
        return [self.x, self.y]

    def to_tuple(self) -> tuple[int, int]:
        """
        Перевод класса в кортеж
        """
        return self.x, self.y


_list_points = {'center': 100, 'left_center': 101, 'right_center': 102, 'up_center': 103, 'bottom_center': 104}


class WhichPointObjectBeTracked:
    """
    Класс служит для определения "особой" точки, по которой будет происходить детектирование
    """
    @staticmethod
    def center() -> int:
        """
        "Особая" точка - центр прямоугольника
        """
        return _list_points['center']

    @staticmethod
    def left_center() -> int:
        """
        "Особая" точка - центр левого ребра прямоугольника
        """
        return _list_points['left_center']

    @staticmethod
    def right_center() -> int:
        """
        "Особая" точка - центр правого ребра прямоугольника
        """
        return _list_points['right_center']

    @staticmethod
    def up_center() -> int:
        """
        "Особая" точка - центр верхнего ребра прямоугольника
        """
        return _list_points['up_center']

    @staticmethod
    def bottom_center() -> int:
        """
        "Особая" точка - центр нижнего ребра прямоугольника
        """
        return _list_points['bottom_center']
