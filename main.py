import requests
from bs4 import BeautifulSoup
import json

# Enables or disables debug messages
DEBUG:bool = False
    
####################################################################################################################################
# Auxiliary functions
def parse_nfse_params(raw_nfse_params):
    '''Gets a string with the parameters of the NFSe, and returns a dict object containing the params'''
    params = {}
    for param in raw_nfse_params:
        kv = param.split('=', 1) # splits the string in the equals sign, stoping on the first occurrence
        params[kv[0]] = kv[1]
    
    return params

def nfse_to_json(webpage):
    '''Gets the NFSe and parse it to a json object'''
    # table_data = [[cell.text for cell in row("td")]
    #                      for row in BeautifulSoup(webpage, features='lxml')("tr")]

    table_data = [[cell.text for cell in row("td")]
                        for row in BeautifulSoup(webpage, features='lxml')("table")]                     
    obj = array_to_json(table_data[9])
    return(json.dumps(obj, ensure_ascii=False))

def array_to_json(array):
    dict = {}
    for element in array[2:]: # starts in the second element, since the first two are not relevant
        kv = element.split(':', 1) # splits the string in the : sign, stoping on the first occurrence
        dict[kv[0]] = kv[1]

    return dict

def log(message: str):
    if (DEBUG):
        print(f'{message}\n')

# Auxiliary functions
####################################################################################################################################

def get_nota_fiscal(params, session):
    _url = 'https://nfse.campinas.sp.gov.br/NotaFiscal/notaFiscal.php'
    _response = session.get(_url, params=params)
    return nfse_to_json(_response.text)

def main():
    log("Fetching NFSe info...")
    # Data to fetch. This could be given as an input from API URL
    data = {
        'rPrest':'10.831.692/0001-73', # CNPJ do Prestador de Serviços
        'rNumNota':'1886', # Número da NFSe
        'rInsMun':'1628534', # Inscrição Municipal
        'rCodigoVerificacao':'8eb34d2809793d1d8aabdcb4fb7488d9bd2cfe58', # Código de Verificação da NFSe
        'rCodCid':'6291', # ? 
        'btnVerificar':'Verificar' # ?
    }

    # New Session
    session = requests.Session()
    # Main URL, to fetch information from the NFSe
    verificar_autenticidade_url = 'https://nfse.campinas.sp.gov.br/NotaFiscal/action/notaFiscal/verificarAutenticidade.php'
    response = session.post(verificar_autenticidade_url, data=data)

    # Auxiliary string information. Should get the text that is in between the two strings below
    start = response.text.find('notaFiscal.php?') + len('notaFiscal.php?')
    end = response.text.find("','NFSE'")

    _nfse_params_string = response.text[start:end] # nfse params as string
    nfse_params = parse_nfse_params(_nfse_params_string.split('&')) # splits the string on the & sign, and converts to dict

    log(f'Raw NFSe information: {_nfse_params_string}')
    log(f'NFSe information object: {nfse_params}')

    nota_fiscal_json = get_nota_fiscal(nfse_params, session)
    print(nota_fiscal_json)

if __name__ == '__main__':
    main()