import streamlit as st
from collections import Counter
import pandas as pd
import numpy as np
from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from wordcloud import WordCloud
import seaborn as sns
from gensim import corpora, models
import gensim
from streamlit import components
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
from gensim.models import Word2Vec
import tensorflow as tf
import os
from streamlit_tensorboard import st_tensorboard
import tensorflow as tf
from tensorboard.plugins import projector
from TopCoinsByExchangeVolume import getTopCoinsByExchangeVolume_WebApi
from TopCoinsByExchangeVolume import getTopCoinsByExchangeVolume_DB

st.set_page_config(
    page_title="프로젝트팀 10조",
)

plt.rc('font', family='Malgun Gothic')

def load_data():
    data = pd.read_parquet('tokenized_data.parquet')
    return data
data = load_data()
all_words = [word for sublist in data['tokenized_content'] for word in sublist]


def plot_frequency(data,all_words, num_words=20):
    # 전체 단어 빈도 계산
    
    word_counts = Counter(all_words)

    # 가장 빈번한 단어 추출
    most_common_words = word_counts.most_common(num_words)
    words, counts = zip(*most_common_words)

    # 그래프 그리기
    fig, ax = plt.subplots()
    ax.barh(words, counts)
    ax.set_title('가장 자주 사용된 단어')
    return fig

def create_wordcloud(data,all_words):
    # 전체 텍스트 풀을 문자열로 변환
    text = ' '.join(all_words)

    # 워드 클라우드 객체 생성
    wordcloud = WordCloud(font_path='path/Pretendard-Bold.ttf',
                          width=800, height=400, background_color='white').generate(text)

    # 워드 클라우드 시각화
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig


def main():
            st.title("텍스트 데이터 시각화")
            
            
            analysis_contents = st.sidebar.radio("분석 내용", ['빈도 분석', '워드 클라우드'])
            if analysis_contents=='빈도 분석':
                # 빈도 분석 그래프
                freq_fig = plot_frequency(data,all_words)
                st.write("### 빈도 분석 그래프")
                st.pyplot(freq_fig)
            elif analysis_contents=='워드 클라우드':
                # 워드 클라우드
                wordcloud_fig = create_wordcloud(data,all_words)
                st.write("### 워드 클라우드")
                st.pyplot(wordcloud_fig)



def plot_top_words(lda_model, nb_topics):
    figs = []
    for i in range(nb_topics):
        fig, ax = plt.subplots(figsize=(8, 4))
        topic_words = dict(lda_model.show_topic(i, 10))
        ax.bar(range(len(topic_words)), list(topic_words.values()), align='center', color='dodgerblue')
        ax.set_xticks(range(len(topic_words)))
        ax.set_xticklabels(list(topic_words.keys()), rotation=30, ha='right')
        ax.set_title(f'Topic {i+1}')
        ax.set_ylabel('Weight')
        figs.append(fig)
    return figs

def prepare_data(data, ldamodel, corpus):
    # 'created_date' 열을 datetime 타입으로 변환합니다.
    data['created_date'] = pd.to_datetime(data['created_date'])

    # 각 문서의 주요 토픽을 결정합니다.
    data['main_topic'] = [max(ldamodel[doc], key=lambda x: x[1])[0] for doc in corpus]

    # 시간에 따른 토픽의 빈도를 계산합니다.
    topic_over_time = data.groupby([data['created_date'].dt.day, 'main_topic']).size().unstack().fillna(0)
    
    return topic_over_time


def calculate_average_recommendations(data):
    # 주요 토픽과 추천수 간의 관계를 분석합니다.
    topic_recommendation = data.groupby('main_topic')['recommendation'].mean().reset_index()
    return topic_recommendation

def plot_recommendations(topic_recommendation):
    # 시각화
    plt.figure(figsize=(10, 6))
    sns.barplot(x='main_topic', y='recommendation', data=topic_recommendation, palette='coolwarm')
    plt.title('토픽별 평균 추천수')
    plt.xlabel('토픽')
    plt.ylabel('평균 추천수')
    plt.xticks(range(len(topic_recommendation['main_topic'])), [f'Topic {i}' for i in topic_recommendation['main_topic']])
    plt.tight_layout()  # 텍스트 겹침 방지
    return plt

