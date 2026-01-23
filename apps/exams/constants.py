from enum import Enum


class ExamStatus(str, Enum):
    CLOSED = "closed"
    ACTIVATED = "activated"
