# Phase 3 — React フロントエンド変更解説

Phase 3 で行った React コードの変更を、学習ポイントとともに解説する。

---

## 1. 画像プロキシ — CDN ブロック対策

### 問題

商品画像の URL は Walmart CDN (`i5.walmartimages.com`) を指しているが、
ブラウザから直接アクセスすると **リファラー/CORS ポリシー** でブロックされ画像が表示されない。

### 解決策: バックエンドプロキシ

ブラウザ → FastAPI バックエンド → Walmart CDN の順でリクエストを中継する。

```
[Browser]  --GET /api/image-proxy?url=https://i5...--> [FastAPI]  --GET--> [Walmart CDN]
           <-- image/jpeg response --                              <-- image data --
```

### バックエンド側 (`backend/routers/images.py`)

```python
import httpx
from fastapi import APIRouter, Query
from fastapi.responses import Response

router = APIRouter(prefix="/api", tags=["images"])
_client = httpx.AsyncClient(follow_redirects=True, timeout=10.0)

@router.get("/image-proxy")
async def image_proxy(url: str = Query(...)):
    # セキュリティ: Walmart URL のみ許可
    if not url.startswith("https://i5.walmartimages.com/"):
        return Response(status_code=400, content=b"Only Walmart image URLs allowed")

    resp = await _client.get(url)
    return Response(
        content=resp.content,
        media_type=resp.headers.get("content-type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},  # 24h キャッシュ
    )
```

**学習ポイント**:
- `httpx.AsyncClient` は FastAPI の async エンドポイントと相性が良い
- `follow_redirects=True` でリダイレクトに対応
- URL のホワイトリストチェックで **SSRF (Server-Side Request Forgery)** を防止
- `Cache-Control` ヘッダーでブラウザキャッシュを有効にし、同じ画像の再取得を防ぐ

### フロントエンド側 (`frontend/src/api/client.js`)

```javascript
export function proxyImageUrl(url) {
  if (!url) return null
  const clean = url.replace(/^"|"$/g, '')  // DB に入った余分な引用符を除去
  if (clean.startsWith('https://i5.walmartimages.com/')) {
    return `${BASE_URL}/image-proxy?url=${encodeURIComponent(clean)}`
  }
  return clean  // Walmart 以外の URL はそのまま返す
}
```

**学習ポイント**:
- `encodeURIComponent()` — URL をクエリパラメータに埋め込むときは必ずエンコードする。`?` や `&` がパラメータ区切りと誤解されるのを防ぐ
- 正規表現 `/^"|"$/g` — 文字列の先頭・末尾にある `"` を除去。DB に `"https://..."` と格納されていたため必要

### コンポーネントでの使用 (`ProductCard.jsx` / `ProductDetail.jsx`)

```jsx
// Before (CDN ブロックされる)
<img src={main_image} alt={product_name} />

// After (プロキシ経由)
import { proxyImageUrl } from '../api/client'
<img src={proxyImageUrl(main_image)} alt={product_name} />
```

**学習ポイント**:
- ヘルパー関数を `api/client.js` に集約することで、画像 URL の変換ロジックが 1 箇所にまとまる（DRY 原則）
- 複数コンポーネント (`ProductCard`, `ProductDetail`) で同じ関数を import して使い回す

---

## 2. JSON データの見やすい表示 — ProductDetail.jsx

### 問題

`specifications`, `colors`, `customer_reviews` フィールドは **JSON 文字列** として DB に格納されている。
そのまま表示すると `[{"name":"Weight","value":"4 oz"},...]` のような生データが画面に出る。

### データ形式

```javascript
// specifications — キーバリューペアの配列
'[{"name":"Assembled Product Weight","value":"4 oz"},{"name":"Brand","value":"PhoLicious"}]'

// colors — 文字列の配列
'["Blue","Pink"]'

// customer_reviews — レビューオブジェクトの配列
'[{"name":"John","rating":5,"review":"Great product!","title":"Love it"}]'
```

### 解決策: フィールド別の専用コンポーネント

#### 共通ヘルパー: `tryParseJson()`

```javascript
function tryParseJson(data) {
  if (Array.isArray(data)) return data           // 既にパース済みならそのまま
  if (typeof data !== 'string') return null       // 文字列でなければ null
  try { return JSON.parse(data) } catch { return null }  // パース失敗しても crash しない
}
```

**学習ポイント**:
- `try...catch` で `JSON.parse` のエラーを安全にハンドリング
- データが文字列の場合もオブジェクトの場合も対応する **防御的プログラミング**

