# coding: utf-8

from enum import Enum


class AnswerRange(Enum):
    knowWithLlm = "knowWithLlm"
    knowOnly = "knowOnly"


class JoinType(Enum):
    num = "num"
    power = "power"


class SearchType(Enum):
    llm = "llm"
    fixed = "fixed"


class IsShowSource(Enum):
    show = 1
    notShow = 0


class EmbeddingType(Enum):
    BgeLarge = "bge-large-zh"
    BgeSmall = "bge-small-zh"


EMBEDDING_MAP = {
    "bge-large-zh": "ai_knowledge_base_large",
    "bge-small-zh": "ai_knowledge_base_small",
}


class FileSplitType(Enum):
    normal = 0  #普通处理
    qa = 1      #qa对，excel一问一答
