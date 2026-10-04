# もふもふ不動産 RSS

`https://mofmof-investor.com/column/` をRSS化し、GitHub Actionsで1時間ごとに更新します。

## 初回設定
1. GitHubで新しいPublicリポジトリを作成。
2. このZIPの中身をリポジトリへアップロード。
3. Settings → Pages → Source を `GitHub Actions` に設定。
4. Actions → Update RSS → Run workflow を一度実行。
5. `https://ユーザー名.github.io/リポジトリ名/rss.xml` をFeedlyに追加。
