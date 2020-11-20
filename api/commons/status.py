import enum

class Status(enum.Enum):
    RUNNING = 'running'
    TRAINING = 'training'
    CONCLUDED = 'concluded'
    ERROR = 'error'
