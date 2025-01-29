import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.ensemble import IsolationForest, GradientBoostingClassifier
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import FeatureUnion
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModel
import umap
import nltk
from nltk import pos_tag, word_tokenize
from nltk.chunk import RegexpParser
import re
import spacy
from spacy.matcher import Matcher
import requests
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import torch


nlp = spacy.load("en_core_web_sm")
DEEPSEEK_API_KEY = ""
API_URL = "https://api.deepseek.com/v1/chat/completions"

class NLPPatternExtractor:
    def __init__(self, top_n=5):
        self.top_n = top_n  # 仅保留配置参数

    def extract_opening_patterns(self, texts):
        """动态分析给定文本的开头模式"""
        # 依存模式提取逻辑（示例）
        opening_patterns = []
        for doc in nlp.pipe(texts):
            if len(doc) >= 3:
                pattern = "-".join([doc[0].dep_, doc[1].dep_, doc[2].dep_])
                opening_patterns.append(pattern)
        return Counter(opening_patterns).most_common(self.top_n)

    def extract_adj_clusters(self, texts):
        """动态分析形容词组合"""
        # 原检测逻辑（示例）
        adj_patterns = []
        matcher = Matcher(nlp.vocab)
        pattern = [{"POS": "ADJ"}, {"POS": {"IN": ["CCONJ", "PUNCT"]}}, {"POS": "ADJ"}]
        matcher.add("ADJ_PAIRS", [pattern])

        for doc in nlp.pipe(texts):
            matches = matcher(doc)
            for _, start, end in matches:
                adj_patterns.append(doc[start:end].text.lower())
        return Counter(adj_patterns).most_common(self.top_n)

# ---------------------------
# 零样本AI检测模块
# ---------------------------
class ZeroShotAIDetector:
    def __init__(self):
        self.detector = pipeline(
            "text-classification",
            model="roberta-base-openai-detector",  # 专门检测AI生成的预训练模型
            device=0 if torch.cuda.is_available() else -1
        )

    def predict(self, texts):
        results = self.detector(texts)
        return [result['score'] if result['label']=='AI' else 1-result['score']
                for result in results]

# ---------------------------
# 语义-句法联合嵌入
# ---------------------------
class UnifiedEmbedder:
    def __init__(self):
        self.semantic_model = SentenceTransformer('all-mpnet-base-v2')
        self.syntax_extractor = NLPPatternExtractor(top_n=5)  # 初始化时无需传入texts
        self.nlp = spacy.load("en_core_web_sm")  # 加载模型

    def embed(self, texts):
        semantic_emb = self.semantic_model.encode(texts, show_progress_bar=False)

        # 动态提取句法特征
        syntax_features = []
        for text in texts:
            doc = self.nlp(text)
            features = {
                'passive_ratio': self._passive_ratio(doc),
                'adj_clusters': len(self.syntax_extractor.extract_adj_clusters([text])),
                'opening_match': 1 if self._check_opening_pattern(text) else 0
            }
            syntax_features.append(list(features.values()))

        return np.hstack([semantic_emb, np.array(syntax_features)])

    def _passive_ratio(self, doc):
        """计算被动语态比例"""
        passive_count = sum(1 for token in doc if token.tag_ == "VBN" and token.dep_ == "auxpass")
        return passive_count / len(list(doc.sents)) if doc else 0

    def _check_opening_pattern(self, text):
        """检查动态提取的开头模式"""
        patterns = self.syntax_extractor.extract_opening_patterns([text])
        return len(patterns) > 0

# ---------------------------
# 无监督检测流程
# ---------------------------
class UnsupervisedDetector:
    def __init__(self):
        self.embedder = UnifiedEmbedder()  # 初始化正常
        self.detector = ZeroShotAIDetector()

    def analyze(self, texts):
        # 生成联合嵌入
        embeddings = self.embedder.embed(texts)

        # 降维可视化
        reducer = umap.UMAP(n_components=2)
        embeddings_2d = reducer.fit_transform(embeddings)

        # 聚类分析
        clusterer = HDBSCAN(min_cluster_size=5)
        clusters = clusterer.fit_predict(embeddings)

        # 异常检测
        from pyod.models.ecod import ECOD
        detector = ECOD()
        anomaly_scores = detector.fit_predict(embeddings)

        # 零样本AI概率
        ai_probs = self.detector.predict(texts)

        # 综合评分
        df = pd.DataFrame({
            "text": texts,
            "cluster": clusters,
            "anomaly_score": anomaly_scores,
            "ai_prob": ai_probs,
            "x": embeddings_2d[:,0],
            "y": embeddings_2d[:,1]
        })
        df["suspect_index"] = df["anomaly_score"] * 0.4 + df["ai_prob"] * 0.6

        return df

