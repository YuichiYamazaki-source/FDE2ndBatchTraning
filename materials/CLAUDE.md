# Project Environment

## Python環境

**MinicondaのPythonを直接使うこと。**

Pythonスクリプトを実行する際は、以下を使用する:

```bash
/c/Users/yuila/miniconda3/python.exe <script.py>
```

または `-c` でワンライナー:

```bash
/c/Users/yuila/miniconda3/python.exe -c "import ..."
```

> `conda run -n base python -c` はWindowsのGit Bash上でマルチラインが使えないため非推奨。

## 利用可能なPDFライブラリ

- `pypdf` 6.7.1 (base環境にインストール済み)

### PDF読み込みの優先順位

| 方法 | 使いどころ | 備考 |
| --- | --- | --- |
| Claude Code の `Read` ツール | 通常はこれを使う | `pdftoppm` 未インストールのため **Windows環境では使用不可** |
| `pypdf` + Bash ツール | Windows環境でのPDF読み込み | 以下のコマンドを使う |

### Windows環境でのPDF読み込みコマンド（確定版）

Windowsのターミナル(Git Bash)では文字コード(cp932)の問題で日本語・特殊文字が
`UnicodeEncodeError` になるため、ASCII変換してから出力する。

```bash
/c/Users/yuila/miniconda3/python.exe -c "
from pypdf import PdfReader
reader = PdfReader('path/to/file.pdf')
out = []
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        out.append(f'=== Page {i+1} ===')
        out.append(text)
print('\n'.join(out).encode('ascii', 'replace').decode('ascii'))
"
```

> `encode('ascii', 'replace')` で変換できない文字を `?` に置換することで
> `UnicodeEncodeError` を回避している。内容の確認には支障なし。

### 注意事項

- `conda run -n base python -c` はWindowsのGit Bash上でマルチラインが使えないため非推奨
- `-c` のワンライナーは文字列を `"..."` で囲むため、内部の文字列は `'...'` を使うこと

## 教材PDFの場所

`materials/` ディレクトリ以下にカテゴリ別に整理されている:

- `Authentication_JavaScript/`
- `Captone/`
- `Introduction AI and Prompt Engineering/`
- `Pytest_JEST/`
- `React_assessment/`
- `React_pagenation/`
- `ReactEasier/`
- `ReactFirstStep/`

## Conda環境一覧

- `base`: `C:\Users\yuila\miniconda3` (メイン)
- `recognition`: `C:\Users\yuila\miniconda3\envs\recognition`
