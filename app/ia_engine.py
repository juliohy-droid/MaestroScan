def clasificar_plaga(nombre):
    categorias = {'Drosophila suzukii': 'Primaria / Alerta SAG', 'Agrotis ipsilon': 'Primaria'}
    return categorias.get(nombre, 'Asociado')