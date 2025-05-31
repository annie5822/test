# HW3


Q : Describe the workflow and mechanism in Spike, related to cache simulation.

Q : Describe the concept behind your modified matrix transpose algorithm.
改良矩陣轉置演算法的核心觀念是 Blocking。
首先將 n × n 矩陣切分為 16×16 的小區塊，在每個區塊內局部完成轉置。這樣設計的目的是讓目前操作的資料集中落在 L1 cache 中，有效提升spatial locality 及 temporal locality。

每個 16×16 的 int 區塊大小為 16×16×4 = 1024 bytes（1KB），剛好等於快取容量（8 sets × 4 ways × 32B = 1024B），保證整個區塊能完整 fit 進 L1 cache，且同一組最多只會佔用 4 個 way，避免不必要的替換。

接著在區塊內使用 微區塊化（2×2 子區塊 + 迴圈展開） 的策略，進一步提升 cache line 的使用率。因為每條 cache line 為 32B，可容納 8 個 int，若只單一訪問一個元素將造成空間浪費。而 2×2 微區塊一次搬移 4 個元素（2 行 × 2 列），可充分利用 2 條 cache line 的資料，並透過 loop unrolling 降低迴圈控制開銷，提升執行效率與 pipeline 的 issue rate。

Q : Describe the concept behind your modified matrix multiplication algorithm.


Q : Describe the concept behind your design philosophy of previous Assignment I and Assignment II.