# ---------------------------
# 动态模式发现模块
# ---------------------------
class PatternDiscoverer:
    def __init__(self, top_n=10):
        self.top_n = top_n

    def discover(self, df):
        # 提取高嫌疑样本
        high_risk = df[df["suspect_index"] > 0.7]

        # 语义模式发现
        semantic_patterns = self._find_semantic_patterns(high_risk["text"])

        # 句法模式发现
        syntax_patterns = self._find_syntax_patterns(high_risk["text"])

        return {
            "semantic": semantic_patterns,
            "syntax": syntax_patterns
        }

    def _find_semantic_patterns(self, texts):
        # 使用KeyBERT提取关键词
        from keybert import KeyBERT
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(texts, keyphrase_ngram_range=(1,3))
        return [kw[0] for kw, _ in Counter([item for sublist in keywords for item in sublist]).most_common(self.top_n)]

    def _find_syntax_patterns(self, texts):
        """使用 nltk 的 RegexpParser 提取句法模式"""
        # 定义句法规则
        grammar = r"""
            AI_OPENING: {<DT><NNP>+<VBP><CD>}  # 匹配 "As a Ukrainian, I am 20..."
            ADJ_CLUSTER: {<JJ><,|CC><JJ>}      # 匹配形容词组合
        """
        parser = RegexpParser(grammar)
        
        # 匹配文本
        matches = defaultdict(int)
        for text in texts:
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            tree = parser.parse(pos_tags)
            
            for subtree in tree:
                if isinstance(subtree, nltk.Tree):
                    label = subtree.label()
                    matches[label] += 1
        
        return dict(matches)
    
if __name__ == "__main__":
    texts = [
        "Hardworking, I like to work in the garden, take care",
            "I, as a 22-year-old Ukrainian, am looking for a job in the hotel business and tourism. I will describe my personality: I am open to communication and sociable. I have a high level of organization and the ability to work in a team. European standards of service and quality are also important to me. My attitude to work is very serious. I always put my responsibilities first and make every effort to achieve results. I have high motivation and perseverance, which allows me to acquire new knowledge and skills. I also know how to effectively manage my time and prioritize tasks to achieve success. My favorite activities are related to hospitality and customer service. I enjoy interacting with people, helping them solve problems and making their stay enjoyable. I also appreciate the opportunity to learn new cultures and languages, which adds variety and interest to my work. In this field of employment, I intend to develop and work to achieve stability and high quality of service. I believe I can be a valuable asset to any hotel or travel company and look forward to the opportunity to prove my skills and abilities.",
            "Purposeful, I always meticulously perform the tasks assigned to me",
            "I like working in sales, creating content and advertising",
            "I am a purposeful person. I like communication with people. I like to draw and do creative crafts",
            "I am a doctor who works 14 hours a day at two jobs: at a McDonald's restaurant and in the reception department of my hospital. Because I simply do not have enough money to live on, which is paid by the state for medical activities, and I cannot ask or demand money from someone. I am a very responsible person with an excellent memory, intuition and sense of humor. I have a little cat at home that I rescued from the street and now I try to give her the best. I have one day off a week where I sleep a lot, eat delicious junk, and then sleep."
        ]

    # 无监督分析
    detector = UnsupervisedDetector()
    df = detector.analyze(texts)

    # 动态模式发现
    discoverer = PatternDiscoverer()
    patterns = discoverer.discover(df)

    print("高嫌疑文本特征:")
    print(df.sort_values("suspect_index", ascending=False).head())

    print("\n自动发现的语义模式:", patterns["semantic"])
    print("自动发现的句法模式:", patterns["syntax"])

    # 可视化
    import plotly.express as px
    fig = px.scatter(
        df, x='x', y='y',
        color='suspect_index',
        hover_data=['text'],
        title="文本分布可视化"
    )
    fig.show()