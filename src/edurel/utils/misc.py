import edurel.utils.llm as llmu
import edurel.utils.duckdb as ddbu

def text2sql(no, question, model, schema, con):
    print(f"{no}:{question}")
    sql = llmu.chat_text_to_sql(model, schema, question)
    print(sql)
    ddbu.sql_print(con, sql)

