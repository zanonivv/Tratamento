import streamlit as st
import pandas as pd
import re

def main():
    st.title("Tratamento de Dados")

    st.write("Por favor, carregue seu arquivo e selecione as opções de tratamento.")

    # File uploader
    uploaded_file = st.file_uploader("Escolha um arquivo Excel ou CSV", type=['xlsx', 'xls', 'csv'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith('.xlsx') or uploaded_file.name.lower().endswith('.xls'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.lower().endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                st.error("Formato de arquivo não suportado.")
                return

            st.success(f"Arquivo '{uploaded_file.name}' carregado com sucesso!")

            # Display dataframe preview
            st.subheader("Pré-visualização dos Dados:")
            st.dataframe(df.head())

            # Select treatments
            st.subheader("Selecione os tratamentos desejados:")
            treatments = {}
            treatments["Tratar Telefones"] = st.checkbox("Tratar Telefones")
            treatments["Higienizar Nomes"] = st.checkbox("Higienizar Nomes")
            treatments["Selecionar Primeiro Nome"] = st.checkbox("Selecionar Primeiro Nome")

            if any(treatments.values()):
                # Column selection
                columns = {}
                st.subheader("Selecione as colunas correspondentes:")

                if treatments["Higienizar Nomes"] or treatments["Selecionar Primeiro Nome"]:
                    name_column = st.selectbox("Coluna de Nomes:", options=df.columns)
                    columns['name_column'] = name_column

                if treatments["Tratar Telefones"]:
                    phone_column = st.selectbox("Coluna de Telefones:", options=df.columns)
                    columns['phone_column'] = phone_column

                # Process data
                if st.button("Processar Dados"):
                    with st.spinner("Processando..."):
                        # Process data using the `process_data` function
                        output_df = df.copy()
                        process_data(output_df, treatments, columns)

                    st.success("Dados processados com sucesso!")

                    # Display processed data
                    st.subheader("Dados Tratados:")
                    st.dataframe(output_df.head())

                    # Download processed data
                    @st.cache_data
                    def convert_df(df):
                        # Convert DataFrame to Excel in memory
                        from io import BytesIO
                        output = BytesIO()
                        writer = pd.ExcelWriter(output, engine='xlsxwriter')
                        df.to_excel(writer, index=False, sheet_name='Dados Tratados')
                        writer.close()
                        processed_data = output.getvalue()
                        return processed_data


                    excel_bytes = convert_df(output_df)
                    st.download_button(
                        label="Baixar arquivo Excel",
                        data=excel_bytes,
                        file_name='dados_tratados.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
            else:
                st.warning("Por favor, selecione ao menos um tratamento.")

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

def process_data(df, treatments, columns):
    if treatments.get("Higienizar Nomes", False):
        name_col = columns.get('name_column', None)
        if name_col in df.columns:
            df['Nome_Higienizado'] = df[name_col].apply(sanitize_name)
        else:
            st.error(f"A coluna '{name_col}' não está presente no arquivo.")

    if treatments.get("Selecionar Primeiro Nome", False):
        name_col = columns.get('name_column', None)
        if name_col in df.columns:
            if 'Nome_Higienizado' in df.columns:
                df['Primeiro_Nome'] = df['Nome_Higienizado'].apply(get_first_name)
            else:
                df['Primeiro_Nome'] = df[name_col].apply(get_first_name)
        else:
            st.error(f"A coluna '{name_col}' não está presente no arquivo.")

    if treatments.get("Tratar Telefones", False):
        phone_col = columns.get('phone_column', None)
        if phone_col in df.columns:
            df['Telefone_Tratado'] = df[phone_col].apply(clean_phone_number)
        else:
            st.error(f"A coluna '{phone_col}' não está presente no arquivo.")

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

if __name__ == '__main__':
    main()
