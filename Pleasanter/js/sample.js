// APIURLとtokenは本来は秘匿する
const url = "http://192.168.3.101:13500/api/items/" + "6" + "/get";
const token =
  "134f666431808f6734f54bf4b13bd46650412c294929c06613590adc8f335466197adeb4fd3fbf4730adb4fceeb8b84f881c89ffdd2773b63e98bb7197bffd3f";
// ヘッダー
const headers = new Headers({
  "Content-Type": "application/json",
  charset: "UTF-8",
});
// body
const body = JSON.stringify({
  ApiVersion: 1.1,
  apiKey: token,
});
// 処理の埋め込み
document.getElementById("fetchData").addEventListener("click", () => {
  // API実行
  fetch(url, { method: "POST", headers, body })
    .then((response) => {
      if (!response.ok) {
        // レスポンス失敗時はエラーを起こす
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      // 取得したレスポンスの表示
      console.log("Created:", data);
      // 取得した要素をバラす
      console.log(data.Response.Data[0]);
      // データをhtmlに表示する
      const output = document.getElementById("output");
      output.innerHTML = JSON.stringify(data.Response, null, 2);
    })
    .catch((error) => console.error("Error:", error));
});
// 🔽 リセットボタンの処理を追加
document.getElementById("reset").addEventListener("click", () => {
  const output = document.getElementById("output");
  output.textContent = "読み込み中..."; // ← 初期状態に戻す
});
