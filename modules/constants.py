def get_ctype_elems(ctype):
    return [
        v for k, v in ctype.__dict__.items()
        if '__' not in k and 'object at' not in k
    ]

class ItemCategory:
    Vahicle = "vehicles"
    PrivateLesson = "private_lessons"
    Computer = "computers"
    Phone = "phones"