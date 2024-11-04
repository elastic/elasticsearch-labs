import pandas as pd

from elasticsearch_connection import ElasticsearchConnection

es_client = ElasticsearchConnection().get_client()

term = "seafood for grilling"
size = 5


def format_text(description, line_length=120):
    words = description.split()
    if len(words) <= line_length:
        return description
    else:
        return " ".join(words[:line_length]) + "..."


def search_semantic(term):
    result = []
    response = es_client.search(
        index="grocery-catalog-elser",
        size=size,
        source_excludes="description_embedding",
        query={"semantic": {"field": "description_embedding", "query": term}},
    )

    for hit in response["hits"]["hits"]:
        score = hit["_score"]
        name = format_text(hit["_source"]["name"], line_length=10)
        description = hit["_source"]["description"]
        formatted_description = format_text(description)
        result.append(
            {
                "score": score,
                "name": name,
                "description": formatted_description,
            }
        )
    return result


def search_lexical(term):
    result = []
    response = es_client.search(
        index="grocery-catalog-elser",
        size=size,
        source_excludes="description_embedding",
        query={"multi_match": {"query": term, "fields": ["name", "description"]}},
    )

    for hit in response["hits"]["hits"]:
        score = hit["_score"]
        name = format_text(hit["_source"]["name"], line_length=10)
        description = hit["_source"]["description"]
        result.append(
            {
                "score": score,
                "name": name,
                "description": description,
            }
        )
    return result


if __name__ == "__main__":
    rs1 = search_semantic(term)
    rs2 = search_lexical(term)

    df1 = (
        pd.DataFrame(rs1)[["name", "score"]]
        if rs1
        else pd.DataFrame(columns=["name", "score"])
    )
    df2 = (
        pd.DataFrame(rs2)[["name", "score"]]
        if rs2
        else pd.DataFrame(columns=["name", "score"])
    )
    df1 = (
        pd.DataFrame(rs1)[["name", "score"]]
        if rs1
        else pd.DataFrame(columns=["name", "score"])
    )
    df1["Search Type"] = "Semantic"

    df2 = (
        pd.DataFrame(rs2)[["name", "score"]]
        if rs2
        else pd.DataFrame(columns(["name", "score"]))
    )
    df2["Search Type"] = "Lexical"

    tabela = pd.concat([df1, df2], axis=0).reset_index(drop=True)

    tabela = tabela[["Search Type", "name", "score"]]

    tabela.columns = ["Search Type", "Name", "Score"]

    tabela["Search Type"] = tabela["Search Type"].astype(str).str.ljust(0)
    tabela["Name"] = tabela["Name"].astype(str).str.ljust(15)
    tabela["Score"] = tabela["Score"].astype(str).str.ljust(5)

    print(tabela.to_string(index=False))
