import streamlit as st
import pandas as pd
from main import process_data

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
                        # Process data using the existing `process_data` function
                        output_df = df.copy()
                        process_data(output_df, treatments, columns)

                    st.success("Dados processados com sucesso!")

                    # Display processed data
                    st.subheader("Dados Tratados:")
                    st.dataframe(output_df.head())

                    # Download processed data
                    @st.cache_data
                    def convert_df(df):
                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                        return df.to_excel(index=False)

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
    from data_cleaner import clean_phone_number, sanitize_name, get_first_name

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

if __name__ == '__main__':
    main()
