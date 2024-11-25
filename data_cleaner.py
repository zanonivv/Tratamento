import re
import pandas as pd

def sanitize_name(name):
    """
    Remove emojis, a palavra 'tag' e caracteres especiais do nome.
    Extrai o nome real, mesmo que haja múltiplos '|'.
    :param name: Nome como string.
    :return: Nome sem emojis, 'tag' ou caracteres especiais.
    """
    if pd.isna(name):
        return name
    name = str(name)  # Garantir que é uma string

    # Remover emojis primeiro
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Símbolos e pictogramas
        "\U0001F680-\U0001F6FF"  # Transportes e símbolos de mapas
        "\U0001F1E0-\U0001F1FF"  # Bandeiras
        "\U00002700-\U000027BF"  # Símbolos diversos
        "\U0001F900-\U0001F9FF"  # Símbolos suplementares
        "\U00002600-\U000026FF"  # Símbolos miscelâneos
        "]+", flags=re.UNICODE)
    name = emoji_pattern.sub(r'', name)

    # Remover espaços no início e no fim
    name = name.strip()

    # Remover a palavra 'tag' em qualquer posição (case-insensitive)
    name = re.sub(r'\btag\b', '', name, flags=re.IGNORECASE)

    # Remover o caractere '|' e tudo antes dele
    if '|' in name:
        name = name.split('|')[-1].strip()

    # Remover caracteres especiais, mantendo letras, números e espaços
    name = re.sub(r'[^\w\s]', '', name)

    # Remover espaços extras entre palavras
    name = ' '.join(name.split())

    return name.strip()

def get_first_name(name):
    """
    Seleciona o primeiro nome da string e capitaliza apenas a primeira letra.
    :param name: Nome completo como string.
    :return: Primeiro nome com capitalização adequada.
    """
    if pd.isna(name):
        return name
    name = sanitize_name(name)
    if not name:
        return name
    first_name = name.split()[0]
    first_name = first_name.capitalize()
    return first_name

def add_country_code(phone_number):
    """
    Adiciona o código do país (55) ao número de telefone, se necessário.

    :param phone_number: Número de telefone como string.
    :return: Número de telefone com o código do país.
    """
    if pd.isna(phone_number):
        return phone_number
    phone_number = re.sub(r'\D', '', str(phone_number))
    if not phone_number.startswith('55'):
        phone_number = '55' + phone_number
    return phone_number

def add_ninth_digit(phone_number):
    """
    Adiciona o nono dígito ao número de celular, se necessário.

    :param phone_number: Número de telefone como string.
    :return: Número de telefone com o nono dígito.
    """
    if pd.isna(phone_number):
        return phone_number
    phone_number = re.sub(r'\D', '', str(phone_number))
    pattern = r'^(55)?(\d{2})(9)?(\d{4})(\d{4})$'
    match = re.match(pattern, phone_number)
    if match:
        country_code = match.group(1) if match.group(1) else ''
        area_code = match.group(2)
        ninth_digit = '9' if not match.group(3) else match.group(3)
        first_part = match.group(4)
        second_part = match.group(5)
        phone_number = f"{country_code}{area_code}{ninth_digit}{first_part}{second_part}"
    return phone_number

def clean_phone_number(phone_number):
    """
    Realiza o tratamento completo do número de telefone.

    :param phone_number: Número de telefone como string.
    :return: Número de telefone tratado.
    """
    if pd.isna(phone_number):
        return phone_number
    phone_number = add_country_code(phone_number)
    phone_number = add_ninth_digit(phone_number)
    return phone_number
