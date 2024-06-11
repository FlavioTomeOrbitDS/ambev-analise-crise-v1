from transformers import GPT2Tokenizer

# description = """
#  Perfil: Analista de Crise de Marca

#  Objetivo: Monitorar e responder a crises de reputação que possam afetar a imagem pública da marca. Utilizar análises de sentimentos, identificação de tendências nas redes sociais e outros dados relevantes para informar estratégias de comunicação e resposta.

# Capacidades:
# Análise de Sentimentos: Avaliar rapidamente os sentimentos dos consumidores em relação à marca com base em comentários nas redes sociais, notícias e outras fontes de mídia.
# Identificação de Tendências: Detectar mudanças de humor ou novas preocupações que estão ganhando tração entre o público e que podem afetar a marca.
# Comunicação de Crise: Formular respostas e declarações para a mídia e stakeholders que abordem as preocupações do público de maneira transparente e eficaz.
# Assessoria Estratégica: Oferecer recomendações baseadas em análises para ajudar a marca a mitigar os impactos negativos durante e após a crise.
# Relatórios Detalhados: Preparar relatórios sobre o status da crise, incluindo análises de impacto, respostas da marca e recomendações para ações futuras.

# Trabalho Principal:
# Analisar um conjunto de comentários de redes sociais, possivelmente relacionados a algum evento ou crise que seja relevante para a marca.

# Diretrizes:
# Manter uma linguagem profissional e corporativa.
# Priorizar respostas rápidas mas fundamentadas para mitigar rapidamente qualquer dano à reputação.
# Ser proativo na identificação de potenciais crises antes que se intensifiquem.
# Manter um alto nível de confidencialidade e discrição em comunicações sensíveis.

# """

description = """
Você é um analista de crises de marcas e trabalha para a marca Ambev. 
O usuário irá inserir uma lista de comentários de uma rede social associadas a ao contexto informado.
Seu trabalho é ler o comentário fazer os seguintes passos:
1. Faça a análise de sentimentos, informando o número de comentários relacionados a cada sentimento.
2. Crie 5 principais categorias baseado nas palavras chave mais importantes dos textos.
3. gere o comentário médio baseado nos comentários.
"""

context = """ O contexto da crise é a mudança nos igredientes de produção da cerveja Heineken que alguns usuários estão alegando que alterou o sabor ] """

def update_conversation_context(messages, max_length=4096):
    """
    Atualiza o contexto da conversa, mantendo mensagens com role 'system' e removendo outras antigas quando o limite de tokens é atingido.
    
    Parâmetros:
    - messages (list of dict): Lista de dicionários contendo as mensagens e seus roles.
    - max_length (int): Comprimento máximo de tokens para o contexto.

    Retorna:
    - list: Lista de dicionários atualizada após a remoção das mensagens antigas para manter o contexto dentro do limite.
    """
    # Inicializa o tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    # Tokeniza cada mensagem e mantém a contagem de tokens
    tokenized_messages = [(msg, tokenizer.encode(msg['content'], add_special_tokens=False)) for msg in messages]
    total_tokens = sum(len(tokens) for _, tokens in tokenized_messages)

    # Enquanto o número total de tokens exceder o máximo permitido, remova as mensagens mais antigas
    # que não são do tipo 'system'
    index = 0
    while total_tokens > max_length and index < len(tokenized_messages):
        if tokenized_messages[index][0]['role'] != 'system':
            removed_message, removed_tokens = tokenized_messages.pop(index)
            total_tokens -= len(removed_tokens)
            print(f"Removendo mensagem antiga: {removed_message['content']}")
        else:
            index += 1  # Pula mensagens de 'system'

    # Reconstrói a lista de mensagens a partir dos tokens restantes
    updated_messages = [{'role': msg['role'], 'content': tokenizer.decode(tokens)} for msg, tokens in tokenized_messages]

    return updated_messages