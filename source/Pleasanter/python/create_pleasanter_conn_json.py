import json

url = input("URL...")
apikey = input("APIKEY...")

if url != "" and apikey != "":
    ple_conn_info: dict = {
        "HOST": {
            "URL": url,
            "APIKEY": apikey
        },
        "SITES": {}
    }

    with open("pleasanter_connection_info.json","w") as f:
        json.dump(ple_conn_info, f, ensure_ascii=False, indent=4)

    print("Successfully")

else:
    print("Failed.")