def load_w2v():
    model = Word2Vec.load("word2vec_tokenpost.model")
    max_vocab = 500
    # vectors = np.load('vectors.npy')  # 벡터 데이터 불러오기
    # words = np.load('words.npy')  # 단어 목록 불러오기
    vectors = np.zeros((max_vocab, model.vector_size))
    words = list(model.wv.index_to_key)[:max_vocab]
    return vectors, words


# 차원 축소 실행
def dimension_reduction(method):
    if method == 'PCA':
        reducer = PCA(n_components=3)
    elif method == 't-SNE':
        reducer = TSNE(n_components=3, learning_rate='auto', init='random')
    elif method == 'UMAP':
        reducer = umap.UMAP(n_components=3)
    return reducer.fit_transform(vectors)

# 시각화
def plot_embeddings(embeddings, words):
    fig = px.scatter_3d(
        x=embeddings[:, 0],
        y=embeddings[:, 1],
        z=embeddings[:, 2],
        text=words,
        title=f"{option} 결과로 시각화"
    )
    fig.update_traces(marker=dict(size=1.5))
    fig.update_layout(scene=dict(xaxis_title='Component 1',
                                 yaxis_title='Component 2',
                                 zaxis_title='Component 3'))
    return fig




data = pd.read_parquet('tokenized_data.parquet')
all_words = [word for sublist in data['tokenized_content'] for word in sublist]
# 사이드 바
st.sidebar.title("메뉴")
page = st.sidebar.radio("페이지 선택", ["가상화폐 및 블록체인 뉴스 분석", "상세 분석", "국내 5대 거래소에서의 거래량 Top20"])

if page == "가상화폐 및 블록체인 뉴스 분석":
    st.title("가상화폐 및 블록체인 뉴스 분석")
    st.write("이 대시보드는 가상화폐 및 블록체인에 대한 뉴스 기사를 분석하여 시각화합니다.")
    
    # 추천 수  를 기준으로 상위 문서들을 선택합니다.
    top_documents = data.nlargest(10, 'recommendation')

    # 상위 문서들의 제목, 추천 수, 그리고 주요 토픽을 출력합니다.
    top_documents=top_documents[['title','created_date', 'recommendation']]

    st.dataframe(top_documents)
