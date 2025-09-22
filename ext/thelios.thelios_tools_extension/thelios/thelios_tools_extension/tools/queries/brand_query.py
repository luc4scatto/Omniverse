import pyodbc

def pop_combo_brands(db_key):
    
    conn = pyodbc.connect(db_key)
    cur = conn.cursor()
    
    query_rel_sku = f"SELECT DISTINCT [Brand] FROM [ReportDB].[dbo].[render_style_sku]"
    cur.execute(query_rel_sku)
    res = cur.fetchall() 
    conn.close()
    
    res_list = [tup[0] for tup in res]
    brands = list(set(res_list))
    brands_sorted = sorted(brands)
    
    return brands_sorted