#### `SpecificationsSection` — テーブル表示

```jsx
function SpecificationsSection({ data }) {
  const items = tryParseJson(data)
  if (!items || items.length === 0) return null   // データなしなら何も描画しない
  return (
    <div style={{ marginTop: 14 }}>
      <h4>Specifications</h4>
      <table style={{ fontSize: 13, borderCollapse: 'collapse', width: '100%' }}>
        <tbody>
          {items.map((spec, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ color: '#777', whiteSpace: 'nowrap' }}>{spec.name}</td>
              <td>{spec.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

**学習ポイント**:
- `items.map()` で配列を JSX のリストに変換（React の基本パターン）
- `key={i}` — React がリスト要素を効率的に更新するための識別子
- `borderCollapse: 'collapse'` — テーブルセル間の隙間をなくす CSS プロパティ
- 早期 return (`if (!items) return null`) でデータがない場合のレンダリングをスキップ

#### `ColorsSection` — タグ（バッジ）表示

```jsx
function ColorsSection({ data }) {
  const items = tryParseJson(data)
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginTop: 14 }}>
      <h4>Colors</h4>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {items.map((color, i) => (
          <span key={i} style={{
            fontSize: 12, padding: '2px 10px',
            borderRadius: 12,       // 角丸でタグ風に
            background: '#f0f0f0',
          }}>{color}</span>
        ))}
      </div>
    </div>
  )
}
```

**学習ポイント**:
- `display: 'flex'` + `flexWrap: 'wrap'` で横並び＋折り返しレイアウト
- `borderRadius: 12` でピル型（角丸）のタグデザイン
- `gap: 6` で Flexbox の子要素間に均等な余白を設定

#### `ReviewsSection` — レビューカード表示

```jsx
function ReviewsSection({ data }) {
  const items = tryParseJson(data)
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginTop: 14 }}>
      <h4>Customer Reviews</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {items.map((rev, i) => (
          <div key={i} style={{ background: '#fafafa', borderRadius: 6, padding: '8px 12px' }}>
            {/* ヘッダー行: 名前（左）と星評価（右） */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 600 }}>{rev.name || 'Anonymous'}</span>
              <span style={{ color: '#e8a000' }}>
                {'★'.repeat(rev.rating || 0)}{'☆'.repeat(5 - (rev.rating || 0))}
              </span>
            </div>
            {rev.title && <p style={{ fontWeight: 500 }}>{rev.title}</p>}
            <p style={{ color: '#555' }}>{rev.review}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**学習ポイント**:
- `'★'.repeat(rev.rating)` + `'☆'.repeat(5 - rev.rating)` で **星評価の視覚化**。例: rating=3 → `★★★☆☆`
- `justifyContent: 'space-between'` で名前を左、星を右に配置
- `rev.name || 'Anonymous'` — 名前が未設定の場合のフォールバック（OR 演算子のショートサーキット）
- `{rev.title && <p>...</p>}` — 条件付きレンダリング。title が存在する場合のみ表示

---

## 3. コンポーネント設計パターンまとめ

| パターン | 使用箇所 | 説明 |
| ------- | ------- | ---- |
| 早期 return | 全専用コンポーネント | データが null/空なら `return null` で何も描画しない |
| props の分割代入 | `ProductDetail`, `ProductCard` | `const { name, ... } = product` でフィールドを展開 |
| ヘルパー関数の分離 | `proxyImageUrl`, `tryParseJson` | ロジックをコンポーネントから切り出して再利用可能にする |
| 条件付きレンダリング | `{brand && <p>...</p>}` | falsy な値の場合は何も表示しない |
| リストレンダリング | `.map((item, i) => <JSX key={i} />)` | 配列から JSX のリストを生成 |
| イベント伝播の制御 | `onClick={e => e.stopPropagation()}` | モーダル内クリックで背景の onClose が発火しないようにする |

---

## 4. 変更ファイル一覧

| File | 変更内容 |
| ---- | ------- |
| `backend/routers/images.py` | 新規: 画像プロキシエンドポイント |
| `backend/main.py` | images router の登録を追加 |
| `frontend/src/api/client.js` | `proxyImageUrl()` ヘルパー関数を追加 |
| `frontend/src/components/ProductCard.jsx` | `proxyImageUrl` を import して画像 src に適用 |
| `frontend/src/components/ProductDetail.jsx` | `proxyImageUrl` 適用 + Specifications/Colors/Reviews の専用コンポーネントを追加 |
