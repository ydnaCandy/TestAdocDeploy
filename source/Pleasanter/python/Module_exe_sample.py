import json
from Module.pleasanter_api import PleasanterConnector

# =================================================================
# インスタンス生成
# =================================================================

# ファイルを開いて読み込む
with open('pleasanter_connection_info.json', 'r', encoding='utf-8') as f:
    pl_conn_info:dict = json.load(f)

PL_ADDR: str = pl_conn_info["HOST"]["URL"]
API_KEY: str = pl_conn_info["HOST"]["APIKEY"]
default_paylaod: dict = {
    "ApiVersion": 1.1,
    "apiKey": API_KEY,
}


pl_exe = PleasanterConnector(
    pl_addr=PL_ADDR,
    api_key=API_KEY
)


# =================================================================
print("===エディットタブのカラムを取得")
req_edit_cols = pl_exe.get_columns_in_edit_tab(site_id="2")
grid_cols = req_edit_cols["ResponseData"]["EditColsList"]

print(grid_cols)

# =================================================================
print("===カラムのマッピング情報を取得")
mapping_dict = pl_exe.get_mapping_cols(site_id="2")
print(mapping_dict)


# =================================================================
print("===レコードIDの取得")
print(pl_exe.get_item_record_by_id_in_site(site_id="2", record_id="4"))
print(
    pl_exe.get_item_record_by_id_in_site(
        site_id="2",
        record_id="4",
        grid_columns=grid_cols
    )
)



# =================================================================
print("===データ送信")
insert_data = {
    'Title': 'aaaa',
    'Status': '100',
    "ClassHash": {
        "ClassA": "FromAPI",
        "ClassB": "FromAPI",
    },
}

pl_exe.insert_single_record(
    site_id="1",
    insert_data=insert_data,
)

# =================================================================
print("===データ更新")
update_data = {
    'Title': 'API',
    "ClassHash": {
        "ClassA": "UpdateScript",
    },
}

# レコード無し
pl_exe.update_single_record(
    record_id="6",
    update_data=update_data,
)