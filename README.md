# HW3
The biggest challenge I faced in this assignment was not knowing how to update the modified code. Later, I realized that I needed to run make again to apply the updates. In Exercise 2 of this assignment, I also learned how to use the blocking technique to reduce cache misses.

Q : Describe the workflow and mechanism in Spike, related to cache simulation.
在 Spike 模擬器中，快取模擬（cache simulation）透過 cache_sim_t 這個類別實現，目的是模擬處理器在執行過程中讀寫記憶體時與 L1 cache 互動的情況。整體模擬流程如下：

記憶體操作攔截（Trace）
當 Spike 執行一個指令導致 LOAD、STORE 或 FETCH 操作時，這些操作會被繼承自 memtracer_t 的類別（如 dcache_sim_t 和 icache_sim_t）所攔截。只有當存取類型符合該 cache（例如：FETCH 對 I-cache，LOAD/STORE 對 D-cache）時，才會進行後續模擬。

檢查是否命中（check_tag）
Cache 模擬器會根據 address 進行 tag 與 index 計算，並從 tags[] 陣列中尋找是否已有相符區塊（代表命中 hit）。若找不到則視為 cache miss。

替換策略（victimize）
若發生 miss，模擬器會根據 FIFO 規則選出一個要替換的區塊（victim），此資訊由 fifo_ptr[] 控制。新的資料會寫入該位置。

處理寫回與遞迴存取（writeback & miss handler）
若被替換的區塊為 dirty（曾經寫入過），模擬器會對更下一層記憶體（通常是另一層 cache 或 main memory）做 write-back 操作。這透過 miss_handler 機制實現遞迴模擬階層式記憶體。

統計記錄與顯示（print_stats）
模擬期間，模擬器會記錄讀寫次數、miss 次數、bytes 傳輸量、write-back 次數等統計資料，最終透過 print_stats() 輸出結果。這些數據有助於計算 cache miss 率與記憶體存取延遲。

Cache 結構初始化與參數設計（sets:ways:linesz）
使用者可透過字串（例如 "8:4:32"）設定 cache 的組數、associativity（相聯度）、與 block size。系統會驗證參數是否為 2 的次方等合法條件，並設定 internal tag array 與相關索引。

完全相聯快取（Fully-Associative Cache）處理
當 cache 為完全相聯（如 1 組、8 way），模擬器會自動轉為使用 fa_cache_sim_t 類別，其內部以 std::map 和 queue 管理資料，不使用固定 index。

Q : Describe the concept behind your modified matrix transpose algorithm.
改良矩陣轉置演算法的核心觀念是 Blocking。
首先將 n × n 矩陣切分為 16×16 的小區塊，在每個區塊內局部完成轉置。這樣設計的目的是讓目前操作的資料集中落在 L1 cache 中，有效提升spatial locality 及 temporal locality。

每個 16×16 的 int 區塊大小為 16×16×4 = 1024 bytes（1KB），剛好等於快取容量（8 sets × 4 ways × 32B = 1024B），保證整個區塊能完整 fit 進 L1 cache，且同一組最多只會佔用 4 個 way，避免不必要的替換。

接著在區塊內使用 微區塊化（2×2 子區塊 + 迴圈展開） 的策略，進一步提升 cache line 的使用率。因為每條 cache line 為 32B，可容納 8 個 int，若只單一訪問一個元素將造成空間浪費。而 2×2 微區塊一次搬移 4 個元素（2 行 × 2 列），可充分利用 2 條 cache line 的資料，並透過 loop unrolling 降低迴圈控制開銷，提升執行效率與 pipeline 的 issue rate。

Q : Describe the concept behind your modified matrix multiplication algorithm.
首先，將矩陣 b 進行轉置，以改善記憶體存取模式。
原本對 a 是以 row-major（連續記憶體）方式讀取，具備良好的空間區域性；但對 b 的訪問則是 column-wise（跨行），容易導致 frequent cache miss。透過轉置 b，將其存取方向改為 row-wise，進而提升 cache line 使用效率與命中率。

接著，採用 Blocking（區塊化） 技術，將矩陣運算拆分為小區塊，提升 L1 cache 的資料重用率，避免在處理大矩陣時造成 cache thrashing。這種區塊內部計算能讓 a、b_t、output 的 working set 控制在 cache 容量內，提高 temporal 與 spatial locality。

此外，在乘法累加的過程中，先使用暫存變數進行區塊內加總，最後再寫回 output 矩陣，可減少對記憶體的寫入次數，降低寫回開銷並避免 cache line 的頻繁失效。

Q : Describe the concept behind your design philosophy of previous Assignment I and Assignment II.
HW1
array_sort.c 的設計說明：
本程式實作了針對固定大小整數陣列的排序功能，使用的是泡沫排序法（Bubble Sort），透過兩層迴圈依序比較並交換相鄰元素，以將陣列由小排到大。特別之處在於程式中加入了 RISC-V 的 inline assembly 組語，將交換的動作以暫存器方式實作，使得交換的邏輯更接近實際硬體層級的運作。此外，程式使用指標（pointer）來操作陣列元素位置，進一步強化對底層記憶體操作方式的掌握。

array_search.c 的設計說明：
本程式設計目的是搜尋一個整數陣列中是否存在指定的目標值（target），採用線性搜尋法（Linear Search）逐一比對每個元素，並找出目標所在的 index。搜尋的過程完全透過 RISC-V inline assembly 撰寫，包含 index 累加、陣列元素存取、與目標比對等，皆以暫存器與指令模擬。此設計不僅加深對組語語意的理解，也強調在處理記憶體與指標運算時的細節處理，實用於低階系統的基礎訓練。

linked_list_sort.c 的設計說明：
此程式針對單向鏈結串列（Singly Linked List）實作排序功能，同樣採用泡沫排序法來排序節點中的數值（val）。設計上不對節點本身的位置或指標重新連接，而是僅交換兩個相鄰節點的數值欄位，避免因 pointer 操作錯誤導致鏈結錯亂。數值交換部分以 RISC-V inline assembly 撰寫，操作指標所對應的記憶體位址，完成兩個節點數值的對調。此設計展示了在 linked list 上進行資料操作時的細緻控制與安全性思考。

HW2
