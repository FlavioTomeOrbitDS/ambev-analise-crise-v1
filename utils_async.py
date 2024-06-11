import pandas as pd
import asyncio
import aiohttp
import json
import datetime



description = """
Você é um analista de crises de marcas e trabalha para a marca Ambev. 
O usuário irá inserir uma lista de comentários de uma rede social associadas a ao contexto informado.
Seu trabalho é ler o comentário fazer os seguintes passos a partir do contexto dado:
1. Faça a análise de sentimentos, informando o número de comentários relacionados a cada sentimento.
2. Crie 5 principais categorias baseado nas palavras chave mais importantes dos textos. Informe também a quantidade de comentários relacionados a cada palavra chave.
3. gere o comentário médio baseado nos comentários.
"""


def dividir_dataframe_em_blocos(df, tamanho_bloco=100):
    """
    Divide um DataFrame em vários sub-DataFrames com um número especificado de linhas
    e retorna uma lista de listas contendo os textos da coluna 'Texto' de cada bloco.
    
    Parâmetros:
        df (pd.DataFrame): DataFrame original para ser dividido.
        tamanho_bloco (int): Número de linhas em cada bloco (sub-DataFrame).
    
    Retorna:
        lista_de_textos_bloco (list of list of str): Lista contendo listas dos textos de cada bloco.
    """
    if 'Texto' not in df.columns:
        raise ValueError("A coluna 'Texto' não está presente no DataFrame.")
    
    num_blocos = (len(df) + tamanho_bloco - 1) // tamanho_bloco
    lista_de_textos_bloco = [df['Texto'][i*tamanho_bloco:(i+1)*tamanho_bloco].tolist() for i in range(num_blocos)]
    
    return lista_de_textos_bloco

def concatena_textos_blocos(blocos_de_textos):    
    lista_de_strings = []
    for bloco in blocos_de_textos:
        # Concatenar os textos do bloco com quebra de linha entre eles
        texto_concatenado = '\n'.join(bloco)
        lista_de_strings.append(texto_concatenado)
    
    return lista_de_strings


async def make_api_call_to_gpt(prompt, api_key):
    print(f"##### Calling API...: {datetime.datetime.now()}")
    
    headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
    }
    #print(prompt)
    async with aiohttp.ClientSession() as session:                
        payload = {
            "model": "gpt-4",
            #"messages": [{"role": "user", "content": prompt}],
            "messages": prompt,
            "temperature": 0,
            "max_tokens": 4096,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        async with session.post('https://api.openai.com/v1/chat/completions',
                                headers=headers, data=json.dumps(payload)) as response:
            if response.status == 200:
                resp_json = await response.json()
                return resp_json['choices'][0]['message']['content']
            else:
                return f"Error: {response.status}"


async def retorna_valor_final(results, api_key):
    print(f"##### Making Final Analysis....{datetime.datetime.now()}")
    prompt = [] 
    texto_concatenado = ''
    
    prompt.append({'role': 'system',  'content' : """O usuário irá inserir uma lista de resultados de análises de redes sociais. Com base nesses resultados faça as seguintes tarefas:
                    1. Faça a quantificação total dos sentimentos, mostrando somente o resultado final da soma juntamente com o percentual em relação ao total;
                    2. crie 5 categorias a partir das palavras chave mais recorrentes que possam classificar os comentários a partir de uma frase, mostrando também a quantidade de comentários relacionados a cada categoria;
                    3. Gere um comentário médio que resuma as analises feitas. Utilize uma linguagem executiva;"""})    
    for i in results:
        texto_concatenado = texto_concatenado + " \n "+i
    
    prompt.append({'role': 'user', 'content':f"lista de análises: {texto_concatenado}"})
    
    resultado_final = await make_api_call_to_gpt(prompt, api_key)
    
    print(f"##### Resultado final...{datetime.datetime.now()}: {resultado_final}")
    
    return resultado_final
    
    
async def process_comments(df, context, api_key):
    
    print(f"##### Async Process Init...{datetime.datetime.now()}")
    # df = le_arquivo()    
    
    blocos_de_textos = dividir_dataframe_em_blocos(df)
    concatenados = concatena_textos_blocos(blocos_de_textos)
    
    #prompts = ["crie uma história com 3 paragrafos!", "me ensine como fazer arroz"]
    prompts = []
    dicionario_de_prompts = []
    for i in concatenados:
        prompts = []
        prompts.append({'role': 'system',  'content' : description})    
        prompts.append({'role': 'system',  'content' : f"O contexto da análise é:{context}"})    
        prompts.append({'role': 'assistant',  'content' : f"comentários: {i}"})
        dicionario_de_prompts.append(prompts)
    
    # print("*************DICIONARIO")
    # print(dicionario_de_prompts[0])
    results = []
    tasks = [make_api_call_to_gpt(prompt, api_key) for prompt in dicionario_de_prompts]
    results = await asyncio.gather(*tasks)
    
    # print("*****************RESULTS")
    # print("Gerando resultado final...")
    resultado_final = await retorna_valor_final(results,api_key)
    
    return resultado_final

if __name__ == "__main__":
    asyncio.run(process_comments())
