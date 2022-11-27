"""
This script runs the ToDoWebProject application using a development server.
"""

from os import environ
from ToDoWebProject import app

if __name__ == '__main__':
    app.run('localhost', '5000')
