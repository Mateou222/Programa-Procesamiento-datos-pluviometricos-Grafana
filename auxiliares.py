

def color_grafica(multi):
    #Funcion que devuelve un color distinto en hexadecimal para cada equipo
    if multi == 0:
        color = "#000000"
    elif multi == 1:
        color = "#0000ff"
    elif multi == 2:
        color = "#00ff00"
    elif multi == 3:
        color = "#2DCB5F"
    elif multi == 4:
        color = "#CF9909"
    elif multi == 5:
        color = "#19C6E9"
    elif multi == 6:
        color = "#A2D9CE"
    elif multi == 7:
        color = "#E91968"
    elif multi == 8:
        color = "#C8AFB9"
    elif multi == 9:
        color = "#E919BD"
    elif multi == 10:
        color = "#007124"
    elif multi == 11:
        color = "#D0A6FF"
    elif multi == 12:
        color = "#936200"
    elif multi == 13:
        color = "#FFA07A"
    elif multi == 14:
        color = "#BDC3C7"
    elif multi == 15:
        color = "#F9E79F" 
    elif multi == 16:
        color = "#E8DAEF"
    elif multi ==17:
        color = "#580065"
    else:
        color = "#ff0000"
    return color

def nombre_abreviado(Nombre):
    #Funcion que pasas el nombre del equipo y devuelve el nombre abreviado
    if Nombre == "Areas_Verdes":
        return "AV"
    elif Nombre == "Lucas_Piriz":
        return "LP"
    elif Nombre == "Museo_Blanes":
        return "MB"
    elif Nombre == "PAGRO":
        return "PA"
    elif Nombre == "CCZ7":
        return "CCZ7"
    elif Nombre == "Casavalle":
        return "PCV"
    elif Nombre == "Giraldez":
        return "PGZ"
    elif Nombre == "La_Paloma":
        return "PLP"
    elif Nombre == "Evaristo_Ciganda":
        return "EC"
    elif Nombre == "Jardín_348":
        return "J348"
    elif Nombre == "Lixiviados":
        return "PL"
    elif Nombre == "Anexo":
        return "AN"
    elif Nombre == "Punta_Carretas":
        return "PC"
    elif Nombre == "CCZ9":
        return "CCZ9"
    elif Nombre == "Colón":
        return "CN"
    elif Nombre == "CCZ18":
        return "CCZ18"
    elif Nombre == "Caif":
        return "CA"
    elif Nombre == "Miguelete":
        return "MI"
    else:
        return "INUMET"