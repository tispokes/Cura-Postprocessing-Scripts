# Cura PostProcessingPlugin
# Author:   Amanda de Castilho pour la partie Layer
# Author:   Mathias Lyngklip Kjeldgaard pour la partie Temps restant
# Author:   Laurent Lalliard
# Date:     Janvier 02 2020
# Modified: Janvier 05 2020  Option afficher LayerId

# Description:  This plugin shows custom messages about your print on the Status bar...
#               Please look at the option
#               - LayerId: Utilise le Layer ID codé dans le fichier origine

from ..Script import Script
from UM.Application import Application

class DisplayPrintInfosOnLCD(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Display Print Infos On LCD",
            "key": "DisplayPrintInfosOnLCD",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "LayerId":
                {
                    "label": "Utilisation Layer Id G-Code",
                    "description": "Utilise le Layer Id codé dans le fichier G-Code. A utiliser pour impression pièce à pièce",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""
    
    def execute(self, data):
        max_layer = 0
        total_time = 0
        part = 0
        total_time_string = ""
        current_time_string = ""
        lcd_text = "M117 ("
        Id = 1
        for layer in data:
            display_text = lcd_text + str(Id) + "/" 
            layer_index = data.index(layer)
            lines = layer.split("\n")
            for line in lines:
                if line.startswith(";LAYER_COUNT:"):
                    max_layer = line.split(":")[1]   # Recuperation Nb Layer Maxi
                elif line.startswith(";LAYER:"):
                    line_index = lines.index(line)
                    if part > 1:
                        display_text = display_text + max_layer + ") " + current_time_string + " P" + str(part)
                    else:
                        display_text = display_text + max_layer + ") " + current_time_string
                        
                    lines.insert(line_index + 1, display_text)      # Insert du code M117 apres les layers
                    if self.getSettingValueByKey("LayerId"):
                        Id = int(line.split(":")[1])                # Utilise le Layer dans G-Code ;LAYER:1
                        if Id == 0:
                            part += 1                               # Incrémente le numero de pièce       
                        Id += 1
                    else:
                        Id += 1                                     # Incrémente le numero de Layer (sans utiliser celui du Gcode)
                if line.startswith(";TIME:"):
                    line_index = lines.index(line)
                    total_time = int(line.split(":")[1])
                    m, s = divmod(total_time, 60)    # Decomposition en
                    h, m = divmod(m, 60)             # heures, minutes et secondes
                    total_time_string = "{:d}h{:d}m{:d}s".format(int(h), int(m), int(s))
                    current_time_string = total_time_string
                    display_text = lcd_text + total_time_string + ")"
                    lines.insert(line_index + 1, display_text)
                elif line.startswith(";TIME_ELAPSED:"):
                    line_index = lines.index(line)
                    current_time = float(line.split(":")[1])
                    time_left = total_time - current_time   # Calcul du temps restant
                    m1, s1 = divmod(time_left, 60)          # Decomposition en
                    h1, m1 = divmod(m1, 60)                 # heures, minutes et secondes
                    current_time_string = "{:d}h{:d}m{:d}s".format(int(h1), int(m1), int(s1))
                    
            final_lines = "\n".join(lines)
            data[layer_index] = final_lines
            
        return data
