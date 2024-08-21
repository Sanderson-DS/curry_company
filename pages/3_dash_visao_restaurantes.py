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
import numpy as np
from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title= 'Visão Restaurantes', page_icon= ':)', layout= 'wide')


# ===============================================================
# Funções  
# ===============================================================

def avg_std_time_on_traffic( df1 ):
    df_aux =(df1.loc[:,['Time_taken(min)','City', 'Road_traffic_density']]
                    .groupby(['City','Road_traffic_density'])
                    .agg({'Time_taken(min)':['std', 'mean']}))

    df_aux.columns = ['std', 'mean']
    df_aux = df_aux.reset_index()
    

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values= 'mean',
                    color= 'std', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['std']) )
    return fig  

def avg_std_time_graph( df1 ):
    df_aux =df1.loc[:,['Time_taken(min)','City']].groupby('City').agg({'Time_taken(min)':['std', 'mean']})
    df_aux.columns = ['std', 'mean']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar ( name = 'Control',
                        x=df_aux['City'],
                        y=df_aux['mean'],
                        error_y=dict( type= 'data', array=df_aux['std'])))

    fig.update_layout(barmode='group')

    return fig

def avg_std_time_delivery( df1, festival,op ):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        parametros:
            Input:
                - df: Dataframe com os dados necessário para o cálculo
                    'avg_time': Calcula o tempo medio
                    'std_time': Calcula o desvio padrão do tempo.
            Output:
                - df: Dataframe com 2 colunas e 1 linha.
    
    """
    df_aux = (df1.loc[:,['Time_taken(min)','Festival']]
                    .groupby('Festival')
                    .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linhas_selecionadas, op],2)

    return df_aux

def distance( df1, fig ):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude' ]

        df1['Distances'] =(df1.loc[:,cols]
                            .apply(lambda x: 
                            haversine((
                            x['Restaurant_latitude'], 
                            x['Restaurant_longitude']),(
                            x['Delivery_location_latitude'],
                            x['Delivery_location_longitude']) ), 
                                axis=1))
        avg_distance = np.round(df1['Distances'].mean(),2)
        return avg_distance
    
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude' ]

        df1['Distances'] =(df1.loc[:,cols]
                            .apply(lambda x: 
                            haversine((
                            x['Restaurant_latitude'], 
                            x['Restaurant_longitude']),(
                            x['Delivery_location_latitude'],
                            x['Delivery_location_longitude']) ), 
                                axis=1))
        avg_distance = df1.loc[:,['City', 'Distances']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[ go.Pie(labels=avg_distance['City'], values=avg_distance['Distances'], pull=[0,0.1,0])])
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

st.title('Marketplace - Visão Restaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.header('Indicadores Gerais')
        col1, col2, col3= st.columns( 3, gap = 'large') 
        with col1:
            entregadores_unicos = len(df1['Delivery_person_ID'].unique())
            col1.metric('Qtd entregadores',entregadores_unicos)

        with col2:
            avg_distance = distance( df1, fig = False )
            col2.metric('Distancia média', avg_distance)  

        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes','avg_time')
            col3.metric('Md_Entrega_Festival', df_aux)
            


    with st.container():
        col4, col5, col6= st.columns( 3, gap = 'large')

        with col4:
            df_aux = avg_std_time_delivery(df1,'Yes', 'std_time')
            col4.metric('std_Entrega_Festival', df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1,'No', 'avg_time')
            col5.metric('Md_Entrega', df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df1,'No', 'std_time')
            col6.metric('std_Entrega', df_aux)

    with st.container():
        st.markdown("""---""")
        st.subheader('Tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')
        col1, col2 = st.columns( 2 )
        


        with col1:

            fig = avg_std_time_graph( df1 )
            st.plotly_chart(fig)
           
        with col2:
            df_aux2 =(df1.loc[:,['Time_taken(min)','City', 'Type_of_order']]
            .groupby(['City','Type_of_order'])
            .agg({'Time_taken(min)':['std', 'mean']}))
            df_aux2.columns = ['std', 'mean']
            df_aux2 = df_aux2.reset_index()
            st.dataframe( df_aux2 )
                



    with st.container():
        st.markdown("""---""")
        st.subheader('Tempo médio e desvio padrão de entrega por cidade e tipo de tráfego.')
        col1, col2 = st.columns( 2 )


        with col1:
            fig = distance( df1, fig = True )
            st.plotly_chart(fig)
        
        
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart(fig)



    