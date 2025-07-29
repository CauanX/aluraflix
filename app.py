from notion_client import Client

notion = Client(auth="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")
atendimento_database_id = "224fee17740a81028f14d4d444f26a9b"
faturamento_database_id = "229fee17740a80a5b4a9ff4885061e6d"

def obtain_atedimentos_pages(database_id):
    pages = []
    cursor = None
    

    while True:
        filtro = {
        "and": [
            {
                "property": "Status",
                "status": {
                "equals": "Concluído"
                }
            },
            {
                "property": "Faturamento",
                "relation": {
                    "is_empty": True
                }
            },
            {
                "property": "Cliente",
                "relation": {
                    "is_not_empty": True
                }
            },
            {
                "property": "Data de Conclusão",
                "date": {
                    "is_not_empty": True
                }
            }
        ]
        }
        if cursor:
            response = notion.databases.query(
                database_id=database_id,
                start_cursor=cursor,
                filter = filtro
            )    
        else:
            response = notion.databases.query(
                database_id=database_id,
                        filter = filtro
            )

        pages.extend(response["results"])

        if response.get("has_more"):
            cursor = response["next_cursor"]
        else:
            break
        
    return pages
def obtain_faturamento_pages(database_id):
    pages = []
    cursor = None

    while True:
        filtro = {
            "and": [
                {
                    "property": "Cliente",
                    "relation": {
                        "is_not_empty": True
                    }
                }
            ]
        }
        if cursor:
            response = notion.databases.query(
                database_id=database_id,
                start_cursor=cursor,
                filter=filtro
            )    
        else:
            response = notion.databases.query(
                database_id=database_id,
                filter=filtro
            )

        pages.extend(response["results"])

        if response.get("has_more"):
            cursor = response["next_cursor"]
        else:
            break
        
    return pages
def faturamento_automation(atendimento_pages, faturamento_pages):
    for atendimento_page in atendimento_pages:
        atendimento_id = atendimento_page["id"]
        atendimento_props = atendimento_page["properties"]
        atendimento_title = atendimento_props["Nome do Solicitante"]["title"]
        atendimento_name = atendimento_title[0]["plain_text"] if atendimento_title else "(sem nome)"
        status = atendimento_props["Status"]["status"]["name"]
        date = atendimento_props["Data de Conclusão"]["date"]["start"]
        faturamento = atendimento_props["Faturamento"]["relation"]
        atendimento_cliente = atendimento_props["Cliente"]["relation"][0]["id"]
        yyyymm_date = date[:7].replace("-", "")
        if status == "Concluído":
            for faturamento_page in faturamento_pages:
                faturamento_id = faturamento_page["id"]
                faturamento_props = faturamento_page["properties"]
                faturamento_title = faturamento_props["Fatura"]["title"]
                faturamento_name = faturamento_title[0]["plain_text"] if faturamento_title else "(sem nome)"
                faturamento_cliente = faturamento_props["Cliente"]["relation"][0]["id"]
                yyyymm_fat = faturamento_name[3:11].replace("-", "")
                if yyyymm_date == yyyymm_fat and atendimento_cliente == faturamento_cliente:
                    notion.pages.update(
                        page_id=atendimento_id,
                        properties= {
                            "Faturamento": {
                                "relation": [
                                    {"id": faturamento_id}
                                ]
                            }
                        }
                    )
                    print(f"O chamado {atendimento_name} foi atribuído a {faturamento_name}")
                    break
                        
atendimento_pages = obtain_atedimentos_pages(atendimento_database_id)
faturamento_pages = obtain_faturamento_pages(faturamento_database_id)
faturamento_automation(atendimento_pages, faturamento_pages)

    