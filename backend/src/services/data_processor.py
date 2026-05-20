import os
import pandas as pd
from typing import Optional
import sqlite3
from utils.functios import ocds


# Classe responsável por processar os dados dos certificados, incluindo leitura do CSV, filtragem por ano e mês, e contagem de certificados por órgão certificador
class DataProcessor:
    def __init__(self, root_dir: str, docs_dir: str, db_path: str):        

        self.root_dir = root_dir
        self.docs_dir = docs_dir
        self.db_path = db_path

        # Dicionário para mapear os nomes dos meses em português para seus respectivos códigos numéricos
        self.lista_mes = {
            'janeiro': '1',
            'fevereiro': '2',
            'março':'3',
            'abril': '4',
            'maio': '5',
            'junho': '6',
            'julho': '7',
            'agosto': '8',
            'setembro': '9',
            'outubro': '10',
            'novembro': '11',
            'dezembro': '12',
        }

        # Dicionário para mapear os nomes dos órgãos certificadores para nomes mais amigáveis ou padronizados
        self.dict_name = {
            'UL-BR': 'UL',
            'OCP': 'OCPTELLI',
            'ABCP-OCD':'ABCP',
            'OCD':'BRICS',
            'MT':'MASTER',
            'ELD':'ELDORADO',
            'QC':'QCCERT',
            'TÜV': 'TUV',
            'BRC': 'BRACERT',
            'BRA': 'BR APPROVAL',
            'TELECOM': 'INTERTEK',
            'IBR': 'IBR TECH',
            'TEL': 'ACTA',
            '7C': 'SEVEN COMPLIANCE'
        }

    # Método para processar os dados do CSV, filtrar por ano e salvar os dados processados no banco de dados SQLite
    def process_and_save_to_db(self, ano:int):
        # Caminho do arquivo CSV extraído
        csv_file_path = self.docs_dir / "Produtos_Homologados_Anatel.csv"

        # Verifica se o arquivo CSV existe
        if not os.path.exists(csv_file_path):
            return {
                "status": "Fail",
                "mensagem": f"O arquivo '{csv_file_path}' não foi encontrado.",
                "status_code": 404
            }
        try:

            # Lê o CSV usando Pandas para garantir a leitura correta dos dados, especialmente com encoding e separadores
            df = pd.read_csv(
                    csv_file_path, 
                    sep=";", 
                    encoding='utf-8',
                    usecols=[
                        "Data do Certificado de Conformidade Técnica",
                        "Certificado de Conformidade Técnica",
                        "Número de Homologação"
                    ]
                )
            
            # Converte a coluna para datetime (evita erros de texto)
            col_data = "Data do Certificado de Conformidade Técnica"
            df[col_data] = pd.to_datetime(df[col_data], dayfirst=True, errors='coerce')

            # Filtra o DataFrame para o ano específico, garantindo que apenas os dados do ano
            #  desejado sejam processados
            df_ano = df[df[col_data].dt.year == ano].copy()

            if df_ano.empty:
                return {
                    "status": "Fail",
                    "mensagem": f"Nenhum dado encontrado para o ano {ano}.",
                    "status_code": 404
                }

            # Adiciona colunas de ano e mês para facilitar a filtragem posterior por mês
            df_ano['ano_filtro'] = df_ano[col_data].dt.year
            df_ano['mes_filtro'] = df_ano[col_data].dt.month

            # Renomeia as colunas para nomes mais amigáveis e consistentes com o banco de dados
            df_ano.columns = [
                'numero_homologacao', 
                'certificado_tecnico',
                'data_certificado',
                'ano_filtro', 
                'mes_filtro'
            ]

            conn = sqlite3.connect(self.db_path) # Conecta ao banco de dados SQLite usando o caminho fornecido

            try:
                conn.execute(f"DELETE FROM certificados WHERE ano_filtro = {ano}")
                conn.commit()
            except:
                pass # Se a tabela não existir ainda, ignora o erro do DELETE

            # Salva o DataFrame na tabela 'certificados'. append garante que anos diferentes se acumulem lá
            df_ano.to_sql('certificados', conn, if_exists='append', index=False)
            conn.close()

            # Retorna uma resposta de sucesso indicando que os dados do ano foram processados e salvos com sucesso no banco de dados
            return {
                "status": "Success",
                "mensagem": f"Dados do ano {ano} processados e salvos com sucesso no banco de dados.",
                "status_code": 200
            }

        # Tratamento de erros durante o processamento
        except Exception as e:
            return {
                "status": "Fail",
                "mensagem": f"Erro no processamento Banco de Dados: {e}",
                "status_code": 500
            }

    # Método para contar a quantidade de certificados por órgão certificador, com opções de filtragem por ano, mês e OCD específico
    def contar_certificados(self, ano:Optional[int] = None, mes:Optional[str] = None, ocd_enviado: Optional[str] = None):

        if mes is not None:
            # Converte o nome do mês em texto para o número correspondente (ex: 'janeiro' -> 1)
            mes_num = self.lista_mes.get(mes.lower())
        else:
            mes_num = None
        
        if ano is not None and mes_num is not None:
            comando_sql = f"SELECT * FROM certificados WHERE ano_filtro = {ano} AND mes_filtro = {mes_num}"
        elif ano is not None and mes_num is None:
            comando_sql = f"SELECT * FROM certificados WHERE ano_filtro = {ano}"
        elif ano is None and mes_num is not None:
            comando_sql = f"SELECT * FROM certificados WHERE mes_filtro = {mes_num}"
        else:
            comando_sql = "SELECT * FROM certificados"


        try:
            # Abre conexão e busca dados filtrados do banco usando Pandas
            conn = sqlite3.connect(self.db_path)

            # Lê os dados diretamente para um DataFrame do Pandas, facilitando a manipulação e filtragem dos dados
            df = pd.read_sql_query(comando_sql, conn)
            conn.close()

        # Tratamento de erros para garantir que qualquer problema na consulta ao banco seja capturado 
        # e comunicado de forma clara
        except Exception as e:
            return {
                "status": "Fail",
                "mensagem": f"Erro ao consultar o Banco de Dados: {e}",
                "status_code": 500
            }
        

        # Verifica se o DataFrame resultante da consulta está vazio. Se estiver vazio, significa que não há dados 
        # para o ano e mês especificados, e a função retorna uma resposta de erro indicando que nenhum dado foi encontrado.
        if df.empty:
            return {
                "status": "Fail",
                "mensagem": "Nenhum dado encontrado.",
                "status_code": 404
            }

        # Se um OCD específico foi enviado como parâmetro, a função cria uma lista contendo apenas esse OCD.
        #  Caso contrário, a função chama a função auxiliar 'ocds' para extrair a lista de OCDs únicos 
        # presentes na coluna 'certificado_tecnico' do DataFrame.
        if ocd_enviado is not None:
            lista_ocd = [ocd_enviado]
        else:
            # Chame sua função auxiliar 'ocds' ou extraia as ocds direto do df se preferir
            lista_ocd = ocds(df['certificado_tecnico'])

        saida = {}
        coluna = "certificado_tecnico" # Nome atualizado da coluna no banco
        
        # Para cada OCD na lista de OCDs, a função filtra o DataFrame para incluir apenas as linhas onde a coluna 
        # 'certificado_tecnico' contém o nome do OCD. Em seguida, conta a quantidade de certificados únicos
        # para esse OCD e armazena o resultado em um dicionário de saída, mapeando o nome do OCD para a quantidade de certificados encontrados.
        if lista_ocd:
            for ocd in lista_ocd:
                df_filtrado = df[df[coluna].str.contains(ocd, na=False)]
                quantidade_certificados = df_filtrado[coluna].nunique()

                if quantidade_certificados:
                    if ocd in self.dict_name:
                        ocd = self.dict_name[ocd]
                    saida[ocd.upper()] = quantidade_certificados

        # Agrupamentos específicos (ABCP vs BRICS / CPQD / OCPTELLI)
        if 'ABCP' in saida and 'BRICS' in saida:
            if saida['BRICS'] > saida['ABCP']:
                saida['BRICS'] -= saida['ABCP']

        if 'CPQD' in saida and 'CPQD-I' in saida:
            saida['CPQD'] += saida['CPQD-I']
            saida.pop('CPQD-I')

        if 'OCP-I' in saida and 'OCPTELLI' in saida:
            saida['OCPTELLI'] += saida['OCP-I']
            saida.pop('OCP-I')
        elif 'OCP-I' in saida and 'OCPTELLI' not in saida:
            saida['OCPTELLI'] = saida.pop('OCP-I')

        # Cria uma lista de dicionários a partir do dicionário de saída, onde cada dicionário contém o nome do OCD 
        # e a quantidade de certificados correspondente.
        resultado = [{"ocd": k, "quantidade_de_certificado": v} for k, v in saida.items()]
        dados = sorted(resultado, key=lambda item: item['quantidade_de_certificado'], reverse=True)      
        
        # Retorna uma resposta de sucesso contendo a mensagem de que os certificados foram obtidos com sucesso,
        # o resultado da contagem de certificados por OCD e o código de status HTTP 200 indicando que a requisição foi bem-sucedida.
        return {
            "status": "Success",
            "mensagem": f"Certificados de {mes} de {ano} obtidos com sucesso.",
            "result": dados,
            "status_code": 200
        }