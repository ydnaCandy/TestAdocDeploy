import json
import requests
from typing import Optional,Tuple


class PleasanterConnector:
    def __init__(self, pl_addr: str , api_key: str) -> None:
        self.pl_addr: str = pl_addr
        self.api_key: str = api_key
        self.timeout: tuple = (3.0, 10.0)
        self.paylaod: dict = {
            "ApiVersion": 1.1,
            "apiKey": self.api_key,
        }

    def _handle_http_error(self, status_code: int) -> dict:
        """Handle non-200 HTTP status codes"""
        return {
            "Result": False,
            "ErrorMsg": {
                "ErrorType": str(status_code),
                "Message": "HTTP Request Error"
            }
        }

    def _process_request(self, api_url:str, payload:dict) -> dict:
        """Common process request to Pleasanter API"""
        try:
            # APIにリクエストを送信
            request_post = requests.post(
                api_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json', 'charset': 'UTF-8'},
                timeout=self.timeout
            )

            # HTTPレスポンスの判定
            if request_post.status_code != 200:
                # 200以外のレスポンス
                return self._handle_http_error(request_post.status_code)

            else:
                # レスポンスをjson形式に変換
                data: dict = request_post.json()

                # 返り値を作成
                response_dict: dict = {
                    "Result": True,
                }

                # Responseキーがある場合は返り値に含める
                if "Response" in data.keys():

                    # Responseにデータがある場合は返り値に含める
                    if "Data" in data["Response"].keys() :
                        response_dict["ResponseData"] = data["Response"]["Data"]

                    # オフセット位置なども取得
                    if "Offset" in data["Response"].keys() :
                        response_dict["Offset"] = data["Response"]["Offset"]

                    if "PageSize" in data["Response"].keys() :
                        response_dict["PageSize"] = data["Response"]["PageSize"]

                    if "TotalCount" in data["Response"].keys() :
                        response_dict["TotalCount"] = data["Response"]["TotalCount"]

                # 返り値を作成
                return response_dict

        # タイムアウト
        except requests.exceptions.ConnectTimeout as e:
            return {
                "Result": False,
                "ErrorMsg": {
                    "ErrorType":str(type(e)),
                    "Message":"Timeout Error"
                }
            }

        # 接続エラー
        except requests.exceptions.ConnectionError as e:
            return {
                "Result": False,
                "ErrorMsg": {
                    "ErrorType":str(type(e)),
                    "Message":"Connection Error"
                }
            }

        # 想定外エラー
        except Exception as e:
            return {
                "Result": False,
                "ErrorMsg": {
                    "ErrorType":str(type(e)),
                    "Message":"Unexcepted Error"
                }
            }

    def get_mapping_cols(self, site_id: str) -> dict:
        """This function gets the default column names and display column names of Pleasenter as key-value pairs.
        """
        
        # URLを作成
        url = self.pl_addr + "api/items/" + str(site_id) + "/getsite"

        # APIにリクエストするデータを作成
        payload: dict = self.paylaod

        # リクエスト実行
        response_dict = self._process_request(
            api_url=url,
            payload=payload
        )

        # リクエストの判定
        if response_dict["Result"]:
            # 対象IDがサイトかどうかの確認
            if response_dict["ResponseData"]["ReferenceType"] in ["Results", "Issues"]:
                # デフォルト名と表示名を取得
                mapping_cols = {
                    "CreatedTime": "CreatedTime",
                    "UpdatedTime": "UpdatedTime",
                    "Updator": "Updator",
                    "Creator": "Creator",
                }
                for col_dict in response_dict["ResponseData"]["SiteSettings"]["Columns"]:
                    mapping_cols[col_dict["ColumnName"]] = col_dict["LabelText"]

                return {
                    "Result": True,
                    "ResponseData": {
                        "MappingColsDict": mapping_cols
                    }
                }

            elif response_dict["ResponseData"]["ReferenceType"] == "Sites":
                # ディレクトリサイトがsite_idとして指定されたらNGを返す
                return {
                    "Result": False,
                    "ErrorMsg": {
                        "ErrorType": "Uncorrect site id.",
                        "Message": "This id is directly site id."
                    }
                }

            else:
                # 想定外のエラー
                return {
                    "Result": False,
                    "ErrorMsg": {
                        "ErrorType": "Unexpected.",
                        "Message": "Successfully response. But Unexpected ReferenceType."
                    }
                }

        # リクエスト送信時のエラー
        else:
            return response_dict

    def get_columns_in_edit_tab(self, site_id: str) -> dict:
        """This function gets GridColumn for the edit tab.
        """
        
        # URLを作成
        url = self.pl_addr + "api/items/" + str(site_id) + "/getsite"

        # pleasanter標準のカラムで使用するカラムを指定
        default_cols: list = ['CreatedTime', 'UpdatedTime', "Creator", "Updator"]

        # APIにリクエストするデータを作成
        payload: dict = self.paylaod

        response_dict = self._process_request(
            api_url=url,
            payload=payload
        )

        # リクエストの判定
        if response_dict["Result"]:
            # 対象IDがサイトかどうかの確認
            if response_dict["ResponseData"]["ReferenceType"] in ["Results", "Issues"]:
                # エディットタブで使用されているカラムを取得
                col_list: list = response_dict["ResponseData"]["SiteSettings"]["EditorColumnHash"]["General"]
                # デフォルトカラムで使用するカラム名を追加
                col_list.extend(default_cols)
                # 結果の出力
                return {
                    "Result": True,
                    "ResponseData": {
                        "EditColsList": col_list
                    }
                }

            elif response_dict["ResponseData"]["ReferenceType"] == "Sites":
                # ディレクトリサイトがsite_idとして指定されたらNGを返す
                return {
                    "Result": False,
                    "ErrorMsg": {
                        "ErrorType": "Uncorrect site id.",
                        "Message": "This id is directly site id."
                    }
                }

            else:
                # 想定外のエラー
                return {
                    "Result": False,
                    "ErrorMsg": {
                        "ErrorType": "Unexpected.",
                        "Message": "Successfully response. But Unexpected ReferenceType."
                    }
                }

        # リクエスト送信時のエラー
        else:
            return response_dict

    def get_item_record_by_id_in_site(
            self,
            site_id: str,
            record_id: str,
            grid_columns: Optional[list] = None,
        ) -> dict:
        """return dict(result request and data)
        Args:
        - grid_columns: 
            - List the column names you want to retrieve.
            - default: None
        """
        # site_idとrecord_idに同じ値がセットされた
        if site_id == record_id:
            return  {
                "Result": False,
                "ErrorMsg": {
                    "ErrorType": "The ID is invalid.",
                    "Message": "The same value has been specified for both the record ID and the site ID."
                }
            }

        # payloadを作成
        payload: dict = self.paylaod
        payload.update({
            "View": {
                # Pleasanter上の表示名で取得
                "ApiDataType": "KeyValues",
                # グリッドカラムの指定
                "GridColumns": grid_columns
            }
        })

        # URLを作成
        url = self.pl_addr + "api/items/" + str(record_id) + "/get"

        # リクエスト実行
        response_dict = self._process_request(
            api_url=url,
            payload=payload
        )

        # レスポンスの処理
        if response_dict['Result']:
            # リストかつリストの要素が1つであればレコードIDが指定されている
            if isinstance(response_dict["ResponseData"], list) and len(response_dict["ResponseData"]) == 1:
                result_dict: dict = {
                    "Result": True,
                    "ResponseData": response_dict["ResponseData"]
                }
                return result_dict

            # リスト以外もしくはレコードIDが複数行ある
            else:
                result_dict: dict = {
                    "Result": False,
                    "ErrorMsg": {
                        "ErrorType": "The provided ID is incorrect.",
                        "Message": "The provided ID is site id or folder id."
                    }
                }
                return result_dict

        else:
            # エディットカラム取得時のリクエストのエラー
            return response_dict

    def setup_search_type(self, cols: list, search_type:str) -> dict:
        """This function setup searchtype for pleasnater api
        Args:
        - cols: 
            - Set list to want to setup search type
        - search_type: 
            - Single:
                - ExactMatch or PartialMatch or ForwardMatch
            - Multi
                - ExactMatchMultiple or PartialMatchMultiple or ForwardMatchMultiple
        - reference
            - https://pleasanter.org/ja/manual/api-view
        """
        setup_dict: dict = {}

        for col in cols:
            setup_dict[col] = search_type

        return {
            "Result": True,
            "ResponseData": setup_dict
        }

    def get_item_records(
            self,
            site_id: str,
            grid_columns: Optional[list] = None,
            view_filters: Optional[dict] = None,
            search_type_filters: Optional[dict] = None,
        ) -> dict:
        """This function gets records.
        Args:
        - grid_columns:
        - view_filters: 
        - search_type_filters:
        """

        # 初期値を設定
        offset: int = 0
        page_size: int = 200
        total_count: int = 1
        records: list = []

        # URLを作成
        url = self.pl_addr + "api/items/" + str(site_id) + "/get"

        # payloadを作成
        payload: dict = self.paylaod
        payload.update({
            "View": {
                # Pleasanter上の表示名で取得
                "ApiDataType": "KeyValues",
                # 検索条件の指定
                "ColumnFilterHash": view_filters,
                # 検索条件の一致方式の指定
                "ColumnFilterSearchTypes": search_type_filters,
                # グリッドカラムを指定
                "GridColumns": grid_columns,
            }
        })

        # 一度に取得できる件数が200と仕様で決まっているのでループする
        while offset < total_count:

            # オフセット位置を指定
            payload["Offset"] = offset

            # リクエスト実行
            response_dict = self._process_request(
                api_url=url,
                payload=payload
            )

            # レスポンスの処理
            if response_dict['Result']:

                # 対象IDがフォルダの場合、辞書型で返ってくるのでNG
                if isinstance(response_dict["ResponseData"],dict):
                    error_msg:dict = {
                        "Result": True,
                        "ErrorMsg": {
                            "ErrorType": "The provided ID is incorrect.",
                            "Message": "The provided ID is folder id."
                        }
                    }
                    return (False, error_msg)

                # データがリストであればレコードが取得できている
                elif isinstance(response_dict["ResponseData"], list):
                    # レコード数とページサイズを取得
                    total_count = response_dict['TotalCount']
                    page_size = response_dict['PageSize']
                    # レコードを取得
                    for data in response_dict['ResponseData']:
                        records.append(data)
                    # offsetをインクリメントする
                    offset = offset + page_size

            # すべての行を取得し終えたら値を返す
            result_dict: dict = {
                "Result": True,
                "ResponseData": records
            }
            return result_dict

        else:
            # リクエスト失敗
            return response_dict


    def insert_single_record(
            self,
            site_id: str,
            insert_data: dict,
        ) -> dict:
        """This function inserts a single record.
        Args:
        - grid_columns:
        - view_filters: 
        - search_type_filters:
        """

        # TODO: 指定したsite_idがテーブル内のレコードでもデータ送信できてしまう。

        # URLを作成
        url = self.pl_addr + "api/items/" + str(site_id) + "/create"

        # APIにリクエストするデータを作成
        payload: dict = self.paylaod

        # 送信データをPayloadに含める
        payload.update(insert_data)

        # リクエスト実行
        response_dict = self._process_request(
            api_url=url,
            payload=payload
        )

        # リクエストの判定
        if response_dict["Result"]:
            # Trueであればデータ送信できている
            # 結果の出力
            return {
                "Result": True,
            }

        # リクエスト送信時のエラー
        else:
            return response_dict

    def update_single_record(
            self,
            record_id: str,
            update_data: dict,
        ) -> dict:
        """This function updates a single record.
        Args:
        - grid_columns:
        - view_filters: 
        - search_type_filters:
        """

        # URLを作成
        url = self.pl_addr + "api/items/" + str(record_id) + "/update"

        # APIにリクエストするデータを作成
        payload: dict = self.paylaod

        # 送信データをPayloadに含める
        payload.update(update_data)

        # リクエスト実行
        response_dict = self._process_request(
            api_url=url,
            payload=payload
        )

        # リクエストの判定
        if response_dict["Result"]:
            # Trueであればデータ送信できている
            # 結果の出力
            return {
                "Result": True,
            }

        # リクエスト送信時のエラー
        else:
            return response_dict