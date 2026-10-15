<h1 align="center">
  Market Share
</h1>

<p align="center">
 <img src="https://img.shields.io/static/v1?label=Instagram&message=@filipe_lisboa07&color=8257E5&labelColor=000000" alt="@filipe_lisboa07" />
 <img src="https://img.shields.io/static/v1?label=Tipo&message=Automacao&color=8257E5&labelColor=000000" alt="Automação" />
</p>

API para mapeamento de Market Share de Organismos de Certificação Designados (OCD) homologados pela ANATEL.

## Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/#requirements)
- [Pandas](https://pandas.pydata.org/docs/)
- [Streamlit](https://docs.streamlit.io/)
- [SQlite](https://sqlite.org/docs.html)

## 🚀 Como Executar o Projeto

1. Clonar repositório git
   ```bash
   git clone https://github.com/Lipe-lisboa/Projeto-Moderna.git
   ```
2. Crie um ambiente virtual e faça o dowload das bibliotecas necessárias
   ```bash
   pip install -r requirements.txt
   ```
3. Renomeie o arquivo banco_exemplo.db para que o sistema reconheça o banco de dados
   ```bash
   Altere o nome de banco_exemplo.db para banco.db
   ```

## 🛠️ Inicializando a Aplicação

- Para executar a aplicação entre no diretorio em que a API se encontra (src):

  ```bash
  cd backend
  cd src  
  uvicorn api:app --reload
  ```

### 🎨 Executando o Frontend (Streamlit)

Com a API já em execução, **abra uma nova aba ou janela do seu terminal** e siga os passos abaixo:

1. Entre no diretório do frontend:
   ```bash
   cd frontend
   ```
2. Execute a aplicação do Streamlit:
   ```bash
   streamlit run app.py
   ```

O dashboard em Streamlit abrirá automaticamente no seu navegador pelo endereço: http://localhost:8501

Vc também pode acessar a API em [127.0.0.1:8000](http://127.0.0.1:8000). O Swagger poderá ser visualizado em [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🔌 API Endpoints

Abaixo estão listados os principais endpoints da API. Você pode testar essas requisições utilizando ferramentas como [Insomnia](https://insomnia.rest/), [Postman](https://www.postman.com/) ou diretamente pela documentação interativa do Swagger em `http://127.0.0.1:8000/docs`.

---

### 1. Carregar Dados Anatel

Gera os arquivos no formato Parquet com base no ano fornecido.

* **Método:** `POST`
* **URL:** `http://127.0.0.1:8000/carregar-dados`
* **Parâmetros de Query:**
  * `ano` (obrigatório): O ano que deseja processar (Ex: `2026`).

<details>
<summary><b>▶ Ver Exemplo de Resposta (200 OK)</b></summary>

```json
{
    "status": "Success",
    "mensagem": "Arquivos Parquet para o ano 2026 foram criados com sucesso.",
    "result": "Processamento do ano 2026 concluído com sucesso!"
}

```

**Exemplo de Requisição:**

    POST[http://127.0.0.1:8000/carregar-dados?ano=2026](http://127.0.0.1:8000/carregar-dados?ano=2026)

</details>

### 2. Contagem Geral de Certificados por OCD

Retorna a listagem e contagem de certificados de todas as OCDs com base no ano e mês informados.

* **Método:** `GET`
* **URL:** `http://127.0.0.1:8000/certificados`
* **Parâmetros de Query:**
  * `ano` (Opcional): O ano que deseja processar (Ex: `2026`).
  * `mês` (Opcional): Mês de busca em letras maiúsculas (ex: JANEIRO).

<details>
<summary><b>▶ Ver Exemplo de Resposta (200 OK)</b></summary>

```json
{
    "status": "Success",
    "mensagem": "Contagem de certificados para o ano 2026 e mês JANEIRO obtida com sucesso.",
    "result": [
        {
            "ocd": "MODERNA",
            "quantidade_de_certificado": XXX
        },
        {
            "ocd": "NCC",
            "quantidade_de_certificado": XXX
        },
        {
            "ocd": "ICC",
            "quantidade_de_certificado": XXX
        }
    ]
}

```

**Exemplo de Requisição:**

    GET[http://127.0.0.1:8000/certificados?ano=2026&amp;mes=JANEIRO](http://127.0.0.1:8000/certificados?ano=2026&mes=JANEIRO)

</details>

### 3. Filtrar Certificados de uma OCD Específica

Retorna a quantidade de certificados emitidos por uma organização específica (ex: MODERNA), filtrando por ano e mês.

* **Método:** `GET`
* **URL:** `http://127.0.0.1:8000/certificados/{OCD}`
* **Parâmetros de Query:**
  * `OCD` (obrigatório): O nome da organização na URL (ex: MODERNA).
  * `Ano` (obrigatório): O ano de busca (ex: 2026)
  * `Mês` (obrigatório): Mês de busca em letras maiúsculas (ex: JANEIRO).

<details>
<summary><b>▶ Ver Exemplo de Resposta (200 OK)</b></summary>

```json
{
    "status": "Success",
    "mensagem": "Contagem de certificados para o ano 2026 e mês JANEIRO obtida com sucesso.",
    "result": [
        {
            "ocd": "MODERNA",
            "quantidade_de_certificado": XXX
        }
    ]
}

```

**Exemplo de Requisição:**

    GET[http://127.0.0.1:8000/certificados/MODERNA?ano=2026&amp;mes=JANEIRO](http://127.0.0.1:8000/certificados/MODERNA?ano=2026&mes=JANEIRO)

</details>
