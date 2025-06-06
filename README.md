# HW3
The biggest challenge I faced in this assignment was not knowing how to update the modified code. Later, I realized that I needed to run make again to apply the updates. In Exercise 2 of this assignment, I also learned how to use the blocking technique to reduce cache misses.

作業1的部份把快取的替換策略從原本的隨機策略，變成了先進先出（FIFO）的方式。對 set-associative cache 來說，它加了一個 fifo_ptr 陣列，用來記住每組下一個該被替換的欄位（way）在哪，每次替換完就往下移一格，照順序循環。至於 fully associative cache ，則是用一個 queue 來記住資料加入的順序，只要超過容量，就把最早進來的那個踢掉。這樣就可以讓整個替換流程更有規律、也比較好預測。

## Q : Describe the workflow and mechanism in Spike, related to cache simulation.

# Spike Cache Simulator README

Spike 的模擬環境中，Cache Simulation 是藉由 `cachesim.h` 和 `cachesim.cc` 中的類別與方法來完成的。其工作流程與機制主要分為以下幾個部分，涵蓋記憶體訪問攔截（memory access interception）、cache 行為模擬、替換策略、統計紀錄等。

---

##  1. 快取模擬架構 (Cache Simulation Framework)

Spike 的快取模擬架構採物件導向方式設計，包含以下幾個類別：

| 類別名稱                | 功能描述                                                |
| ------------------- | --------------------------------------------------- |
| `cache_sim_t`       | 一般組合快取模擬 (支援 direct-mapped 與 set-associative cache) |
| `fa_cache_sim_t`    | 完全相連快取 (Fully-Associative Cache)                    |
| `cache_memtracer_t` | 快取與記憶體追蹤器整合類別                                       |
| `icache_sim_t`      | 指令快取模擬                                              |
| `dcache_sim_t`      | 資料快取模擬                                              |
| `lfsr_t`            | 實作隨機替換策略的選擇                                 |

---

##  2. 工作流程 (Workflow)

###  Step 1: 建立 Cache 模擬器

```cpp
cache_sim_t::construct(config_str, name);
```

* 例如: `"64:4:32"` 表示 64 組、4-way、block size 32


###  Step 2: 攜得記憶體操作

```cpp
trace(addr, size, type);
```

* `FETCH` 傳給 icache
* `LOAD/STORE` 傳給 dcache

###  Step 3: 模擬 cache 存取

```cpp
cache_sim_t::access(addr, size, is_store);
```

* 判斷 hit/miss (使用 `check_tag()`)
* miss 時:

  * 執行替換 (使用 `victimize()`)
  * 如 victim 為 dirty 則執行寫回
  * 若有下一層 cache 則 access
  * 寫入操作時設定 dirty bit

---

##  3. 模擬細節與位址處理

###  標籤與組指數計算

```cpp
idx = (addr >> idx_shift) & (sets - 1);
tag = (addr >> idx_shift) | VALID;
```

* `idx_shift` 由 block size 決定 (例如 block = 32 則 shift 5 bits)

---

##  4. 統計數據與輸出

使用 `print_stats()` 展示預算效能:

| 指標               | 說明                          |
| ---------------- | --------------------------- |
| `read_accesses`  | 讀取次數                        |
| `write_accesses` | 寫入次數                        |
| `read_misses`    | 讀取 miss 次數                  |
| `write_misses`   | 寫入 miss 次數                  |
| `bytes_read`     | 讀取總使用位元組                    |
| `bytes_written`  | 寫入總使用位元組                    |
| `writebacks`     | 寫回次數 (dirty 被替換)            |
| `miss rate`      | (總 miss / 總 access) \* 100% |

---

##  5. 快取替換策略

###  `cache_sim_t`

* 各 set 維持 FIFO 指鏈 `fifo_ptr`
* victim 被替換 tag (設 VALID bit)
* dirty 則寫回

###  `fa_cache_sim_t`

* 使用 `std::map` 儲存 tag
* FIFO queue 控制替換順序
* 如容量滿，pop 最舊的一項

---

##  6. 清除與失效 (clean\_invalidate)

```cpp
clean_invalidate(addr, size, clean, invalidate);
```

* `clean = true` 則 dirty 寫回
* `invalidate = true` 則清除 valid bit
* 模擬 cache flush/記憶體一致性操作

---

## Q : Describe the concept behind your modified matrix transpose algorithm.
這段程式的設計核心在於改良矩陣轉置演算法，採用 Blocking 技術 將 n×n 矩陣切分為多個 16×16 的小區塊，在每個區塊內局部完成轉置操作。此設計目的是讓目前操作的資料集中落在 L1 cache 中，提升記憶體的 spatial locality（空間區域性） 與 temporal locality（時間區域性），有效降低 cache miss 機率並提升存取效率。

