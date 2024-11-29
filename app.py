import streamlit as st
import pandas as pd
import re
import unicodedata
from io import BytesIO

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
                        output_df = process_data(df, treatments, columns)

                    st.success("Dados processados com sucesso!")

                    # Display processed data
                    st.subheader("Dados Tratados:")
                    st.dataframe(output_df.head())

                    # Download processed data
                    excel_bytes = convert_df_to_excel(output_df)
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
    output_df = pd.DataFrame()

    if treatments.get("Higienizar Nomes", False) or treatments.get("Selecionar Primeiro Nome", False):
        name_col = columns.get('name_column', None)
        if name_col in df.columns:
            # Higienizar os nomes
            df['Nome_Higienizado'] = df[name_col].apply(sanitize_name)

            # Adicionar coluna do nome completo tratado com capitalização
            output_df['Nome_Completo'] = df['Nome_Higienizado'].apply(format_name_capitalized)

            if treatments.get("Selecionar Primeiro Nome", False):
                # Selecionar o primeiro nome
                output_df['Primeiro_Nome'] = df['Nome_Higienizado'].apply(get_first_name)
            else:
                output_df['Primeiro_Nome'] = df['Nome_Higienizado']
        else:
            st.error(f"A coluna '{name_col}' não está presente no arquivo.")

    if treatments.get("Tratar Telefones", False):
        phone_col = columns.get('phone_column', None)
        if phone_col in df.columns:
            output_df['Telefone'] = df[phone_col].apply(clean_phone_number)
        else:
            st.error(f"A coluna '{phone_col}' não está presente no arquivo.")

    if output_df.empty:
        st.warning("Nenhuma coluna válida foi encontrada para processar.")
        return pd.DataFrame(columns=['Primeiro_Nome', 'Nome_Completo', 'Telefone'])  # Retornar DataFrame vazio para evitar erros

    return output_df

def sanitize_name(name):
    if pd.isna(name):
        return ''
    name = str(name)  # Garantir que é uma string

    # Remover emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U00002600-\U000026FF"
        "]+", flags=re.UNICODE)
    name = emoji_pattern.sub(r'', name)

    # Remover a palavra 'tag' e caracteres especiais
    name = re.sub(r'\btag\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[^\w\s]', '', name)

    # Remover o caractere '|' e tudo antes dele
    if '|' in name:
        parts = name.split('|')
        if len(parts) > 1:  # Verificar se há algo após '|'
            name = parts[-1].strip()
        else:
            name = parts[0].strip()

    # Remover acentos
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')

    # Remover espaços extras
    return ' '.join(name.split())

def get_first_name(name):
    if pd.isna(name) or not isinstance(name, str):
        return ''
    name = sanitize_name(name)
    parts = name.split()
    if parts:  # Verificar se há palavras após dividir
        return parts[0]
    return ''

def format_name_capitalized(name):
    """
    Capitaliza a primeira letra de cada palavra no nome tratado.
    """
    if pd.isna(name) or not isinstance(name, str):
        return ''
    name = sanitize_name(name)
    return ' '.join([word.capitalize() for word in name.split()])

def clean_phone_number(phone_number):
    if pd.isna(phone_number):
        return ''
    phone_number = re.sub(r'\D', '', str(phone_number))  # Remover tudo que não é número
    if len(phone_number) == 0:
        return ''  # Retornar vazio se não houver números

    if not phone_number.startswith('55'):
        phone_number = '55' + phone_number

    # Adicionar nono dígito, se necessário
    if len(phone_number) == 12 and phone_number[4] != '9':
        phone_number = phone_number[:4] + '9' + phone_number[4:]

    return phone_number

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Nome e Telefone')
    writer.close()
    return output.getvalue()

if __name__ == '__main__':
    main()
