from enum import Enum

from operategpt.embeddings.string_embedding import StringEmbedding
from operategpt.embeddings.url_embedding import URLEmbedding


class KnowledgeType(Enum):
    DOCUMENT = "DOCUMENT"
    URL = "URL"
    TEXT = "TEXT"
    OSS = "OSS"
    S3 = "S3"
    NOTION = "NOTION"
    MYSQL = "MYSQL"
    TIDB = "TIDB"
    CLICKHOUSE = "CLICKHOUSE"
    OCEANBASE = "OCEANBASE"
    ELASTICSEARCH = "ELASTICSEARCH"
    HIVE = "HIVE"
    PRESTO = "PRESTO"
    KAFKA = "KAFKA"
    SPARK = "SPARK"
    YOUTUBE = "YOUTUBE"


def get_knowledge_embedding(
    knowledge_type, knowledge_source, vector_store_config, source_reader, text_splitter
):
    match knowledge_type:
        case KnowledgeType.URL.value:
            embedding = URLEmbedding(
                file_path=knowledge_source,
                vector_store_config=vector_store_config,
                source_reader=source_reader,
                text_splitter=text_splitter,
            )
            return embedding
        case KnowledgeType.TEXT.value:
            embedding = StringEmbedding(
                file_path=knowledge_source,
                vector_store_config=vector_store_config,
                source_reader=source_reader,
                text_splitter=text_splitter,
            )
            return embedding
        case KnowledgeType.DOCUMENT.value:
            raise Exception("DOCUMENT have not integrate")
        case KnowledgeType.OSS.value:
            raise Exception("OSS have not integrate")
        case KnowledgeType.S3.value:
            raise Exception("S3 have not integrate")
        case KnowledgeType.NOTION.value:
            raise Exception("NOTION have not integrate")
        case KnowledgeType.MYSQL.value:
            raise Exception("MYSQL have not integrate")
        case KnowledgeType.TIDB.value:
            raise Exception("TIDB have not integrate")
        case KnowledgeType.CLICKHOUSE.value:
            raise Exception("CLICKHOUSE have not integrate")
        case KnowledgeType.OCEANBASE.value:
            raise Exception("OCEANBASE have not integrate")
        case KnowledgeType.ELASTICSEARCH.value:
            raise Exception("ELASTICSEARCH have not integrate")
        case KnowledgeType.HIVE.value:
            raise Exception("HIVE have not integrate")
        case KnowledgeType.PRESTO.value:
            raise Exception("PRESTO have not integrate")
        case KnowledgeType.KAFKA.value:
            raise Exception("KAFKA have not integrate")
        case KnowledgeType.SPARK.value:
            raise Exception("SPARK have not integrate")
        case KnowledgeType.YOUTUBE.value:
            raise Exception("YOUTUBE have not integrate")
        case _:
            raise Exception("unknown knowledge type")