在區塊內，程式進一步使用 2×2 微區塊化策略來提升效能。透過兩層 for 迴圈搭配每次搬移 4 個元素（b_00, b_01, b_10, b_11），不僅減少 index 計算與迴圈控制開銷，也提高 cache line 的使用效率。

此外，為避免處理矩陣邊界時發生記憶體越界錯誤，程式加入條件檢查 x + 1 < n 與 y + 1 < n，例如當 n = 17 且 x = 16 時，x + 1 = 17 會導致存取 src[17 * n + y]，超出合法範圍而產生錯誤。

## Q : Describe the concept behind your modified matrix multiplication algorithm.
首先，將矩陣 b 進行轉置，以改善記憶體存取模式。
原本對 a 是以 row-major 方式讀取，具備良好的空間區域性；但對 b 的訪問則是 column-wise，容易導致 frequent cache miss。透過轉置 b，將其存取方向改為 row-wise，進而提升 cache line 使用效率與命中率。

接著，採用 Blocking 技術，將矩陣運算拆分為小區塊，提升 L1 cache 的資料重用率，避免在處理大矩陣時造成 cache thrashing。這種區塊內部計算能讓 a、b_t、output 的 working set 控制在 cache 容量內，提高 temporal 與 spatial locality。

此外，在乘法累加的過程中，先使用暫存變數進行區塊內加總，最後再寫回 output 矩陣，可減少對記憶體的寫入次數，降低寫回開銷並避免 cache line 的頻繁 miss 的情況。

## Q : Describe the concept behind your design philosophy of previous Assignment I and Assignment II.

### HW1
#### array_sort.c 的設計說明：
此程式實作了針對固定大小整數陣列的排序功能，使用的是 Bubble Sort，透過兩層迴圈依序比較並交換相鄰元素，以將陣列由小排到大。

#### array_search.c 的設計說明：
此程式設計目的是搜尋一個整數陣列中是否存在指定的目標值（target），採用線性搜尋法（Linear Search）逐一比對每個元素，並找出目標所在的 index。

#### linked_list_sort.c 的設計說明：
splitList 是將原始 linked list 平均分成兩半，以利後續進行遞迴式的 merge sort 操作。其核心概念是使用「fast & slow pointers」來找出中間節點，其中 slow 每次前進一格，fast 每次前進兩格，當 fast 或 fast->next 為 NULL 時，slow 剛好停在中間。此時可將 slow->next 作為第二段 list 的開頭（*secondHalf = slow->next），並將 slow->next 設為 NULL 來斷開連結，確保第一段 list（*firstHalf = head）與第二段彼此獨立。若原 list 為空或僅有一個節點，則直接將 *firstHalf 指向 head，*secondHalf 設為 NULL 即可。此設計的關鍵在於利用 fast 指標快速達到尾端，讓 slow 停在中間以實現高效分割。

mergesortedlists則是透過比較兩條已排序的 linked list中節點的資料值，逐步合併成一條新的有序 linked list。程式一開始處理邊界情況，若其中一條為空，則直接回傳另一條；否則透過比較 a->data 與 b->data 的大小，決定哪個節點作為結果 list 的開頭。接著利用 tail 指標追蹤目前合併結果的尾端，進入迴圈反覆比較兩個 list 的當前節點資料值，將較小者接到 tail 之後，並持續前進。當任一條 list 遍歷完後，將尚未處理完的另一條直接串接至 tail，使整個合併過程完整且高效。

### HW2

#### FFT

 pi : 這段程式碼是利用萊布尼茲級數展開式計算圓周率 π 的近似值。程式初始化迴圈變數並將初始正負號設定為 1，接著透過迴圈計算每一項的分母 2k+1，並以 fdiv.s 執行浮點除法求出該項值，再用 fadd.s 累加進結果變數 pi 中。為了實現交錯正負號，每輪迴圈透過 fsgnjn.s 指令反轉符號，模擬數學式中的 (−1) 的k次方。此外，程式在每次使用關鍵指令如加法、除法、符號反轉前，皆用 addi 對應計數器遞增，用於統計指令使用頻率。

 bit_reverse : 這段程式的設計理念是利用逐層掩碼（masking）與位移（shift）操作來完成 32-bit 資料的位元反轉（bit reversal）。這種轉換常用於 FFT 快速傅立葉轉換演算法中，作為資料重排（bit-reversed addressing）的一部分。具體來說，程式將原始整數 b 依照位元組合規律進行多輪操作：

  1.先將奇數與偶數位元對調（1-bit 級距）；

  2.再對每 2-bit、4-bit、8-bit、16-bit 的資料區塊進行反轉；

  3.最後再依據 m 的位元長度（例如 log₂(N)）進行右移對齊，保留 m 位反轉結果。

