import json
import re
import ollama


class OllamaProcessor:
    """Classe para processar texto usando modelos do Ollama"""

    def __init__(self, model_name="llama3"):
        """
        Inicializa o processador Ollama

        Args:
            model_name (str): Nome do modelo Ollama a ser usado
        """
        self.model_name = model_name

    def clean_and_structure_text(self, text):
        """
        Usa o Ollama para limpar e estruturar texto mal formatado

        Args:
            text (str): Texto extraído do PDF

        Returns:
            str: Texto limpo e estruturado
        """
        prompt = f"""
        Por favor, limpe e estruture o seguinte texto extraído de um PDF. 
        O texto está mal formatado com quebras de linha incorretas e espaços extras.

        TEXTO:
        {text}

        Por favor retorne o texto limpo e bem formatado, mantendo a estrutura de seções e parágrafos.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            cleaned_text = response['message']['content']
            return cleaned_text
        except Exception as e:
            print(f"Erro ao usar Ollama para limpar texto: {e}")
            # Retorna o texto original se houver erro
            return text

    def analyze_document_structure(self, text):
        """
        Usa o Ollama para analisar a estrutura do documento e retornar metadados e seções

        Args:
            text (str): Texto do documento

        Returns:
            dict: Estrutura com metadados e seções do documento
        """
        prompt = f"""
        Analise este documento e extraia sua estrutura. Identifique título, subtítulo, versão, data e as seções.
        Para cada seção, identifique título e pontos principais.

        DOCUMENTO:
        {text[:8000]}  # Limitando para evitar tokens muito longos

        Retorne o resultado como um objeto JSON com a seguinte estrutura:
        {{
            "title": "Título do documento",
            "subtitle": "Subtítulo se existir",
            "version": "Versão se mencionada",
            "date": "Data se mencionada",
            "sections": [
                {{
                    "title": "Nome da Seção 1",
                    "content": ["Ponto 1", "Ponto 2", "..."]
                }},
                {{
                    "title": "Nome da Seção 2",
                    "content": ["Ponto 1", "Ponto 2", "..."]
                }}
            ]
        }}

        Não inclua explicações extras, apenas o JSON.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])

            # Verifica se a resposta está vazia
            if not response or 'message' not in response or not response['message'].get('content'):
                raise ValueError("Resposta da API Ollama está vazia ou inválida.")

            result = response['message']['content']

            # Extrair o JSON da resposta (pode estar envolto em ```json ```)
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
            if json_match:
                result = json_match.group(1)

            # Limpar qualquer texto antes ou depois do JSON
            result = re.sub(r'^[^{]*', '', result)  # Remove texto antes do {
            result = re.sub(r'[^}]*$', '', result)  # Remove texto depois do }

            # Parse do JSON
            structure = json.loads(result)
            return structure
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            print(f"Resposta recebida: {response['message']['content']}")
            return {
                "title": "Documento Extraído",
                "subtitle": "",
                "version": "",
                "date": "",
                "sections": []
            }
        except Exception as e:
            print(f"Erro ao analisar estrutura com Ollama: {e}")
            return {
                "title": "Documento Extraído",
                "subtitle": "",
                "version": "",
                "date": "",
                "sections": []
            }

    def generate_slide_content(self, section_text, section_title):
        """
        Usa o Ollama para gerar conteúdo de slide a partir do texto de uma seção

        Args:
            section_text (str): Texto da seção
            section_title (str): Título da seção

        Returns:
            list: Lista de pontos para o slide
        """
        prompt = f"""
        Crie conteúdo para um slide de PowerPoint com base no seguinte texto da seção "{section_title}".
        Extraia 3-5 pontos principais que sejam claros e concisos.

        TEXTO DA SEÇÃO:
        {section_text}

        Retorne apenas os pontos, um por linha, sem numeração ou marcadores.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])

            content = response['message']['content']

            # Divide o conteúdo em linhas e limpa
            points = [line.strip() for line in content.split('\n') if line.strip()]

            # Remove marcadores ou números se existirem
            cleaned_points = []
            for point in points:
                # Remove marcadores comuns e números
                point = re.sub(r'^[\*\-•\d]+[\.\)]\s*', '', point)
                if point:
                    cleaned_points.append(point)

            return cleaned_points
        except Exception as e:
            print(f"Erro ao gerar conteúdo de slide com Ollama: {e}")
            # Se houver erro, divide o texto em frases
            sentences = re.split(r'[.!?]+', section_text)
            # Seleciona até 5 frases não vazias
            return [s.strip() for s in sentences if len(s.strip()) > 20][:5]
