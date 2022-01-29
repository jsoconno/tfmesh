import re
from tfmesh.core import *

color_list = ["HEADER", "OK_BLUE", "OK_CYAN", "OK_GREEN", "WARNING", "FAIL", "END", "BOLD", "UNDERLINE"]

pattern = r'\033\[[0-9]*m'

for color in color_list:
    string = colors(color)
    if re.match(pattern, string):
        print('yes')
    else:
        print("no")
