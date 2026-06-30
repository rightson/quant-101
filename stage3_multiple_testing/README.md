# Stage 3 — Multiple Testing 與 Research Methodology ★

> **修的錯**:錯誤 B(specification mining / garden of forking paths / HARKing)。文章最致命、最常被忽略的一層。
> **Duration**:4–5 週。**Prereq**:Stage 2。

Stage 2 教你把**單一**檢定做對。Stage 3 的重點是:現實裡你從來不是只做一個檢定。
「新高用一年還是半年?急殺算 3 天還是 4 天?跌幅前 2% 還是 5%?」——每一個沒被講出來
的選擇,都是一次隱性比較。把這些乘起來,「找到一個顯著型態」幾乎是**必然**,跟有沒有
真訊號無關。這是整篇文章最致命的一層,也是 ★ 兩站的第二站。

## 四拍節奏
1. **讀**:Benjamini & Hochberg (1995);Gelman & Loken (2013) "Garden of Forking Paths";Simmons-Nelson-Simonsohn (2011);Ioannidis (2005)。
2. **算**:跑 `notebook_stage3.py`,把事件定義參數化做 grid search,看顯著性如何隨參數漂移、BH 校正後幾乎全滅。
3. **重做 case**:列出文章定義裡所有 researcher degrees of freedom,估計隱性比較數。
4. **過 gate**:見最下方。

## Milestones
- **M3.1** FWER vs FDR;Bonferroni / Holm / Benjamini-Hochberg。
- **M3.2** Researcher degrees of freedom、p-hacking、HARKing(Hypothesizing After Results Known)。
- **M3.3** Pre-registration 的科學哲學基礎;為何「先看到結果再框定義」會讓 in-sample 顯著性貶值。
- **M3.4** 量化直覺:每多一個自由參數,有效 p 值如何膨脹。

## 檔案
| 檔案 | 用途 |
|---|---|
| `lecture.md` | 精講稿 |
| `exercises.md` | 習題 |
| `solutions/ex1_degrees_of_freedom.py` | 列出文章所有 DoF,算隱性比較數與 `P(≥1 顯著)` 膨脹 |
| `solutions/ex2_forking_paths.py` | 純噪音序列跑 50 變體,實證「總會撈到幾個顯著」 |
| `notebook_stage3.py` | 把事件定義 grid search,展示顯著性隨參數漂移、BH 後幾乎全滅 |

## Gate ★
對任一「回測發現」,能估計它試了多少 implicit comparison,並說明 multiple-testing
校正後 p 值如何膨脹。

> **參考值(已用本 repo 程式驗證)**:
> - 文章定義含 5 個 researcher degrees of freedom(新高窗口、急殺天數、近期跌幅窗口、
>   跌幅門檻、評估報酬 horizon),保守各取 4 個合理值 ⇒ **4⁵ = 1024 個隱性比較**。
> - 即使全部都是噪音,`P(≥1 個 raw p<0.05) = 1 − 0.95¹⁰²⁴ ≈ 1.000`——「找到顯著」是必然。
> - Bonferroni 門檻變成 `0.05/1024 ≈ 4.9e-5`;在合成(無訊號)資料上 grid search 後,
>   raw 顯著率 ≈ 5%,經 BH 校正後幾乎歸零。

**正典**:Benjamini & Hochberg (1995);Gelman & Loken (2013);Simmons, Nelson & Simonsohn (2011);Ioannidis (2005)。
