#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     November 10, 2021
#
# Description:  MultiBrim
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 10/11/2021 first prototype
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re #To perform the search
from enum import Enum
from collections import namedtuple
from typing import List, Tuple

__version__ = '1.0'

Point2D = namedtuple('Point2D', 'x y')

class Section(Enum):
    """Enum for section type."""

    NOTHING = 0
    SKIRT = 1
    BRIM = 2
    INNER_WALL = 3
    OUTER_WALL = 4
    INFILL = 5
    SKIN = 6
    SKIN2 = 7

def is_begin_layer_line(line: str) -> bool:
    """Check if current line is the start of a layer section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a layer section
    """
    return line.startswith(";LAYER:")

def is_begin_skirt_line(line: str) -> bool:
    """Check if current line is the start of a SKIRT section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a SKIRT section
    """
    return line.startswith(";TYPE:SKIRT")

def is_begin_type_line(line: str) -> bool:
    """Check if current line is the start of a type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a type section
    """
    return line.startswith(";TYPE")

def is_begin_mesh_line(line: str) -> bool:
    """Check if current line is the start of a new MESH.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a new MESH
    """
    return line.startswith(";MESH:")

    
def is_z_line(line: str) -> bool:
    """Check if current line is a Z line

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a Z line segment
    """
    return "G0" in line and "Z" in line and not "E" in line

def getXY(currentLine: str) -> Point2D:
    """Create a ``Point2D`` object from a gcode line.

    Args:
        currentLine (str): gcode line

    Raises:
        SyntaxError: when the regular expressions cannot find the relevant coordinates in the gcode

    Returns:
        Point2D: the parsed coordinates
    """
    searchX = re.search(r"X(\d*\.?\d*)", currentLine)
    searchY = re.search(r"Y(\d*\.?\d*)", currentLine)
    if searchX and searchY:
        elementX = searchX.group(1)
        elementY = searchY.group(1)
    else:
        raise SyntaxError('Gcode file parsing error for line {currentLine}')

    return Point2D(float(elementX), float(elementY))
    
class MultiBrim(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "MultiBrim",
            "key": "MultiBrim",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "multiply":
                {
                    "label": "Brim multiply",
                    "description": "Number of Brim to Multiply",
                    "type": "int",
                    "default_value": 2,
                    "minimum_value": "1",
                    "maximum_value_warning": "3",
                    "maximum_value": "5"
                }                 
            }
        }"""

    def execute(self, data):

        BrimMultiply = int(self.getSettingValueByKey("multiply")) 

        idl=0
        lines_brim =[]
        startline=''
        nb_line=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:                  
               
                if line.startswith(";LAYER_COUNT:"):
                    # Logger.log("w", "found LAYER_COUNT %s", line[13:])
                    layercount=int(line[13:])                    
               
                if is_begin_layer_line(line):
                    line_index = lines.index(line)    
                    # Logger.log('d', 'layer_lines : {}'.format(line))
                    currentlayer=int(line[7:])
                    # Logger.log('d', 'currentlayer : {:d}'.format(currentlayer))
                    if line.startswith(";LAYER:0"):
                        idl=1
                    elif currentlayer <= BrimMultiply :
                        Logger.log('d', 'Insert here : {:d}'.format(currentlayer))
                        line_index = lines.index(line)
                        lines.insert(line_index + 1, "G92 E0")
                        lines.insert(line_index + 2, startline)

 
                if idl == 2 and is_begin_type_line(line):
                    idl == 0
                    
                if idl == 2 and is_begin_mesh_line(line) :
                    idl = 0
                    Logger.log('d', 'mesh_lines : {}'.format(line))
                    Logger.log('d', 'nb_line    : {:d}'.format(nb_line))
                    # for aline in lines_brim:
                    #     Logger.log('d', 'brim_lines : {}'.format(aline))
                        
                if idl == 2 :
                    lines_brim.append(line)
                    nb_line+=1
 
                if idl == 1 and is_begin_skirt_line(line):
                    idl=2
                    line_index = lines.index(line)
                    startline=lines(line_index)
                    lines_brim =[]
                    startlayer=currentlayer
                    lines_brim.append(line)
                    nb_line=1
                    # Logger.log("w", "Z Height %f", currentz) 
                
                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data
