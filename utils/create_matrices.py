def createArray(type, arrName, arr, n_elements):
    stri = f'{type} {arrName}[{n_elements}] = {{'
    for i, n in enumerate(arr):
        stri = stri + ' ' + str(n) + ', '
    stri = stri + '};\n'
    stri = stri.replace(', }', '}')
    return stri

def createMatrix(type, matName, mat, dim0, dim1):
    #stri = f'{type} {matName}[{mat.shape[0]}][{mat.shape[1]}] = {{ '
    stri = f'{type} {matName}[{dim0}][{dim1}] = {{ '
    for i, row in enumerate(mat):
        if i != 0:
            stri = stri + '\t\t\t'
        stri = stri + '{ '
        for j, val in enumerate(row):
            if type=='int':
                val = val.astype(int)
            stri = stri + str(val)
            if j < (row.shape[0] - 1): # changed by Fb
                stri = stri + ', '
        stri = stri + ' }'
        if i < (mat.shape[0] - 1):
            stri = stri + ',\n'
    stri = stri + ' };\n'
    return stri

def createMatrix2(type, matName, mat, dim0, dim1):
    #stri = f'{type} {matName}[{mat.shape[0]}][{mat.shape[2]}] = {{ '
    stri = f'{type} {matName}[{dim0}][{dim1}] = {{ '
    for i, row in enumerate(mat):
        if i != 0:
            stri = stri + '\t\t\t'
        stri = stri + '{ '
        for j, val in enumerate(row[0]):
            if type=='int':
                val = int(val)
            stri = stri + str(val)
            if j < (row.size - 1):
                stri = stri + ', '
        stri = stri + ' }'
        if i < (mat.shape[0] - 1):
            stri = stri + ',\n'
    stri = stri + ' };\n'
    return stri