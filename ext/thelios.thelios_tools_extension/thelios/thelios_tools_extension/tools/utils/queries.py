import pyodbc
from ... import constants

def pop_combo_brands(db_key):
    
    conn = pyodbc.connect(db_key)
    cur = conn.cursor()
    
    query_rel_sku = f"SELECT DISTINCT [Brand] FROM {constants.RENDER_STYLE_TABLE} "
    cur.execute(query_rel_sku)
    res = cur.fetchall() 
    conn.close()
    
    res_list = [tup[0] for tup in res]
    brands = list(set(res_list))
    brands_sorted = sorted(brands)
    
    return brands_sorted

def get_plm_data(db_key, season, brand, category):
    
    #Connect to PLM DB
    conn = pyodbc.connect(db_key)
    cur = conn.cursor()
    #Split category field
    new_category = category.split( " - ")[0]
    new_genre = category.split( " - ")[1]
    
    #Convert gender to M/F
    if new_genre == "Man": 
        new_genre = "M"
    elif new_genre == "Woman":
        new_genre = "F"
        
    print(new_category)
    print(new_genre)
    print(brand)
    
    #Query to get all models, skus for the selected season, brand, category, gender
    query_rel_sku = f"""SELECT [Style], [Colorway] 
                        FROM {constants.RENDER_STYLE_TABLE} 
                        WHERE [Season] = '{season}'
                            AND [Brand] = '{brand}' 
                            AND [Category] = '{new_category}' 
                            AND [Gender] = '{new_genre}'
                    """
    cur.execute(query_rel_sku)
    res = cur.fetchall()
    conn.close()
    
    def transform_list(input_list):
        #Create a dictionary to store the result
        result = {}
        
        #Iterate over the input list and update the dictionary
        for key, value in input_list:
            if key not in result:
                result[key] = set()
            result[key].add(value)
        
        #Convert the dictionary back to a list of tuples
        return [(key, *sorted(values)) for key, values in result.items()]
    
    #Final tuple list and length of slides to create
    remove_dup = transform_list(res)
    
    return remove_dup

#print(get_plm_data(db_key, season, brand, category))

def get_sku_model_plm(db_key, model):
    #Connect to PLM DB
    conn = pyodbc.connect(db_key)
    cur = conn.cursor()
    
    query_rel_sku = f"""SELECT [Colorway], [Season], [Style_Name] 
                        FROM {constants.RENDER_STYLE_TABLE} 
                        WHERE [Style] = '{model}'
                    """
    cur.execute(query_rel_sku)
    res = cur.fetchall()
    conn.close()
    return res