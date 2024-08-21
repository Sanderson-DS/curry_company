# ==============================================================
# Importando as bibliotecas
# ==============================================================

# libraries
import pandas as pd 
import io
import plotly.express as px
import folium 
import streamlit as st
import plotly.graph_objects as go
from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title= 'Visão Entregadores', page_icon= ':)', layout= 'wide')


# ===============================================================
# Funções  
# ===============================================================

def top_delivers( df1, top_asc):
    df2 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City','Time_taken(min)'], ascending=top_asc)
              .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban',:].head(10)

    df3 = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index( drop= True)

    return df3

def clean_code( df1 ):
    """ 
    Esta funcao tem a responsabilidade de limpar o dataframe

    Tipos de limpeza:
    1. Remoção do dados NaN
    2. Mudança do tipo de coluna de dados 
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo ( remoção do texto da variável númerica)
    
    Input: Dataframe
    Output: Dataframe
    """
  

    # Conversão 1 - Coluna age para inteiros
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversão 2 - Coluna ratings para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversão 3 - Coluna Order Date para data:
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Conversão 4 - Coluna multiple_deliveries para inteiros
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.extract(r'(\d{2})')
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( float )

    # Conversão 5 - Tirando os espaços usando iloc + strip:
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    
    return df1

# ===============================================================
# Início da Estrutura Lógica do código
# ===============================================================

# import database:
df = pd.read_csv( 'datasets/train.csv' )

# Chamando a função para limpeza dos dados:
df1 = clean_code( df )



# ===============================================================
# Barra Lateral Streamlit 
# ===============================================================

# image_path = 'c:/Users/sande/Documents/Cursos/DS_Formation-Comunidade_DS_Meigarom-2022/4-FTC Analisando dados com Python/Ciclo 06 Visualização Interativa/alvo.png'
image = Image.open( 'alvo.png' )
st.sidebar.image( image, width= 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione uma data limite')
date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime(2022, 2, 11 ),
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )
st.sidebar.markdown("""---""")



traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Sanderson Bergmann')

# Aplicando filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

# Aplicando filtri de tráfego:
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]



# ==============================================================
# Layout no Streamlit 
# ==============================================================

st.title('Marketplace - Visão Entregadores')
#st.header(date_slider)
#st.dataframe(df1)

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
  
    with st.container():
        st.markdown('## Indicadores Gerais')
        col1,col2,col3, col4 = st.columns(4)

        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade)
        with col2:
             # A menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            # A melhor condicao de veiculos
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric("Melhor condicao veiculos",melhor_condicao)
        with col4:
            # A pior condicao de veiculos
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric("Pior condicao veiculos", pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.markdown('## Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliações médias por Entregador')
            avaliacao = (df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
            .groupby('Delivery_person_ID')
            .mean().reset_index())
            st.dataframe(avaliacao)
        with col2:
            st.markdown('##### Avaliação média por transito')
            df2 = df1.loc[df1['Road_traffic_density'] != 'NaN ',:]

            # Usando a função agg para agregar dois calculos na analise:

            df_aux = (df2.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
            .groupby('Road_traffic_density')
            .agg({'Delivery_person_Ratings':['mean','std']})
            )

            df_aux.columns = ['delivery_Mean', 'delivery_std']
            df_aux.reset_index()
            st.dataframe(df_aux)
            st.markdown('##### Avaliação média por clima')
            condicoes_climaticas = (df2.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                            .groupby('Weatherconditions')
                            .agg({'Delivery_person_Ratings':['mean','std']}))

            # Renomear as colunas:

            condicoes_climaticas.columns = ['delivery_mean', 'delivery_std']
            condicoes_climaticas = condicoes_climaticas.reset_index()
            st.dataframe(condicoes_climaticas)
                
    with st.container():
        st.markdown("""---""")
        st.markdown('## Velocidade de Entrega')

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Top Entregadores mais rapidos')
            df3 = top_delivers( df1 , top_asc =True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers( df1 , top_asc =False)
            st.dataframe( df3 )