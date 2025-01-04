import datetime
import unicodedata
import re

class GetDate:

    def __init__(self):
        self.dias_da_semana = {
            'segunda': 0,
            'terca': 1,
            'quarta': 2,
            'quinta': 3,
            'sexta': 4,
            'sabado': 5,
            'domingo': 6
        }

    def remover_acentos(self,texto):
        # Normaliza a string e remove os acentos
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def proximo_dia(self,entrada):
        # Normaliza a entrada: remove acentos, converte para minúsculas, remove "feira", espaços e hífens
        entrada_normalizada = self.remover_acentos(entrada.lower()).replace("feira", "").replace(" ", "").replace("-", "").strip()

        # Obtém a data atual
        hoje = datetime.datetime.now()

        # Se a entrada for "hoje", retorna o dia de hoje
        if entrada_normalizada == "hoje":
            return hoje.day

        # Se a entrada for "amanha", retorna o dia de amanhã
        if entrada_normalizada == "amanha":
            return (hoje + datetime.timedelta(days=1)).day

        # Se a entrada for "depois de amanha", retorna o dia de depois de amanhã
        if entrada_normalizada == "depoisdeamanha":
            return (hoje + datetime.timedelta(days=2)).day

        # Se for um dia da semana, calcula o próximo dia correspondente
        if entrada_normalizada in self.dias_da_semana:
            dia_atual = hoje.weekday()
            dia_desejado = self.dias_da_semana[entrada_normalizada]
            
            # Se o dia desejado for o mesmo de hoje, retorna o dia do mês atual
            if dia_desejado == dia_atual:
                return hoje.day
            
            # Calcula a diferença de dias até o próximo dia desejado
            if dia_desejado < dia_atual:
                dias_ate_o_proximo = 7 - (dia_atual - dia_desejado)
            else:
                dias_ate_o_proximo = dia_desejado - dia_atual
            
            # Adiciona os dias ao dia de hoje
            proximo_dia = hoje + datetime.timedelta(days=dias_ate_o_proximo)
            
            # Retorna o dia do mês do próximo dia desejado
            return proximo_dia.day
        
        return "não sei"
    

    def extrair_hora(self,input_string):
    # Usando expressão regular para cobrir os casos: "17 h", "17 horas", "às 17", "às 8h"
        match = re.search(r'(?:às\s*)?(\d+)\s*(h|horas)?\b', input_string)

        if match:
            # Retorna o número como inteiro
            return int(match.group(1))
        else:
            # Retorna None caso não encontre um padrão válido
            return None

