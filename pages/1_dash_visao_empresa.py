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

st.set_page_config(page_title= 'Visão Empresa', page_icon= ':)', layout= 'wide')
# ===============================================================
# Funções
# ===============================================================

def country_maps( df1 ):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df_aux = (df1.loc[:,cols]
            .groupby(['City', 'Road_traffic_density'])
            .median()
            .reset_index())

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City','Road_traffic_density']]).add_to( map )
    folium_static(map,width= 1024, height= 600)
    return None

def order_share_by_week( df1 ):
    df_aux01 = (df1.loc[:,['ID','Week_of_Year']]
                .groupby('Week_of_Year')
                .count()
                .reset_index())
    df_aux02 = (df1.loc[:,['Delivery_person_ID','Week_of_Year']]
                .groupby('Week_of_Year')
                .nunique()
                .reset_index())
    df_aux = pd.merge(df_aux01, df_aux02, how= 'inner')
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, y='Order_by_delivery', x='Week_of_Year')
    return fig

def order_by_week( df1 ):
    # Criar a coluna da semana do ano:
    df1['Week_of_Year'] = df1['Order_Date'].dt.strftime( '%U' )
    # Selecionando as colunas
    colunas = ['ID','Week_of_Year']
    # somar os pedidos por semana
    df2 = df1.loc[:,colunas].groupby('Week_of_Year').count().reset_index()
    # Criar o gráfico
    fig = px.line(df2,x='Week_of_Year', y='ID', title= 'Pedidos por semana')
    return fig

def traffic_order_city( df1 ):
    df_aux =(df1.loc[:,['ID','City','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .count()
                .reset_index())
    #Criar o gráfico:
    fig = px.scatter(df_aux,x= 'City', y='Road_traffic_density', size='ID', color= 'City')
    return fig

def traffic_order_share( df1 ):
    # Selecionando as colunas
    cols = ['ID','Road_traffic_density']

    # somar os pedidos por semana
    df_aux = (df1.loc[:,cols]
              .groupby('Road_traffic_density')
              .count()
              .reset_index())
    df_aux['% Pedidos'] = df_aux['ID'] / df_aux['ID'].sum()

    # Criar o gráfico
    fig = px.pie(df_aux, names='Road_traffic_density', values='% Pedidos',hole=0.5)
    
    return fig

def order_metric( df1 ):     
    # Selecao de colunas
    cols = ['ID', 'Order_Date']
    # Selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    # Criar o gráfico
    fig = px.bar(df_aux, x= 'Order_Date', y='ID', title= 'Pedidos por dia')

    return fig 

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

# import dataset
df = pd.read_csv( '../datasets/train.csv' )

# Limpando os dados
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

#st.dataframe( df1 )

# ==============================================================
# Layout no Streamlit 
# ==============================================================
st.header('Marketplace - Visão Cliente')
#st.header(date_slider)
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('## Order Metric')
        fig = order_metric( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width=True)
      
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('1# Order Share by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    country_maps( df1 )