elif page == "상세 분석":
    st.title("뉴스 기사 분석")
    analysis_type = st.sidebar.radio("분석 유형", ["빈도", "LDA", "Word2Vec"])
    
    if analysis_type == "빈도":
        st.header("단어 빈도 분석")             
        

        if __name__ == "__main__":
            main()
        

    elif analysis_type == "LDA":
        number = 1
        st.header("LDA 토픽 모델링")
        

        if st.button('Start LDA Modeling'):  
            # 토큰화된 데이터를 사전(dictionary)과 말뭉치(corpus)로 변환
            dictionary = corpora.Dictionary(data['tokenized_content'])
            corpus = [dictionary.doc2bow(text) for text in data['tokenized_content']]

            # LDA 모델 생성 및 훈련
            ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word = dictionary, passes=15)

            # 토픽과 그에 따른 단어들을 출력
            topics = ldamodel.print_topics(num_words=5)
            for topic in topics:
                st.write(topic)
            # 토픽 모델링 결과를 시각화하는 함수

            
            figs = plot_top_words(ldamodel, 5)
            for  fig in figs:
                st.header(f'Topic {number} 결과')
                st.pyplot(fig)
                number += 1
            
            topic_over_time = prepare_data(data, ldamodel, corpus)
            # 년도별 토픽 빈도를 시각화합니다.
            fig, ax = plt.subplots(figsize=(15, 7))
            topic_over_time.plot(kind='bar', stacked=True, colormap='viridis', ax=ax)
            ax.set_title('시간별 토픽 빈도')
            ax.set_ylabel('문서 수')
            ax.set_xlabel('4월')
            ax.legend(title='토픽', loc='upper left', labels=[f'Topic {i}' for i in range(topic_over_time.shape[1])])
            st.header("시간별 토픽 빈도")
            st.pyplot(fig)

            st.header("토픽별 평균 추천수 분석")
            topic_recommendation = calculate_average_recommendations(data)
            fig = plot_recommendations(topic_recommendation)
            st.pyplot(fig)
            # 준비된 LDA 모델과 말뭉치, 사전을 이용하여 시각화 데이터를 준비합니다.
            vis_data = gensimvis.prepare(ldamodel, corpus, dictionary)

            # 시각화를 위한 HTML 파일을 생성합니다.
            html_data = pyLDAvis.prepared_data_to_html(vis_data)
            components.v1.html(html_data, width=1300, height=800, scrolling=True)
            

                


    elif analysis_type == "Word2Vec":
        
        st.header("Word2Vec 시각화")
        # Word2Vec 모델링 및 시각화 로직
        # 차원 축소 선택
        
        # Word2Vec 모델 로드
        model = Word2Vec.load("word2vec_tokenpost.model")

        # 임베딩 벡터와 관련 메타데이터 준비
        max_vocab = 500
        vectors = np.zeros((max_vocab, model.vector_size))
        words = list(model.wv.index_to_key)[:max_vocab]

        for i, word in enumerate(words):
            vectors[i] = model.wv[word]

        # Tensorflow 변수로 임베딩 벡터 저장
        embedding_var = tf.Variable(vectors, name='word_embedding', trainable=False)

        # 체크포인트 생성 및 저장
        checkpoint_dir = 'logs/word2vec'
        checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
        checkpoint = tf.train.Checkpoint(embedding=embedding_var)
        checkpoint.save(file_prefix=checkpoint_prefix)

        # 메타데이터 파일 생성
        metadata_file = os.path.join(checkpoint_dir, 'metadata.tsv')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(f'{word}\n')

        # 프로젝터 설정
        config = projector.ProjectorConfig()
        embedding = config.embeddings.add()
        embedding.tensor_name = embedding_var.name
        embedding.metadata_path = 'metadata.tsv'

        # 로그 디렉토리 경로
        log_dir = 'logs/word2vec'

        # 프로젝터 설정을 저장
        
        projector.visualize_embeddings(log_dir, config)

        # 스트림릿에서 TensorBoard 시작
        st_tensorboard(logdir=log_dir, port=6006, width=1080)
        # option = st.selectbox(
        #     '차원 축소 기법을 선택하세요:',
        #     ('PCA', 't-SNE', 'UMAP')
        # )
        # vectors, words = load_w2v()
        # embeddings = dimension_reduction(option)
        # fig = plot_embeddings(embeddings, words)

        # st.plotly_chart(fig, use_container_width=True)

        # st.write("Word2Vec 모델을 사용하여 단어 임베딩 시각화.")
elif page == "국내 5대 거래소에서의 거래량 Top20":
    st.title('국내 5대 거래소에서의 거래량 Top20')

    sourceType = st.sidebar.radio("소스 유형", ["DB", "WebAPI"])
    
    df = None
    
    if sourceType == "DB":
        df = getTopCoinsByExchangeVolume_DB()
    elif sourceType == "WebAPI":
        df = getTopCoinsByExchangeVolume_WebApi()

    if df is not None:
        st.dataframe(
            df,
            use_container_width = True,
            column_config = {
                "아이콘" : st.column_config.ImageColumn(
                    "아이콘", help="Streamlit app preview screenshots"
                ),
                "최근 7일" : st.column_config.ImageColumn(
                    "최근 7일", help="Streamlit app preview screenshots"
                ),
            },
            hide_index = True,
        )
    else:
        st.subheader('조금뒤에 다시 시도해주세요.')