import re
from typing import List

import nlpcloud
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sumy.summarizers.lsa import LsaSummarizer

client = nlpcloud.Client("bart-large-cnn", "ac937ad1e1b3dd41198339e389cb48eee4a16bd4")

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import names, stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('names')
nltk.download('stopwords')
nltk.download('wordnet')

class TextManager:
    def __init__(self, text: str):
        self.text = text
        self.summarizer = LsaSummarizer()
        self.known_names = set(names.words())

    def cluster_sentences(sentences, num_clusters=3):
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sentences)

        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)

        clustered_sentences = {i: [] for i in range(num_clusters)}
        for i, label in enumerate(clusters):
            clustered_sentences[label].append(sentences[i])

        return clustered_sentences

    def extract_sentences(self, text: str) -> List[str]:
        """Extracts and cleans meaningful sentences from text."""
        sentences = nltk.sent_tokenize(text)  # Melhor segmentação de frases

        cleaned_sentences = []
        for sentence in sentences:
            # Remove caracteres especiais, mantendo letras e espaços
            cleaned_sentence = re.sub(r'[^a-zA-Z\s]', '', sentence)
            cleaned_sentence = ' '.join(cleaned_sentence.split())  # Remove espaços extras

            # Ignorar frases que são apenas números ou que têm menos de 2 palavras
            if cleaned_sentence and not cleaned_sentence.isdigit() and len(cleaned_sentence.split()) > 1:
                cleaned_sentences.append(cleaned_sentence)

        return cleaned_sentences

    def preprocess_text(self, text: str) -> str:
        # 1. Remoção de caracteres especiais e pontuação
        text = re.sub(r'[^\w\s]', '', text)

        # 2. Conversão para minúsculas
        text = text.lower()

        # 3. Remoção de stopwords
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in stop_words]

        # 4. Lematização
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]

        # Juntar os tokens de volta em um texto
        preprocessed_text = ' '.join(tokens)

        return preprocessed_text

    def summarize_text(self, text: str) -> str:
        summary_dict = client.summarization(text)
        return summary_dict.get('summary_text', '')

    def extract_document_title(self) -> str:
        """Extract the title from the document text."""

        lines = self.text.strip().split("\n")  # Divide o texto em linhas e remove espaços extras

        # 1. Procurar por um título explícito com palavras-chave
        title_patterns = [
            r'(?i)^\s*(?:title|document title|report|heading|subject)[:\-]?\s*(.+)$'  # "Title: My Document"
        ]

        for line in lines[:10]:  # Verifica apenas as primeiras 10 linhas
            for pattern in title_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    return match.group(1).strip()

        # 2. Se não encontrou um título explícito, assume a primeira linha não vazia como título
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line and not re.match(r'^\d+$', cleaned_line):  # Ignora números isolados (ex: números de página)
                return cleaned_line

        return "Unknown Title"  # Se nada for encontrado

    def extract_document_subtitle(self) -> str:
        """Extract the subtitle from the document text."""

        lines = self.text.strip().split("\n")  # Divide o texto em linhas e remove espaços extras

        # Filtra as linhas removendo espaços e ignorando linhas vazias
        meaningful_lines = [line.strip() for line in lines if line.strip()]

        # 1. Procurar por um subtítulo explícito com palavras-chave
        subtitle_patterns = [
            r'(?i)^\s*(?:subtitle|abstract|summary|overview|description)[:\-]?\s*(.+)$'  # "Subtitle: My Subtitle"
        ]

        for line in meaningful_lines[:10]:  # Verifica apenas as primeiras 10 linhas
            for pattern in subtitle_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    return match.group(1).strip()

        # 2. Se não encontrar um subtítulo explícito, assume a segunda linha significativa como subtítulo
        return meaningful_lines[1] if len(meaningful_lines) > 1 else "Unknown Subtitle"

    def extract_author(self) -> str:
        """Extract the author from the document text, considering both individuals and companies."""

        lines = self.text.strip().split("\n")[:10]  # Verifica as primeiras 10 linhas do documento

        # 1. Padrões comuns para identificar autores
        author_patterns = [
            r'(?i)^\s*(?:author|autor|by|written by|company|organization|produced by)[:\-]?\s*(.+)$',
            r'(?i)^(.{3,50})$'  # Linha curta pode ser um nome ou empresa
        ]

        for line in lines:
            for pattern in author_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    return match.group(1).strip()

        # 2. Se não encontrou explicitamente, tenta identificar um nome próprio ou empresa
        for line in lines:
            words = word_tokenize(line)
            potential_names = [word for word in words if word.istitle() and word in self.known_names]

            # Se encontrar um nome próprio, retorna
            if potential_names:
                return " ".join(potential_names)

            # Se a linha contém siglas ou parece ser o nome de uma empresa
            if re.match(r'^[A-Z][A-Za-z0-9&\s]+(?:Ltd|Inc|Corp|LLC|SA|GmbH|Co|Group|Technologies|Systems)?$', line):
                return line.strip()

        return "Unknown Author"  # Se nada for encontrado
