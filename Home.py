import streamlit as st
from PIL import Image


st.set_page_config(
    page_title= 'Home',
    page_icon= ':)',
    layout= 'wide'
)

# image_path = 'c:/Users/sande/Documents/Cursos/DS_Formation-Comunidade_DS_Meigarom-2022/4-FTC Analisando dados com Python/Ciclo 06 Visualização Interativa/'
image = Image.open('alvo.png')
st.sidebar.image(image, width = 120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write( '# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de 
    cresimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no WPP
        - Sanderson - 45 9 9950-3597
    """ 
)