整體過程不需要使用迴圈或查表，僅透過定值掩碼與位移完成，實現無分支、低延遲的 bit reversal。另外也有透過 others_cnt、add_cnt、sub_cnt 等指令統計變數紀錄每類指令的次數，用於統計指令使用頻率。

 log2 : 這段程式是利用位元右移（srl）模擬整數除以 2 的過程，並統計一個整數 N 至少需要除以幾次 2 才會小於 2，也就是計算整數的「以 2 為底的對數」（log₂ N）整數部分。程式使用 blt 作為迴圈條件判斷，只要 N（t1）大於等於 2，就持續右移除以 2 並將 log 加 1。每執行一次右移與加法，皆透過 addi 對 add_cnt 與 others_cnt 等計數器遞增，用於統計指令使用頻率。

 complex_add : 此段程式碼的目的是實現複數加法運算，即 C=A+B，其中複數 A、B、C 各由實部與虛部組成。程式分別對 A 與 B 的實部、虛部進行浮點加法（fadd.s），將結果儲存至 C 的對應欄位。為了進行效能分析，每次執行浮點加法之前，都使用 addi 將 fadd_cnt 加 1，作為浮點加法指令的執行次數統計。

 complex_mul : 此段程式碼的設計理念是實作複數乘法運算，根據公式 (A_Re + A_Im * i) * (B_Re + B_Im * i)，展開後得到實部為 A_Re * B_Re - A_Im * B_Im，虛部為 A_Re * B_Im + A_Im * B_Re。程式中依序使用 fmul.s 指令計算四個乘積，分別對應實部與虛部的組成，再以 fadd.s 與 fsub.s 完成加減合併，並將結果存入複數 C 的實部與虛部。同時，每執行一次浮點乘法、加法或減法前，透過 addi 將對應的指令計數器（如 fmul_cnt、fadd_cnt、fsub_cnt）加一，用於統計指令使用頻率。

 complex_sub : 此段程式碼針對複數的減法運算進行實作，即 C=A−B，其中複數 A、B、C 各包含實部與虛部。程式先使用 fsub.s 分別對 A 與 B 的實部、虛部做浮點減法運算，並將結果存入 C 的對應位置。同時，為了統計浮點減法指令的使用頻率，每次執行 fsub.s 前都以 addi 將 fsub_cnt 加 1，作為記錄用途。

#### arraymul_baseline & arraymul_improved
baseline 版本採用傳統 for-loop 的形式，逐一處理每一個元素，透過 flw、fmul.s、fadd.s、fsw 等指令對單筆 float 資料進行讀取、乘法、加法與寫回操作，並透過指標的遞增來逐步訪問陣列，h、x、y 在每次迴圈中皆偏移 4 bytes，因此每次迴圈僅處理一筆資料，運算流程簡單直觀，適用於非向量化的基本浮點運算場景。

而 improved 版本則是利用 RISC-V 向量擴充（V Extension）實現批次資料處理，透過 vsetvli 指令根據當前剩餘筆數 arr_size 動態決定每次迴圈可處理的向量長度 n，使其自動適配硬體支援的最大向量寬度。接著利用 vle32.v 將 h 與 x 陣列中的多筆 32-bit 單精度浮點數資料分別載入至向量暫存器 v0 與 v1，並以 vfmul.vv 執行對應元素的乘法運算，結果儲存在 v2 中。隨後透過 vfadd.vf 將常數 id 加至 v2 各元素，完成加法偏移操作，最後以 vse32.v 將結果寫回至 y 陣列。由於每次處理 n 筆資料，實際位移的位元組數為 n * 4（因 float 為 4 bytes），程式會同步更新指標 h、x、y 以及剩餘筆數 arr_size。此實作有效減少迴圈控制與記憶體存取指令數量，達成高效能的平行化資料運算。

#### arraymul_float & arraymul_double
這兩段程式都透過迴圈的方式，對兩個陣列的對應元素進行相乘，並將每次的乘積累乘到 result 中，最終得到整體乘積的結果。主要差別在於，.s 版本使用單精度（float）資料，透過 flw 指令每次載入 4 byte，適用於精度要求較低、運算速度較快的情境；而 .d 版本則使用雙精度（double）資料，透過 fld 指令每次載入 8 byte，提供較高的精度但相對效能略低。

#### macro_define
cycle_count 是將各類指令的執行次數乘上其對應的每指令週期（CPI）後加總，表示程式執行所需的總時脈週期數，常用於跨平台的效能比較；cpu_time 則是將 cycle_count 乘上每個週期所花費的時間（cycle_time），用以估算程式在特定硬體上的實際執行時間，反映程式的執行速度；ratio 則表示運算型指令（如加減乘除及其浮點版本）所佔的週期比例，可用來判斷程式是否為計算密集型（CPU-bound）或記憶體密集型（memory-bound），對於優化方向的判斷具有參考價值。
