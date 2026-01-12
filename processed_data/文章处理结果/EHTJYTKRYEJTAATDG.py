import re
import os
import string
from collections import Counter, defaultdict
from typing import List, Tuple, Dict, Set

class ArticleOrganizer:
    def __init__(self, lang='chinese'):
        self.lang = lang
        self.stopwords = self._get_stopwords()
        self.punctuation = string.punctuation.replace('-', '',)  # 保留连字符
        self.fullwidth_punct = {  # 全角标点映射
            '，': ',', '。': '.', '？': '?', '！': '!', '“': '"', '”': '"',
            '‘': "'", '’': "'", '：': ':', '；': ';', '（': '(', '）': ')'
        }
    
    def _get_stopwords(self) -> Set[str]:
        """中英文停用词表"""
        chinese_stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', 
            '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', 
            '着', '没有', '看', '好', '自己', '这', '那', '其', '此', '彼'
        ])
        english_stopwords = set([
            'a', 'an', 'the', 'in', 'on', 'at', 'for', 'to', 'of', 'is', 
            'are', 'was', 'were', 'be', 'been', 'am', 'as', 'and', 'or', 
            'but', 'not', 'this', 'that', 'these', 'those', 'i', 'you'
        ])
        return chinese_stopwords if self.lang == 'chinese' else english_stopwords
    
    def _convert_fullwidth(self, text: str) -> str:
        """全角标点转半角"""
        for full, half in self.fullwidth_punct.items():
            text = text.replace(full, half)
        return text
    
    def read_file(self, file_path: str) -> str:
        """读取文件（自动处理编码）"""
        for encoding in ['utf-8', 'gbk', 'latin-1', 'utf-16']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return self._convert_fullwidth(f.read())
            except:
                continue
        print(f"错误：无法解码文件 '{file_path}'")
        return ""
    
    def merge_files(self, file_paths: List[str]) -> str:
        """合并多个文件内容"""
        merged = []
        for path in file_paths:
            content = self.read_file(path)
            if content:
                merged.append(content)
        return "\n\n".join(merged)
    
    def clean_text(self, text: str) -> str:
        """深度文本清洗"""
        text = re.sub(r'<.*?>', '', text)  # 移除HTML标签
        text = re.sub(r'[^\w\s{}]'.format(re.escape(string.punctuation)), ' ', text)  # 保留合法标点
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower() if self.lang == 'english' else text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """智能句子分割（支持中英文）"""
        if self.lang == 'chinese':
            return re.split(r'([。？！])', text)
        return re.split(r'(?<=[.!?]) +', text)
    
    def detect_duplicate_sentences(self, text: str, threshold: float = 0.9) -> Dict[str, List[int]]:
        """基于词重叠的重复句检测"""
        sentences = [s for s in self.split_into_sentences(text) if s.strip()]
        cleaned = [self.clean_text(s) for s in sentences]
        duplicates = defaultdict(list)
        
        for i, s1 in enumerate(cleaned):
            if not s1:
                continue
            for j in range(i+1, len(cleaned)):
                sim = self._sentence_similarity(s1, cleaned[j])
                if sim >= threshold:
                    duplicates[i].append(j)
        
        result = {}
        for idx, refs in duplicates.items():
            original = sentences[idx]
            result[original] = [idx] + refs
        return result
    
    def _sentence_similarity(self, s1: str, s2: str) -> float:
        """句子相似度计算"""
        words1 = set(s1.split()) - self.stopwords
        words2 = set(s2.split()) - self.stopwords
        if not words1 and not words2:
            return 0.0
        return len(words1 & words2) / max(len(words1), len(words2), 1)
    
    def remove_duplicates(self, text: str, threshold: float = 0.9) -> str:
        """移除重复句，保留首现"""
        sentences = [s for s in self.split_into_sentences(text) if s.strip()]
        cleaned = [self.clean_text(s) for s in sentences]
        seen = set()
        unique = []
        
        for i, s in enumerate(cleaned):
            if s not in seen:
                seen.add(s)
                unique.append(sentences[i])
        return "".join(unique).strip()
    
    def organize_paragraphs(self, text: str, max_sentences: int = 5) -> str:
        """重组段落（按句子数分割）"""
        sentences = [s for s in self.split_into_sentences(text) if s.strip()]
        paragraphs = []
        for i in range(0, len(sentences), max_sentences):
            para = "".join(sentences[i:i+max_sentences])
            paragraphs.append(para)
        return "\n\n".join(paragraphs)
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[Tuple[str, int]]:
        """基于词频的关键词提取"""
        cleaned = self.clean_text(text)
        tokens = [word for word in cleaned.split() if word not in self.stopwords and len(word) > 1]
        return Counter(tokens).most_common(top_n)
    
    def process_article(self, input_paths: List[str], output_dir: str):
        """一站式处理流程"""
        # 合并文件
        merged_text = self.merge_files(input_paths)
        if not merged_text:
            print("错误：合并后的文本为空")
            return
        
        # 深度处理
        processed = {
            "merged_text": merged_text,
            "cleaned_text": self.clean_text(merged_text),
            "no_duplicates": self.remove_duplicates(merged_text),
            "organized": self.organize_paragraphs(merged_text),
            "keywords": self.extract_keywords(merged_text)
        }
        
        # 保存结果
        os.makedirs(output_dir, exist_ok=True)
        for key, content in processed.items():
            filename = os.path.join(output_dir, f"processed_{key}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(content, list):
                    f.write("\n".join([f"{w}:{c}" for w, c in content]))
                else:
                    f.write(content)
        print(f"处理完成，结果保存至 {output_dir}")
