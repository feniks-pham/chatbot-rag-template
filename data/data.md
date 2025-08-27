# COMPUTER ARCHITECTURE — Chapter 1: Technology & Performance Evaluation

> **Course**: CO2007 – Computer Architecture (HCMUT)  
> **Chapter**: 1 — Technology & Performance Evaluation  
> **Instructor (slides)**: Phạm Quốc Cường  
> **Purpose**: A rich, chunkable Markdown knowledge base for RAG/chatbot

---

## 0) Overview & Learning Objectives

### Why this chapter matters
- Gives the **big picture** of how technology progress drives computer capability and **how to measure performance** correctly.
- Establishes common terminology: *response time, throughput, clock, CPI, instruction count, benchmarks*, …

### After studying this chapter, you can
- Explain the **computer revolution** and **Moore’s Law** and relate them to cost/performance trends.  
- Identify **classes of computers** (PC, server, supercomputer, embedded) and **modern components** (CPU datapath/control, memory/cache, I/O).  
- Describe the **abstraction stack** (application, system software, hardware) and **levels of program code** (HLL, assembly, binary).  
- Use performance metrics: **response time vs throughput**, **clock period/frequency**, **CPU time**, **IC**, **CPI**.  
- Compute **relative performance**, **weighted CPI**, analyze **instruction mix**.  
- Understand **power trends** in CMOS and why **parallelism** became crucial.  
- Interpret **benchmarks** (e.g., SPEC CPU2006) and summarize results meaningfully.

---

## 1) Technology Review

### 1.1 Computer Revolution & Moore’s Law
- **Computer revolution**: often considered the **third revolution** after agriculture and industry.  
- **Moore’s Law (1975)**: *“The number of transistors integrated in a chip doubles every **18–24 months**.”*  
  - Consequences:
    - Rapid progress enables **new applications** (automobiles, cell phones, human genome project, WWW, search engines).  
    - Computers become **pervasive** across industries and daily life.

> Rule of thumb: if transistors double every ~2 years, area/cost per function drops, enabling **higher performance** at lower price points.

### 1.2 Historic Milestones (Illustrative Facts)
- **ENIAC** (Electronic Numerical Integrator and Computer):  
  - Mass: **30+ tons**; Area: **~140 m² (1,500+ sq ft)**  
  - Components: **18,000+ vacuum tubes**  
  - Power: **140+ kW**  
  - Speed: **~5,000 additions/s**
- Generations of computers:  
  1) **Vacuum tubes** (1946–1955)  
  2) **Transistors** (1955–1965)  
  3) **Integrated circuits (IC)** (1965–1980)  
  4) **Personal computers** (1980–…)  
  - *What’s next?* — candidates often cited: **quantum computers**, **memristor**, etc.

### 1.3 Classes of Computers (Today’s Landscape)
- **Personal computers**: general-purpose; broad software ecosystem; cost/performance trade-off.
- **Server computers**: network-based; emphasize **capacity**, **performance**, **reliability**; scale from small racks to building-sized deployments.
- **Supercomputers**: high-end for scientific/engineering workloads; **tiny market share** but top capability.
- **Embedded computers**: hidden inside systems (appliances, vehicles, sensors) with tight **power/performance/cost** constraints.

### 1.4 Post-PC Era — Shipment Trends
- Device shipments data typically show **mobile & embedded** dominating volumes in recent years.  
- Implication: **energy efficiency** and **integration** become first-class design goals.

### 1.5 Modern Computer Components (Common Structure)
- **Processor (CPU)** = **Datapath** (executes operations) + **Control** (orchestrates datapath).  
- **Memory**: **main memory** (DRAM) and **cache** levels (SRAM).  
- **Input/Output**: user interface, networking, secondary storage (SSD/HDD), etc.

### 1.6 Abstraction Stack — “Below Your Program”
- **Application software** (written in HLL): productivity & portability.
- **System software**:
  - **Compiler**: translates HLL to **machine code**.
  - **Operating System**: I/O, memory/storage management, scheduling, resource sharing.
- **Hardware**: CPU, memory system, I/O controllers.

### 1.7 Levels of Program Code
- **High-Level Language (HLL)**: closer to problem domain → more **productive** and **portable**.  
- **Assembly language**: human-readable mnemonics for machine instructions.  
- **Hardware representation**: **binary digits (bits)**, **encoded instructions/data**.

### 1.8 Technology Trends — Capacity, Performance, Cost
A representative table (relative perf/cost proxy):
| Year | Technology | Relative perf/cost (approx.) |
|---:|:---|---:|
| 1951 | Vacuum tube | 1 |
| 1965 | Transistor | 35 |
| 1975 | IC | 900 |
| 1995 | VLSI | 2,400,000 |
| 2013 | ULSI | 250,000,000,000 |

*Takeaway*: **Orders-of-magnitude** improvement in perf/cost with advances in electronics/materials.

---

## 2) Performance Evaluation — Core Concepts

### 2.1 Response Time vs Throughput
- **Response time (execution/elapsed time)**: how long to complete a **single** task.  
- **Throughput**: amount of **work per unit time** (e.g., tasks/s, transactions/hour).  
- Upgrading a single CPU usually improves **response time**; adding more CPUs often improves **throughput** (and sometimes response time for parallel workloads).

### 2.2 Relative Performance
- **Performance** is the reciprocal of **execution time**:  
  \( \text{Performance} = \dfrac{1}{\text{Execution time}} \)
- System X vs Y:  
  \( \dfrac{\text{Performance}_X}{\text{Performance}_Y} = \dfrac{\text{Execution time}_Y}{\text{Execution time}_X} \)
- Example: Program takes **10 s** on A, **15 s** on B → **A is 1.5× faster** than B.

### 2.3 Measuring Time — Clock
- Digital hardware is governed by a **clock** with constant period.  
- **Clock period** \(T\): duration of one cycle; units **s**, **ms**, **µs**, **ns**.  
- **Clock rate/frequency** \(F = 1/T\): **Hz**, **kHz**, **MHz**, **GHz**.

### 2.4 CPU Time — Two Equivalent Forms
- \( \text{CPU Time} = \text{CPU Clock Cycles} \times \text{Clock Cycle Time} \)  
- \( \text{CPU Time} = \dfrac{\text{CPU Clock Cycles}}{\text{Clock Rate}} \)

**Improving performance**: reduce **cycles**, increase **clock rate**. But **microarchitectural trade-offs** often mean increasing frequency may increase cycle count (and power).

#### Worked Example — Clock Targeting
- Computer A: **2.0 GHz**; CPU time = **10 s**.  
- Design target B: CPU time = **6 s**, but B needs **1.2×** A’s cycles.  
- Required \(F_B\):  
  \( 6 = \dfrac{1.2\,\text{cycles}_A}{F_B} \Rightarrow F_B = 4.0\,\text{GHz} \)

### 2.5 Instruction Count (IC) & CPI
- **Instruction Count (IC)**: depends on program, ISA, compiler.  
- **Cycles Per Instruction (CPI)**: depends on the CPU implementation and instruction **mix**.

Key relations:
- \( \text{Clock Cycles} = \text{IC} \times \text{CPI} \)  
- \( \text{CPU Time} = \dfrac{\text{IC} \times \text{CPI}}{\text{Clock Rate}} \)

#### Example — Which CPU is Faster?
- A: cycle time **250 ps**, CPI **2.0** → per-instruction time **500 ps**.  
- B: cycle time **500 ps**, CPI **1.2** → per-instruction time **600 ps**.  
- **A is 1.2× faster** (600/500 = 1.2).

### 2.6 Mixed Instruction CPI — Weighted Average
When CPIs differ per instruction type:  
- \( \text{Clock Cycles} = \sum_i ( \text{CPI}_i \times \text{IC}_i ) \)  
- \( \text{Weighted CPI} = \dfrac{\sum_i (\text{CPI}_i \times \text{IC}_i)}{\sum_i \text{IC}_i} \)

**Illustrative Comparison**  
- Impl.1 uses 2A,1B,2C; CPIs 1,2,3 → cycles = 10; IC=5 → **wCPI=2.0**.  
- Impl.2 uses 4A,1B,1C; same CPIs → cycles = 9; IC=6 → **wCPI=1.5** → **faster**.

### 2.7 Guided Exercise — With Solutions
A program runs on **2 GHz** CPU with **1000 instructions**:  
- 30% **load/store** (CPI=2.5), 10% **jump** (1.0), 20% **branch** (1.5), rest **arithmetic** (2.0).

**a) CPU time**  
- Cycles = 300×2.5 + 100×1 + 200×1.5 + 400×2.0 = **1950 cycles**.  
- Time = 1950 / 2e9 = **0.975 µs**.

**b) Weighted CPI** = 1950 / 1000 = **1.95**.

**c) If load/store CPI halves** (≈2.5 → **1.25**)  
- New cycles = 300×1.25 + 100×1 + 200×1.5 + 400×2.0 = **1575 cycles**.  
- New time = 1575 / 2e9 = **0.7875 µs** → **speedup ≈ 1.24×**.

> Pattern: Speedups in the **dominant fraction** of execution yield the **largest gains** (cf. Amdahl’s law intuition).

---

## 3) Power & Energy Trends (CMOS)

### 3.1 Dynamic Power Model
- \( P = C_{load} \times V^2 \times f \)  
  - \(C_{load}\): effective switching capacitance  
  - \(V\): supply voltage  
  - \(f\): frequency

### 3.2 Example — Reducing Power
- New CPU has **85%** of capacitive load, **−15%** voltage, **−15%** frequency:  
  \( \dfrac{P_{new}}{P_{old}} = 0.85 \times 0.85^2 \times 0.85 = 0.85^4 \approx 0.52 \)  
  → **~48% reduction** in dynamic power.

### 3.3 Power Wall & The Move to Parallelism
- Voltage cannot be reduced indefinitely; heat removal is limited → **power wall**.  
- Performance scaling shifts from **frequency** to **parallelism** (multi-core, many-core).  
- Software must expose **parallelism** for gains.

---

## 4) Benchmarks & SPEC CPU

### 4.1 Purpose of Benchmarks
- Use **representative programs** to measure and compare systems.  
- Enable **repeatability** and **fairness** across vendors/platforms.

### 4.2 SPEC CPU2006 Overview
- Targets CPU performance with **negligible I/O**; report **elapsed time** normalized to a reference.  
- Consolidate with **geometric mean** of ratios.  
- Suites: **CINT2006** (integer) and **CFP2006** (floating-point).

> Good practice: inspect per-benchmark results (outliers, variance) rather than only a single combined score.

---

## 5) Performance Summary — The Big Picture
- Performance is influenced by **algorithm**, **language**, **compiler**, and **ISA** through **IC** and **CPI**, and by implementation (**clock rate**).  
- A practical identity to remember:  
  \( \text{CPU time} = \dfrac{\text{Instructions}}{\text{Program}} \times \dfrac{\text{Clock cycles}}{\text{Instruction}} \times \dfrac{\text{Seconds}}{\text{Clock cycle}} \)
- **Execution time** is the most fundamental measure; **power** is a limiting factor; **parallelism** is the path forward.

---

## 6) Worked Examples (More Practice)

### 6.1 Relative Perf with Mix Change
Program X on CPU P has IC=1e9; CPI mix → **wCPI=1.6**; F=2.5 GHz.  
- Time = (1e9 × 1.6) / 2.5e9 = **0.64 s**.  
If a compiler optimization reduces IC by **10%** but raises wCPI to **1.7**:  
- New time = (0.9e9 × 1.7) / 2.5e9 = **0.612 s** → **speedup ≈ 1.046×**.

### 6.2 Frequency vs CPI Trade-off
A redesign increases F from 3.0 → **3.6 GHz** (**+20%**) but CPI increases **+10%** (1.8→1.98).  
- Net: time scales by \(1.10/1.20 = 0.916\) → **~1.09× faster**.

### 6.3 Amdahl-Style “Hot Fraction”
Program time split: 60% arithmetic (CPI=1.5), 40% memory (CPI=3.0) at 2 GHz.  
Improve memory CPI to **2.0**; arithmetic unchanged.  
- Old cycles (per IC): 0.6×1.5 + 0.4×3.0 = **2.1**  
- New cycles: 0.6×1.5 + 0.4×2.0 = **1.7** → **~1.24× speedup**.

---

## 7) Quick Q&A Seeds (Chatbot Prompts)

1. **Moore’s Law nói gì?** — *Số transistor trên chip tăng gấp đôi mỗi 18–24 tháng (1975).*  
2. **Phân biệt response time và throughput?** — *Response: thời gian xong 1 tác vụ; Throughput: lượng việc/đơn vị thời gian.*  
3. **Công thức hiệu năng tương đối X/Y?** — \( {Perf_X}/{Perf_Y} = {Time_Y}/{Time_X} \).  
4. **Clock period và frequency liên hệ thế nào?** — \( F=1/T \).  
5. **CPU time có hai dạng biểu diễn?** — *Cycles×CycleTime* hoặc *Cycles/Freq*.  
6. **IC, CPI ảnh hưởng CPU time ra sao?** — *CPU time = (IC×CPI)/F*.  
7. **Ví dụ 10 s vs 15 s?** — *Hệ A nhanh hơn 1.5×.*  
8. **Tại sao weighted CPI cần thiết?** — *Vì mỗi loại lệnh có CPI khác nhau, phải tính theo mix.*  
9. **Bảng power trong CMOS?** — \( P=C\cdot V^2\cdot f \).  
10. **Power wall là gì?** — *Giới hạn do điện áp/giải nhiệt khiến tăng xung không còn bền vững.*  
11. **Tại sao cần đa xử lý?** — *Tăng hiệu năng qua song song khi không thể tăng xung nữa.*  
12. **Benchmark SPEC CPU2006 đo gì?** — *Hiệu năng CPU (I/O không đáng kể), báo cáo elapsed time chuẩn hoá.*  
13. **CINT vs CFP?** — *CINT: integer; CFP: floating-point.*  
14. **Vì sao cost/performance cải thiện theo thời gian?** — *Nhờ tiến bộ công nghệ bán dẫn/vật liệu.*  
15. **Các lớp trừu tượng dưới chương trình?** — *App → Compiler/OS → Hardware.*

---

## 8) Glossary

- **Response time**: thời gian hoàn thành một tác vụ.  
- **Throughput**: số tác vụ/đơn vị thời gian.  
- **Clock period (T)**: độ dài 1 chu kỳ. **Clock rate (F)**: số chu kỳ mỗi giây.  
- **IC / CPI**: số lệnh; chu kỳ/lệnh (bình quân).  
- **VLSI/ULSI**: Very/Ultra Large Scale Integration.  
- **SPEC CPU2006**: bộ chuẩn đo hiệu năng CPU.  
- **Power wall**: giới hạn tăng hiệu năng do công suất/điện áp/nhiệt.

---

## 9) Key Formulas (Cheat Sheet)

- \( \text{Performance} = \frac{1}{\text{Execution time}} \)  
- \( \dfrac{\text{Perf}_X}{\text{Perf}_Y} = \dfrac{\text{Time}_Y}{\text{Time}_X} \)  
- \( F = 1/T \)  
- \( \text{CPU Time} = \text{CPU Cycles} \times \text{Cycle Time} = \dfrac{\text{CPU Cycles}}{F} \)  
- \( \text{CPU Cycles} = \text{IC} \times \text{CPI} \)  
- \( \text{Weighted CPI} = \dfrac{\sum_i (\text{CPI}_i \cdot \text{IC}_i)}{\sum_i \text{IC}_i} \)  
- \( P = C_{load} \cdot V^2 \cdot f \)

---

## 10) Additional Practice (Self-Check)

1) A vs B: A at 3.2 GHz, wCPI 1.6; B at 2.8 GHz, wCPI 1.2; same IC. Which is faster? By how much?  
2) A compiler reduces IC by 15% but increases wCPI by 5%; frequency unchanged — net effect?  
3) Power budget requires V ↓10%, f ↓10%, Cload unchanged — power ratio?  
4) Given instruction mix and CPIs, compute weighted CPI and CPU time at 3.0 GHz.  
5) Explain why throughput can increase while single-task response time doesn’t improve (or worsens).

---

*End of Chapter 1 — Technology & Performance Evaluation*

# COMPUTER ARCHITECTURE — Chapter 2: Instruction Set Architecture (ISA)

> **Course**: CO2007 – Computer Architecture (HCMUT)  
> **Chapter**: 2 — Instruction Set Architecture (ISA)  
> **Instructor (slides)**: Phạm Quốc Cường  
> **Purpose**: A rich, chunkable Markdown knowledge base for RAG/chatbot, derived from the slide deck

---

## 0) Overview & Learning Objectives

### Why learn the “language” of computers?
- Để **điều khiển phần cứng**, ta cần nói đúng “ngôn ngữ” của máy: **Instruction Set Architecture (ISA)** — giao diện chuẩn giữa **phần mềm** (compiler/OS) và **phần cứng** (CPU, bộ nhớ, I/O).

### After this chapter, you will be able to
- Nêu vai trò của **ISA** và vị trí của nó trong ngăn xếp **HW/SW**.  
- Mô tả mô hình **Von Neumann** (stored-program) và **mô hình thực thi lệnh**.  
- Nắm các **nguyên tắc thiết kế MIPS**, kiểu toán hạng (**register**, **memory operand**, **immediate**).  
- Ghi nhớ **tập thanh ghi MIPS** và chức năng từng nhóm.  
- Viết/đọc các **nhóm lệnh** (số học, truyền dữ liệu, logic, nhánh có điều kiện, nhảy vô điều kiện) và lệnh **so sánh** (`slt`, `slti`, `sltu`, `sltiu`).  
- Biên dịch các đoạn **C → MIPS**, làm chủ **địa chỉ hoá**, **endianness**, **căn chỉnh**.  
- Hiểu **gọi thủ tục** (`jal/jr`), **convention** thanh ghi, **stack** và thủ tục **đệ quy**.  
- Mã hoá/giải mã lệnh theo **R/I/J format**, tính **PC-relative** & **(pseudo) direct** targets; xử lý **nhánh xa**.

---

## 1) Abstraction & ISA

### 1.1 Abstraction layers
- **Application (HLL) → Compiler/OS → Hardware**.  
- **Compiler** dịch HLL → **machine code**; **OS** quản lý I/O, bộ nhớ, lịch trình; **Hardware** = CPU + bộ nhớ + I/O.

### 1.2 Instruction Set Architecture (ISA)
- ISA xác định **tập lệnh**, **toán hạng**, **mã hoá**; cho phép phần mềm **di động** trên nhiều vi xử lý cùng ISA nhưng khác **vi kiến trúc**.

### 1.3 Von Neumann architecture (Stored-program)
- Lệnh và dữ liệu nằm trong **bộ nhớ**; CPU **fetch–decode–execute** theo **PC**.  
- **Loại lệnh cơ bản**:  
  - **Arithmetic** (cộng/trừ…),  
  - **Data transfer** (load/store),  
  - **Logical** (AND/OR/NOR; dịch bit),  
  - **Conditional branch** (`beq`, `bne`),  
  - **Unconditional jump** (`j`, `jal`, `jr`).

### 1.4 Instruction execution model
1) **Fetch** tại địa chỉ **PC** (PC **tự tăng** về *next*).  
2) **Decode & Execute**.  
3) **PC** giữ địa chỉ lệnh **kế tiếp** (trừ khi control-flow thay đổi).

---

## 2) MIPS ISA — Principles, Operands, Registers

### 2.1 Design principles
- **Simplicity favors regularity** (đều đặn → phần cứng/biên dịch dễ).  
- **Smaller is faster** (đường dữ liệu/giải mã ngắn).  
- **Make the common case fast** (tối ưu trường hợp thường gặp).  
- **Good design demands good compromises** (cân bằng tốc độ/cỡ mã/độ phức tạp).

> Mỗi lệnh MIPS **thực hiện 1 thao tác**: ví dụ `a + b + c` cần ≥ 2 lệnh (`add` rồi `add`).

### 2.2 Operand types (chỉ 3 loại!)
1) **Register**: 32 thanh ghi **32-bit** (ký hiệu `$`), truy cập **cực nhanh**.  
2) **Memory operand**: chỉ truy cập bằng **load/store**, **word=4 byte**, **byte-addressable**, **aligned**.  
3) **Short immediate**: số nguyên **16-bit** (có dấu/không dấu tuỳ lệnh).

### 2.3 MIPS register set — Names, numbers, roles
| Class | Names | Numbers | Notes |
|---|---|---:|---|
| Constant | `$zero` | 0 | cứng 0 |
| Assembler temp | `$at` | 1 | assembler dùng |
| Return values | `$v0–$v1` | 2–3 | trả kết quả |
| Arguments | `$a0–$a3` | 4–7 | tham số |
| Temporaries | `$t0–$t7` | 8–15 | **caller-saved** |
| Saved | `$s0–$s7` | 16–23 | **callee-saved** |
| More temps | `$t8–$t9` | 24–25 | caller-saved |
| Kernel | `$k0–$k1` | 26–27 | OS |
| Global ptr | `$gp` | 28 | static data |
| Stack ptr | `$sp` | 29 | đỉnh stack |
| Frame ptr | `$fp` | 30 | frame hiện tại |
| Return addr | `$ra` | 31 | địa chỉ quay về |

---

## 3) Arithmetic & Logical Instructions

### 3.1 Arithmetic group
- **R-format**: `add $rd,$rs,$rt` → `rd = rs + rt`; `sub` tương tự.  
- **I-format**: `addi $rt,$rs,imm16` → `rt = rs + imm16` (sign-extended).

**C → MIPS ví dụ**  
C: `f = (g + h) - (i + j);` với `$s0..$s4` = `g,h,i,j,f`
```asm
add $t0, $s0, $s1     # g + h
add $t1, $s2, $s3     # i + j
sub $s4, $t0, $t1     # f = (g+h) - (i+j)
# hoặc tái sử dụng thanh ghi:
add $s0, $s0, $s1
add $s1, $s2, $s3
sub $s4, $s0, $s1
```

### 3.2 Logical & shift group
- **AND/OR/NOR**: `and/andi`, `or/ori`, `nor` (không có `not`; dùng `nor $d,$s,$zero`).  
- **Shift**: `sll` (dịch trái logic), `srl` (dịch phải logic).  
  - `sll $d,$s,i` = nhân `2^i`; `srl` ≈ chia `2^i` (chỉ đúng với **unsigned**).

**Ví dụ (kết quả)** với `$s0=0x12345678`, `$s1=0xCAFEFACE`  
1) `sll $s2,$s0,4` → `$s2=0x23456780`  
2) `and $s2,$s0,$s1` → `0x02345248`  
3) `or  $s2,$s0,$s1` → `0xDAFEFEFE`  
4) `andi $s2,$s0,2020` → `0x00000660`

---

## 4) Data Transfer — Load/Store, Addressing, Endianness

### 4.1 Addressing form
- Toán hạng bộ nhớ có dạng **`offset(base)`**; **offset** là số nguyên ngắn (16-bit).  
- Bộ nhớ **địa chỉ theo byte**; **word=4 byte**; yêu cầu **aligned** (địa chỉ bội số của 4 cho `lw/sw`).

### 4.2 Load family (đổ *memory → register*)
- `lw` (word, 4 byte),  
- `lh`/**`lhu`** (half, **sign/zero-extend**),  
- `lb`/**`lbu`** (byte, **sign/zero-extend**),  
- `lui` (load **upper** immediate: `$rt = imm << 16`).

### 4.3 Store family (*register → memory*)
- `sw` (word), `sh` (half), `sb` (byte).

### 4.4 Endianness & alignment
- **MIPS Big Endian**: byte **MSB** nằm ở **địa chỉ thấp nhất** của word.  
- Little Endian (tham khảo): byte **LSB** ở địa chỉ thấp nhất.

### 4.5 Worked examples
**Ví dụ 1**: `g = h + A[8]` (g→`$s1`, h→`$s2`, base A→`$s3`)  
- Chỉ số 8 → offset `8×4 = 32`
```asm
lw  $t0, 32($s3)
add $s1, $s2, $t0
```
**Ví dụ 2**: `A[12] = h + A[8]`
```asm
lw  $t0, 32($s3)
add $t0, $s2, $t0
sw  $t0, 48($s3)
```

**Bài tập gợi ý**: Với bản đồ bộ nhớ, cho `$t0=8`, `$s0=0xCAFEFACE`, tính hiệu ứng:
`lw 0($t0)`, `lw 4($t0)`, `lh 4($t0)`, `lb 3($t0)`, `sw $s0,0($t0)`, `sb $s0,4($t0)`, `lh $s0,7($t0)`.

---

## 5) Control Flow — Branches & Jumps

### 5.1 Conditional branch (chỉ **2** lệnh chuẩn)
- `beq $rs,$rt,L1` — nhảy nếu **bằng**.  
- `bne $rs,$rt,L1` — nhảy nếu **khác**.

**If/Else ví dụ**  
C: `if (i==j) f=g+h; else f=g-h;` (`$s0..$s4` = `f,g,h,i,j`)
```asm
bne $s3, $s4, Else
add $s0, $s1, $s2
j   Exit
Else: sub $s0, $s1, $s2
Exit:
```

### 5.2 Set-on-less-than (so sánh)
- `slt  $rd,$rs,$rt` (signed) → `rd=1` nếu `rs<rt` ngược lại `0`.  
- `slti $rt,$rs,imm` (signed),  
- `sltu $rd,$rs,$rt` (unsigned), `sltiu` (unsigned immediate).

**Ví dụ (signed vs unsigned)** với `$s1=0xFFFFFFFF` (−1), `$s2=0x1`
```asm
slt  $t0, $s1, $s2   # $t0=1 (−1 < 1 signed)
sltu $t1, $s1, $s2   # $t1=0 (0xFFFFFFFF > 1 unsigned)
```

**If (i<j) ví dụ**
```asm
slt $t0, $s3, $s4
beq $t0, $zero, Else
add $s0, $s1, $s2
j   Exit
Else: sub $s0, $s1, $s2
Exit:
```

### 5.3 Unconditional jumps
- `j  L1` — nhảy vô điều kiện.  
- `jal L1` — **jump & link**: lưu **PC+4** vào `$ra`, rồi nhảy (dùng gọi hàm).  
- `jr $ra` — nhảy theo địa chỉ trong thanh ghi (thường để **return**).

### 5.4 Vì sao chỉ `beq/bne`, không `blt/bge`?
- Phần cứng cho `<, ≥` **chậm hơn** `=, ≠`; “gộp” phép so sánh vào nhánh khiến **tất cả** lệnh chậm theo.  
- `beq/bne` xử lý **trường hợp phổ biến** → thỏa hiệp **tốt**.  
- Dùng `slt` + `beq/bne` hoặc **pseudo** (`blt` → `slt` + nhánh).

### 5.5 Pseudo instructions (lệnh “giả”)
- Trợ giúp lập trình viên, do assembler **mở rộng** → 1..n lệnh chuẩn.  
  - `move $t0,$t1` → `add $t0,$zero,$t1`  
  - `blt  $t0,$t1,L` → `slt $at,$t0,$t1` ; `bne $at,$zero,L`

---

## 6) Procedures, Stack, Calling Convention

### 6.1 Caller vs Callee
- **Caller**: chuẩn bị tham số (`$a0–$a3`), gọi `jal`.  
- **Callee**: cấp phát vùng làm việc (stack nếu cần), thực thi, **đặt kết quả** ở `$v0/$v1`, `jr $ra` quay lại.

### 6.2 Register usage
- **Args**: `$a0–$a3`; **Returns**: `$v0–$v1`.  
- **Temps**: `$t0–$t9` (caller‑saved).  
- **Saved**: `$s0–$s7` (callee‑saved).  
- **Pointers**: `$gp`, `$sp`, `$fp`, **link** `$ra`.

### 6.3 Stack model
- Stack tăng **xuống** (địa chỉ giảm). `$sp` trỏ đỉnh stack.  
- Lưu/khôi phục thanh ghi theo **quy ước** (đặc biệt `$ra`, `$sX`).

### 6.4 Leaf procedure (không gọi hàm khác)
C:
```c
int leaf_example (int g, int h, int i, int j){
  int f;
  f = (g + h) - (i + j);
  return f;
}
```
MIPS:
```asm
leaf_example:
  addi $sp, $sp, -4
  sw   $s0, 0($sp)

  add  $t0, $a0, $a1
  add  $t1, $a2, $a3
  sub  $s0, $t0, $t1

  add  $v0, $s0, $zero

  lw   $s0, 0($sp)
  addi $sp, $sp, 4
  jr   $ra
```

### 6.5 Non‑leaf (đệ quy) — Factorial
C:
```c
int fact (int n){
  if (n < 1) return 1;
  else return n * fact(n - 1);
}
```
MIPS:
```asm
fact:
  addi $sp, $sp, -8      # chỗ cho $ra và $a0
  sw   $ra, 4($sp)       # lưu địa chỉ quay về
  sw   $a0, 0($sp)       # lưu tham số
  slti $t0, $a0, 1
  beq  $t0, $zero, L1
  addi $v0, $zero, 1     # base case
  addi $sp, $sp, 8
  jr   $ra

L1: addi $a0, $a0, -1
    jal  fact
    lw   $a0, 0($sp)     # khôi phục n
    lw   $ra, 4($sp)     # khôi phục $ra
    addi $sp, $sp, 8
    mul  $v0, $a0, $v0   # n * fact(n-1)
    jr   $ra
```

**Bài tập gợi ý**: Viết `strcpy(char x[], char y[])` với `$a0=x`, `$a1=y`, `$s0=i`, `'

# COMPUTER ARCHITECTURE — Chapter 3: Computer Arithmetic

> **Course**: CO2007 – Computer Architecture (HCMUT)  
> **Chapter**: 3 — Computer Arithmetic  
> **Instructor (slides)**: Phạm Quốc Cường  
> **Purpose**: Tài liệu kiến thức chi tiết, giàu nội dung để dùng cho RAG/chatbot (dễ chunk).

---

## 0) Mục tiêu học tập (Learning Objectives)

Sau chương này, bạn có thể:
- Phân tích **phép toán số nguyên**: cộng, trừ, nhân, chia; nhận biết và xử lý **tràn** (overflow).  
- Mô tả **thuật toán phần cứng** cho nhân/chia (dịch–cộng; chia dài), biến thể **khôi phục** (restoring) và tối ưu phần cứng.  
- Hiểu cách MIPS thực hiện **nhân/chia** với các thanh ghi **HI/LO** và các lệnh liên quan (`mult/multu`, `div/divu`, `mfhi/mflo`, `mul`).  
- Trình bày **IEEE‑754**: biểu diễn **float** (32 bit) và **double** (64 bit), **bias**, chuẩn hóa significand, miền giá trị.  
- Thực hành **cộng/nhân số chấm động**: canh lề, cộng/multiplicand, chuẩn hóa, làm tròn.  
- Viết/đọc **lệnh dấu phẩy động MIPS** (coprocessor 1), thanh ghi `$f0..$f31`, so sánh FP, nhánh theo cờ FP (`bc1t/bc1f`).  
- Nhận thức vấn đề **độ chính xác** (guard/round/sticky, rounding modes) và tác động tới chương trình.

---

## 1) Số nguyên (Integer Arithmetic)

### 1.1 Cộng số nguyên dạng bù 2 (Two’s complement)

- **Không tràn** khi cộng một số **dương** với một số **âm** (khoảng biểu diễn còn đủ rộng).  
- **Cộng hai số dương**: tràn nếu **bit dấu của kết quả = 1** (vượt miền dương).  
- **Cộng hai số âm**: tràn nếu **bit dấu của kết quả = 0** (vượt miền âm).

> Mẹo thực hành: với bù 2, tràn xảy ra khi **hai toán hạng có cùng dấu** nhưng **kết quả khác dấu**.

#### Ví dụ (4 bit, biểu diễn bù 2)
- `7 + 6 = 0111 + 0110 = 1101` → bit dấu = 1 ⇒ **tràn dương** (kết quả thực là 13 vượt miền 4 bit).

### 1.2 Trừ số nguyên

- Biến trừ thành cộng với **phủ định bù 2**: `a − b = a + (−b)`.  
- **Không tràn** khi trừ hai số **cùng dấu** (± ±).  
- **(−) − (+)**: tràn nếu kết quả **dương**; **(+) − (−)**: tràn nếu kết quả **âm**.

#### Ví dụ
- `7 − 6 = 7 + (−6) = 0111 + 1010 = 0001` (không tràn).

### 1.3 Xử lý tràn trong ngôn ngữ/Lệnh MIPS

- Một số ngôn ngữ (C) **bỏ qua tràn** trên số nguyên có dấu ⇒ dùng `addu`, `addiu`, `subu` (**không sinh** exception).  
- Một số khác (Ada/Fortran) yêu cầu **bắt ngoại lệ** ⇒ dùng `add`, `addi`, `sub` (sinh **exception** khi tràn).  
- Khi exception xảy ra, phần cứng:
  - Lưu **PC** tại **EPC** (exception program counter).  
  - **Nhảy** tới handler; dùng `mfc0` để đọc **EPC** và khôi phục sau khi xử lý.

---

## 2) Nhân số nguyên (Integer Multiplication)

### 2.1 Ý tưởng dịch–cộng (shift–add)

- Nhân nhị phân: với **từng bit** của **multiplicand/multiplier**, nếu bit bằng 1 → **cộng** một bản dịch của multiplicand vào tích; nếu 0 → **không cộng**.  
- **Độ dài tích** = tổng độ dài hai toán hạng (ví dụ 32×32 → tích 64 bit).

#### Sơ đồ hoạt động cơ bản
- Giữ **multiplicand**, **multiplier**; duy trì **product (tích)**.  
- Lặp theo số bit của multiplier:  
  1) Nếu **LSB(multiplier) = 1** ⇒ `product += multiplicand`.  
  2) **Dịch** (shift) multiplicand trái, multiplier phải; lặp.

### 2.2 Ví dụ (4 bit)
- `2 × 3 = 0010 × 0011` → tích lần lượt khi xét các bit của multiplier; kết quả nhị phân **0110 (6)**.

### 2.3 Tối ưu phần cứng
- Gộp thanh ghi, giảm số phần tử logic (tối ưu **tài nguyên** hơn là tối ưu **hiệu năng**).  
- Biến thể Booth/biến thể khác (ngoài phạm vi slide) có thể giảm số lần cộng.

### 2.4 Lệnh MIPS cho nhân
- **Tích 64 bit** lưu vào **HI:LO** (HI: 32 bit cao, LO: 32 bit thấp).
  - `mult rs, rt` / `multu rs, rt` → ghi **HI/LO**.  
  - `mfhi rd`, `mflo rd` → đọc kết quả từ **HI/LO**.  
  - Kiểm tra **HI ≠ 0** để biết tích **tràn 32 bit**.  
- **Chỉ lấy 32 bit thấp**: `mul rd, rs, rt` (bỏ phần cao, dễ mất thông tin tràn).

---

## 3) Chia số nguyên (Integer Division)

### 3.1 Chia dài (long division)
- Tương tự phép chia ở thập phân, thao tác trên nhị phân:  
  - Nếu **divisor ≤ phần còn lại (remainder)** ở độ rộng đang xét ⇒ **đặt 1** vào thương, **trừ** divisor.  
  - Ngược lại ⇒ **đặt 0**, **“kéo xuống”** bit tiếp theo của dividend.  
- **n bit** → **thương n bit**; **dư n bit**.

### 3.2 Restoring division
- Thực hiện **trừ**, nếu remainder **< 0** thì **cộng trả** divisor (khôi phục), đặt bit thương tương ứng.

### 3.3 Dấu của thương và dư
- Chia có dấu: làm việc với **giá trị tuyệt đối** rồi **điều chỉnh dấu** của thương và dư theo quy tắc toán học.

### 3.4 Lệnh MIPS cho chia
- Kết quả vào **HI/LO**: **LO = thương (quotient)**, **HI = dư (remainder)**.  
  - `div rs, rt` / `divu rs, rt` → ghi HI/LO.  
  - `mfhi rd`, `mflo rd` → đọc dư/thương.  
- **Không tự động kiểm tra** overflow hay **chia cho 0** ⇒ **phần mềm phải tự kiểm tra** trước khi gọi `div/divu`.

---

## 4) Số chấm động (Floating-Point Numbers)

### 4.1 Khái niệm
- Biểu diễn số **không nguyên** (rất nhỏ đến rất lớn), giống **khoa học**:  
  \( \, (\pm) 	imes 	ext{significand} 	imes 	ext{base}^{	ext{exponent}} \, \).  
- **Chuẩn hóa (normalized)**: significand trong **[1.0, 2.0)** ở nhị phân → luôn có **bit 1 ẩn** trước dấu chấm.

### 4.2 Chuẩn IEEE‑754 (phổ biến)
- Được chuẩn hóa để đảm bảo **tính di động** và **nhất quán** giữa hệ thống.  
- **Single precision** (32 bit) ~ `float (C)`; **Double precision** (64 bit) ~ `double (C)`.

### 4.3 Cấu trúc bit
- **Ký hiệu**: `S | Exponent | Fraction`.  
- **Single**: `1 | 8 | 23` ; **Double**: `1 | 11 | 52`.  
- **Exponent (biased)**: `E = e_real + Bias` với Bias **127 (single)**, **1023 (double)**.  
- **Giá trị**:  
  \[ \, (-1)^S 	imes (1.	ext{Fraction}) 	imes 2^{(E - 	ext{Bias})} \, \]
  (với số **chuẩn hóa**; số đặc biệt/không chuẩn hóa xem ghi chú mở rộng).

### 4.4 Miền giá trị điển hình
- **Single**: gần **±1.2×10⁻³⁸** đến **±3.4×10³⁸**.  
- **Double**: gần **±2.2×10⁻³⁰⁸** đến **±1.8×10³⁰⁸**.  
- `Exponent` toàn 0 hoặc toàn 1 được **dành riêng** cho các trường hợp đặc biệt (ví dụ: 0, ±∞, NaN, subnormal).

### 4.5 Ví dụ giải mã single
- `0x414C0000` → `S=0`, `E=130 (1000_0010₂)`, `Fraction≈0.59375` ⇒ **12.75** (tương đương `1.10011₂ × 2³`).

### 4.6 Các bước đổi số thập phân sang IEEE‑754
1. **Xác định bit dấu `S`** (âm: 1; dương: 0).  
2. **Chuyển phần nguyên và phần lẻ sang nhị phân**, chuẩn hóa về dạng `1.xxx × 2^k`.  
3. **Tính `E = k + Bias`**, điền **Fraction** là phần `xxx` (cắt/ làm tròn theo độ rộng).

---

## 5) Phép cộng số chấm động (FP Addition)

### 5.1 Thuật toán tổng quát
1) **Canh lề**: so sánh exponent; **dịch** số có exponent **nhỏ** hơn để hai significand cùng “thang”.  
2) **Cộng/trừ** significand (tùy dấu).  
3) **Chuẩn hóa** kết quả; kiểm tra **tràn/thiếu** số mũ (over/underflow).  
4) **Làm tròn** theo **rounding mode** (thường là round‑to‑nearest‑even) và **chuẩn hóa lại** nếu cần.

### 5.2 Ví dụ nhị phân (4 chữ số nhị phân)
- `1.000₂ × 2⁻¹ + (−1.110₂) × 2⁻²`  
  - Canh lề ⇒ `1.000₂ × 2⁻¹ + (−0.111₂) × 2⁻¹`  
  - Cộng ⇒ `0.001₂ × 2⁻¹ = 1.000₂ × 2⁻⁴` (**chuẩn hóa**).

### 5.3 Gợi ý phần cứng cộng FP
- Các **bước pipeline**: so sánh/hiệu chỉnh exponent → dịch significand → cộng/trừ → chuẩn hóa → làm tròn → ghi kết quả.

---

## 6) Phép nhân số chấm động (FP Multiplication)

### 6.1 Thuật toán tổng quát
1) **Cộng số mũ** (nếu dùng bias: cộng hai exponent rồi **trừ Bias** một lần).  
2) **Nhân significand** (giữ đủ bit bảo vệ).  
3) **Chuẩn hóa** kết quả; kiểm tra over/underflow exponent.  
4) **Làm tròn** rồi chuẩn hóa lại nếu cần.  
5) **Dấu**: `(+ × −) = −`, `(+ × +) = +`, `(- × -) = +`.

### 6.2 Ví dụ nhị phân
- `1.000₂ × 2⁻¹ × (−1.110₂) × 2⁻²` ⇒ exponent thật **−3**, significand `1.110₂` (đã chuẩn), kết quả **âm**: `−1.110₂ × 2⁻³`.

---

## 7) MIPS và Dấu phẩy động (FP in MIPS)

### 7.1 Coprocessor 1 và tập thanh ghi
- **MIPS FP** là **coprocessor 1**; có **32 thanh ghi đơn**: `$f0..$f31`.  
- **Double** dùng **cặp thanh ghi**: `$f0/$f1`, `$f2/$f3`, … (thanh ghi lẻ là nửa **phải** của 64 bit).  
- Lệnh FP **chỉ** thao tác trên thanh ghi FP; nạp/ghi dùng: `lwc1`, `swc1` (single); `ldc1`, `sdc1` (double).

### 7.2 Số học FP
- **Single**: `add.s`, `sub.s`, `mul.s`, `div.s`.  
- **Double**: `add.d`, `sub.d`, `mul.d`, `div.d`.

### 7.3 So sánh và nhánh theo cờ FP
- So sánh: `c.xx.s`, `c.xx.d` (`eq`, `lt`, `le`, …) → **đặt/xóa** bit **FP condition code**.  
- Nhánh: `bc1t`, `bc1f` (nhánh khi cờ đúng/sai).

#### Ví dụ C → MIPS (float)
```c
float a, b; // $f0=a, $f1=b
if (a < b) a = a + b;
else       a = a - b;
```
MIPS:
```asm
c.lt.s $f0, $f1
bc1t   IF
sub.s  $f0, $f0, $f1
j      EXIT
IF: add.s $f0, $f0, $f1
EXIT:
```

### 7.4 Ví dụ hàm °F → °C
```c
float f2c (float fahr){ return (5.0/9.0)*(fahr - 32.0); }
```
MIPS (ý tưởng):
```asm
lwc1  $f16, const5($gp)
lwc1  $f18, const9($gp)
div.s $f16, $f16, $f18       # 5/9
lwc1  $f18, const32($gp)     # 32.0
sub.s $f18, $f12, $f18       # fahr - 32
mul.s $f0,  $f16, $f18       # (5/9)*(...)
jr    $ra
```

---

## 8) Độ chính xác & làm tròn (Accuracy & Rounding)

- IEEE‑754 hỗ trợ **bit bảo vệ**: **guard, round, sticky** để nâng chất lượng làm tròn.  
- **Rounding modes**: thường dùng **round‑to‑nearest‑even** (mặc định), ngoài ra có **toward‑0**, **+∞**, **−∞**.  
- Không phải mọi FPU đều hỗ trợ **tất cả** chế độ/tuỳ chọn; đa số ngôn ngữ dùng **mặc định**.  
- **Đổi trade‑off**: độ chính xác vs chi phí phần cứng vs hiệu năng.

---

## 9) Kết luận chương

- **Bit** không có nghĩa nội tại; **ý nghĩa** phụ thuộc **cách diễn giải** của lệnh.  
- Biểu diễn số là **hữu hạn** về **miền** và **độ chính xác** ⇒ cần chú ý khi lập trình, đặc biệt với **floating‑point**.  
- **Integer**: hiểu overflow, nhân/chia phần cứng, HI/LO; **FP**: hiểu IEEE‑754, cộng/nhân và lệnh MIPS FP.

---

## 10) Bài tập & ví dụ mở rộng (Practice)

1) **Overflow**: Cho các biểu diễn 8 bit bù 2, xác định tràn cho từng phép cộng/trừ ngẫu nhiên.  
2) **Nhân nhị phân**: Thực hiện `13 × 11` (5 bit), ghi lại các bước cộng–dịch.  
3) **Chia nhị phân (restoring)**: Thực hiện `7 ÷ 2` (4 bit), theo dõi dư/ thương sau mỗi bước.  
4) **MIPS**: Viết trình tự lệnh dùng `mult/mfhi/mflo` để nhân hai số 32 bit có dấu và phát hiện tràn 32 bit.  
5) **IEEE‑754**: Mã hóa `6.3` dạng single (32 bit), chỉ ra `S`, `E`, `Fraction`.  
6) **FP add**: Thực hiện `1.000₂×2⁻¹ + (−1.100₂)×2⁻³`, làm đủ canh lề–cộng–chuẩn hóa–làm tròn.  
7) **FP mul**: Nhân `−1.010₂×2⁴` với `1.001₂×2⁻²`, xác định dấu, exponent mới và significand.  
8) **FP compare & branch**: Dùng `c.lt.s` + `bc1t` để chọn `max(a,b)` cho hai `float` trong `$f0,$f1`.

---

## 11) Bảng tra nhanh (Cheat Sheet)

### 11.1 Integer (MIPS)
- **Nhân**: `mult/multu` → HI:LO; `mfhi/mflo`; **tràn 32 bit** nếu HI ≠ 0 (khi quan tâm 32 bit thấp).  
- **Chia**: `div/divu` → HI = dư, LO = thương; **tự kiểm tra** chia cho 0.  
- **Tràn**: dùng `add/addi/sub` để **bắt** exception; dùng `addu/addiu/subu` để **bỏ qua**.

### 11.2 IEEE‑754
- **Single**: `S(1) | E(8) | F(23)`; Bias = **127**.  
- **Double**: `S(1) | E(11) | F(52)`; Bias = **1023**.  
- **Giá trị**: \( (-1)^S \cdot (1.F) \cdot 2^{(E-Bias)} \).  
- **Miền (xấp xỉ)**: float `~1.2×10⁻³⁸..3.4×10³⁸`; double `~2.2×10⁻³⁰⁸..1.8×10³⁰⁸`.

### 11.3 FP (MIPS)
- **Tải/Lưu**: `lwc1/ldc1`, `swc1/sdc1`.  
- **Toán học**: `add.s/sub.s/mul.s/div.s` (single); `.d` cho double.  
- **So sánh**: `c.eq/c.lt/c.le .s/.d` → cờ FP; **Nhánh**: `bc1t/bc1f`.

---

## 12) Q&A Seeds (Cho chatbot)

- **Hỏi**: Làm sao phát hiện overflow khi cộng bù 2?  
  **Đáp**: Khi hai toán hạng **cùng dấu** mà **kết quả khác dấu** (ví dụ dương+dương ra âm).

- **Hỏi**: Vì sao tích 32×32 cần 64 bit?  
  **Đáp**: **Độ dài tích** bằng **tổng** độ dài toán hạng; cần **HI:LO** để chứa đủ.

- **Hỏi**: `div/divu` trong MIPS có tự bắt chia cho 0 không?  
  **Đáp**: **Không**; phần mềm phải tự kiểm tra trước khi gọi.

- **Hỏi**: Ý nghĩa “bit 1 ẩn” trong IEEE‑754?  
  **Đáp**: Với số chuẩn hóa, significand có dạng `1.xxxx` nên **không cần lưu** bit 1 trước dấu chấm (tiết kiệm 1 bit).

- **Hỏi**: Trình tự cộng FP gồm mấy bước chính?  
  **Đáp**: **Canh lề → Cộng/Trừ significand → Chuẩn hóa → Làm tròn (và chuẩn hóa lại nếu cần)**.

- **Hỏi**: Rounding mode mặc định là gì?  
  **Đáp**: Thường là **round‑to‑nearest‑even** theo IEEE‑754.

- **Hỏi**: Dùng lệnh nào để nhánh theo so sánh FP trong MIPS?  
  **Đáp**: `c.xx.s/d` để đặt **cờ FP**, sau đó `bc1t/bc1f` để nhánh.

---

*End of Chapter 3 — Computer Arithmetic (detailed knowledge base)*

# COMPUTER ARCHITECTURE — Chapter 4: Microarchitecture

> **Course**: CO2007 – Computer Architecture (HCMUT)  
> **Chapter**: 4 — Microarchitecture  
> **Instructor (slides)**: Phạm Quốc Cường  
> **Purpose**: Tài liệu kiến thức **rất chi tiết**, tối ưu để **chunk** cho RAG/chatbot. Nội dung được biên soạn dựa trên slide, diễn giải lại dễ tra cứu.

---

## 0) Mục tiêu học tập (Learning Objectives)

Sau chương này, bạn có thể:
- Mô tả **mô hình thực thi lệnh** (IF, ID, EXE, MEM, WB) và **datapath + control** tương ứng.  
- Xây dựng datapath tối thiểu cho tập lệnh con của **MIPS** (R/I/J; `lw`, `sw`, `add`, `sub`, `and`, `or`, `slt`, `beq`, `j`).  
- Giải thích **đường dữ liệu** dài nhất trong thiết kế **single‑cycle** và hệ quả lên **chu kỳ xung**.  
- Phân tích **pipelining**: hiệu năng, thông lượng, độ trễ, và **pipeline registers**.  
- Nhận diện & xử lý **hazards**: structural, data (RAW), control; kỹ thuật **re‑schedule**, **stall**, **forwarding**, **branch prediction**.  
- Thiết kế **control unit** & **ALU control** (ALUop, funct) và các **control signals** (RegWrite, MemRead, MemWrite, MemtoReg, ALUSrc, RegDst, Branch, PCSrc, Jump,…).

---

## 1) Mô hình thực thi lệnh (Five Stages)

### 1.1 Vòng đời một lệnh
1) **IF—Instruction Fetch**: `PC → Instruction Memory` để đọc **32‑bit instruction**; đồng thời **PC ← PC + 4**.  
2) **ID—Instruction Decode/Register Read**: giải mã opcode/fields; đọc **rs, rt** từ **Register File**; sign‑extend **imm16** (I‑type).  
3) **EXE—Execute/Address Calculation/Compare**:  
   - R‑type: thực hiện phép **ALU**.  
   - `lw/sw`: tính **địa chỉ hiệu dụng** (`base + offset`).  
   - `beq/bne`: **so sánh** đặt cờ **zero**.  
   - `j/jal`: (đường PC riêng, xem §9).  
4) **MEM—Memory Access**:  
   - `lw`: đọc **Data Memory**.  
   - `sw`: ghi **Data Memory**.  
5) **WB—Write Back**: ghi kết quả về **Register File** (R‑type/`lw`).

**Outputs/inputs chuẩn mỗi stage** (dạng tóm tắt để trace):  
- **IF** → `Instruction`, `PC+4`; **ID** → `rs, rt values`, `sign-extended imm`;  
- **EXE** → `ALU_result`, `zero`; **MEM** → `ReadData` (load); **WB** → ghi `Result` vào `rd/rt` tùy `RegDst`.

---

## 2) Datapath & Control (Toàn cảnh)

### 2.1 Thành phần Datapath
- **Instruction Memory** (IF): chứa mã lệnh.  
- **Register File** (ID & WB): 32 thanh ghi 32‑bit, **đọc 2/ghi 1** mỗi chu kỳ.  
- **Sign‑Extend** (ID): mở rộng imm16 thành 32‑bit **có dấu**.  
- **ALU** (EXE): thực hiện `and, or, add, sub, slt`… trả về **zero** & **ALU_result**.  
- **Data Memory** (MEM): tải/ghi dữ liệu.  
- **Multiplexers (MUX)**: chọn **nguồn** cho đầu vào/ghi xuống.  
- **Adders & Shifters**: tính `PC+4`, **branch target** (shift‑left‑2), v.v.

### 2.2 Control signals (tối thiểu)
- **RegDst**: chọn đích ghi (R‑type: `rd` vs I‑type: `rt`).  
- **RegWrite**: cho phép ghi Register File.  
- **ALUSrc**: chọn toán hạng 2 của ALU (`rt` vs **imm**).  
- **MemRead/MemWrite**: truy cập data memory.  
- **MemtoReg**: chọn dữ liệu ghi về reg (`ALU_result` vs `ReadData`).  
- **Branch**: cho đường tính `PCsrc` khi `zero=1`.  
- **PCSrc**: chọn `PC+4` vs `PC_branch`.  
- **Jump**: chọn đường **PC ← {PC[31:28], addr26, 00}** (xem §9).
- **ALUop(2b)**: từ **opcode** → **ALU Control** (4b) cùng `funct`.

---

## 3) Xây datapath cho từng stage (chi tiết)

### 3.1 IF — Instruction Fetch
- **PC → Instruction Memory**; đọc **Instruction[31:0]**.  
- **Add**: `PC+4`.  
- Kết quả chuyển qua **IF/ID** pipeline register.

### 3.2 ID — Instruction Decode
- Tách trường **R/I/J**:  
  - **R**: `opcode[31:26]=0`, `rs[25:21]`, `rt[20:16]`, `rd[15:11]`, `shamt[10:6]`, `funct[5:0]`.  
  - **I** (`lw=35`,`sw=43`,`beq=4`…): `opcode`, `rs`, `rt`, `imm16`.  
- **Register File**: đọc `rs` → `ReadData1`, `rt` → `ReadData2`.  
- **Sign‑Extend**: `imm16 → imm32`.  
- Control unit sinh **RegDst, ALUSrc, MemtoReg, RegWrite, MemRead, MemWrite, Branch, ALUop**.

### 3.3 EXE — Execute
- **ALU** nhận `op1 = ReadData1`, `op2 = MUX(ReadData2, imm32)` theo **ALUSrc**.  
- R‑type: xác định phép bằng **ALU Control** (dựa **ALUop + funct**).  
- `beq`: tính **(ReadData1 − ReadData2)** để lấy **zero**; đồng thời tính **branch target** = `PC+4 + (imm32<<2)`.

### 3.4 MEM — Memory
- **Load**: `MemRead=1` → đọc **ReadData** tại địa chỉ `ALU_result`.  
- **Store**: `MemWrite=1` → ghi `ReadData2` xuống địa chỉ `ALU_result`.

### 3.5 WB — Write Back
- **MUX MemtoReg**: chọn **ALU_result** (R‑type) hoặc **ReadData** (`lw`).  
- **RegDst** chọn `rd` (R‑type) hoặc `rt` (I‑type).  
- **RegWrite=1** để ghi.

---

## 4) Control Unit & ALU Control

### 4.1 Trích bit & lựa chọn trường
- **Read register 1** = **rs** (`inst[25:21]`).  
- **Read register 2** = **rt** (`inst[20:16]`).  
- **Write register** = MUX(`rt` vs `rd`) theo **RegDst**.  
- **Sign‑extend** từ `inst[15:0]`.

### 4.2 Hai tầng xác định phép ALU
- **ALUop (2b) từ opcode**:  
  - `00` → **add** (dùng cho `lw/sw`).  
  - `01` → **sub** (dùng cho `beq`).  
  - `10` → **R‑type** (xem `funct`).  
- **ALU Control (4b)** (ví dụ điển hình):  
  - `0000`: and, `0001`: or, `0010`: add, `0110`: sub, `0111`: slt.

### 4.3 Multiplexers
- **MUX** giúp chọn ngõ vào: ví dụ `ALUSrc`, `MemtoReg`, `RegDst`, `PCSrc`, `Jump`.  
- Quy tắc **S=0→C=A, S=1→C=B** (binary select).

---

## 5) Single‑cycle vs Đường găng (Critical Path)

- **Single‑cycle**: mọi lệnh hoàn tất trong **1 chu kỳ** → **chu kỳ xung** phải đủ lớn cho **đường dài nhất**.  
- Đối với tập lệnh mẫu: đường dài gồm **Instruction Mem → Reg File → ALU → Data Mem → Reg File** (ví dụ `lw`).  
- Không thể “co dãn” chu kỳ theo từng lệnh khác nhau.  
- **Giải pháp**: **pipelining** để tăng **throughput**.

**Ví dụ thời gian stage (minh họa)**:  
- IF/EXE/MEM: **200 ps**, ID/WB: **100 ps**.  
- Bảng thời lượng (tổng):  
  - `lw`: 200 + 100 + 200 + 200 + 100 = **800 ps**.  
  - `sw`: 200 + 100 + 200 + 200 = **700 ps**.  
  - R‑type: 200 + 100 + 200 + 100 = **600 ps**.  
  - `beq`: 200 + 100 + 200 = **500 ps**.

---

## 6) Pipelining (5‑stage)

### 6.1 Ý tưởng & hiệu năng
- Chia lệnh thành **5 stage**, mỗi stage **1 bước**.  
- **Pipeline registers** (IF/ID, ID/EX, EX/MEM, MEM/WB) giữ dữ liệu giữa các stage.  
- **Speed‑up ~ số stage** nếu **cân bằng**; thực tế **kém hơn** do **mất cân bằng** & **hazards**.  
- **Thông lượng** tăng (nhiều lệnh/s hơn); **độ trễ** của **mỗi lệnh** **không giảm** (thậm chí tăng chút do regs).

### 6.2 Ví dụ so sánh
- **Single‑cycle**: `T_c = 800 ps`.  
- **Pipeline**: `T_p = max(stage)` ≈ **200 ps** → lý thuyết **~4×** nhanh hơn (nếu không stall).

---

## 7) Hazards (Nguồn & Biện pháp)

### 7.1 Structural Hazards
- **Xung đột tài nguyên**: ví dụ 1 bộ nhớ cho cả instruction & data.  
- **Khắc phục**: tách **I‑cache** và **D‑cache**; Register File **đọc/ghi cổng riêng**.  
- Trong MIPS điển hình, **đã loại bỏ** structural hazards chính.

### 7.2 Data Hazards (RAW)
- Lệnh sau **cần dữ liệu** do lệnh trước **sản xuất**.  
- Vấn đề xuất hiện ở **pipeline** (không có ở single‑cycle).

**Biện pháp**:  
1) **Code Re‑scheduling** (compiler): đổi vị trí lệnh **độc lập** để né RAW.  
2) **Stalls insertion** (hardware): chèn **bubble** (dừng cập nhật một số regs).  
3) **Forwarding** (hardware): **chuyển tiếp** kết quả từ **EX/MEM** hoặc **MEM/WB** về ngõ vào ALU **trước khi** ghi Register File.

**Load‑use hazard**: `lw` **tạo dữ liệu muộn** → **không thể** forward kịp cho **ngay lệnh kế** → cần **1 stall** (có forwarding) hoặc **2 stalls** (không forwarding).

### 7.3 Control Hazards
- Phụ thuộc **kết quả nhánh** (`beq/bne`) để quyết định **PC**.  
- Cập nhật PC đúng thường ở **MEM** (hoặc EXE, tùy thiết kế) → có **bong bóng**.  
- **Giải pháp**: **branch prediction** (static/dynamic), **chỉ stall khi sai**.

---

## 8) Forwarding & Hazard Detection (Chi tiết)

### 8.1 Forwarding chọn nguồn (F1/F2)
**Bảng điều khiển MUX (ví dụ triển khai):**

| Mux | Giá trị | Nguồn | Giải thích |
|---|:---:|---|---|
| **F1** | `00` | ID/EX | Toán hạng 1 của ALU từ Register File |
|  | `10` | EX/MEM | Toán hạng 1 **forward** từ kết quả ALU ngay trước |
|  | `01` | MEM/WB | Toán hạng 1 **forward** từ data memory/kết quả trước nữa |
| **F2** | `00` | ID/EX | Toán hạng 2 của ALU từ Register File |
|  | `10` | EX/MEM | Toán hạng 2 **forward** từ kết quả ALU ngay trước |
|  | `01` | MEM/WB | Toán hạng 2 **forward** từ data memory/kết quả trước nữa |

### 8.2 Điều kiện Forwarding (minh họa logic)
- **EX hazard**:  
  - `if (EX/MEM.RegWrite && EX/MEM.rd ≠ 0 && EX/MEM.rd == ID/EX.rs) → F1 = 10`  
  - `if (EX/MEM.RegWrite && EX/MEM.rd ≠ 0 && EX/MEM.rd == ID/EX.rt) → F2 = 10`  
- **MEM hazard** (khi **không** trúng EX hazard):  
  - `if (MEM/WB.RegWrite && MEM/WB.rd ≠ 0 && MEM/WB.rd == ID/EX.rs) → F1 = 01`  
  - `if (MEM/WB.RegWrite && MEM/WB.rd ≠ 0 && MEM/WB.rd == ID/EX.rt) → F2 = 01`

### 8.3 Load‑use Hazard Detection (ID stage)
- Hazard nếu:  
  `ID/EX.MemRead && ( (ID/EX.rt == IF/ID.rs) || (ID/EX.rt == IF/ID.rt) )`
- **Cách stall**:  
  - Ép các **control signals** trong **ID/EX** về **0** (EX/MEM/WB **no‑ops**).  
  - **Đóng băng** (không cập nhật) **PC** và **IF/ID** một chu kỳ.

---

## 9) Jumps & PC Update

- Ngoài `PC+4` và `PC_branch`, còn **Jump target**:  
  `PC ← {PC[31:28], address[25:0], 00}`.  
- Cần thêm **MUX** & **control** giải mã từ **opcode** (`j/jal`).  
- Với `jal`: còn phải ghi **$ra = PC+4** (không chi tiết ở đây).

---

## 10) Ví dụ & Bài tập từ slide (diễn giải)

### 10.1 Ví dụ trace `add $s0,$s1,$s2`
- **Instruction Memory**: địa chỉ = `PC`; **Instruction** = mã máy của `add`.  
- **Registers**: đọc `$s1,$s2` → `ReadData1, ReadData2`; ghi về `$s0` với `RegWrite=1` & `RegDst=rd`.  
- **ALU**: thực hiện **add** (`ALUop=10`, `funct=0x20`).  
- **WB**: ghi kết quả về `$s0` khi `MemtoReg=0`.

### 10.2 Pipeline diagram (5 lệnh minh họa)
Chuỗi:  
1) `lw  $s0, 20($s1)`  
2) `sub $t2, $s2, $s3`  
3) `add $t3, $s3, $s4`  
4) `lw  $t4, 24($s1)`  
5) `add $t5, $s5, $s6`  

- Vẽ **multi‑cycle pipeline diagram** theo thứ tự IF→ID→EXE→MEM→WB và phân tích **chu kỳ 5**: stage nào đang xử lý lệnh nào.  
- Lưu ý **control** đi kèm qua pipeline regs (EX/MEM/WB).

### 10.3 Re‑schedule để né RAW
Chuỗi (ví dụ):  
```
1: lw   $t1, 0($t0)
2: lw   $t2, 4($t0)
3: add  $t3, $t1, $t2
4: sw   $t5, 12($t0)
5: lw   $t4, 8($t0)
6: add  $t5, $t1, $t4
7: addi $t6, $t0, 4
```
- RAW tại (3) và (6).  
- Di chuyển lệnh **độc lập** (5,7) lên ngay sau (2): giảm stall.

### 10.4 Stalls insertion & đếm chu kỳ
Với chuỗi:  
```
1: lw  $t1, 0($t0)
2: lw  $t2, 4($t0)
3: add $t3, $t1, $t2
4: sw  $t3, 12($t0)
```
- RAW (2)→(3), (3)→(4).  
- Chèn **2 stalls** cho lệnh (3) và **2 stalls** cho lệnh (4) (minh họa).  
- Tổng **~12 chu kỳ** (theo diagram ví dụ).

### 10.5 Forwarding case
Chuỗi:  
```
1: sub $s2, $s1, $s3
2: and $s7, $s2, $s5
3: or  $s8, $s6, $s2
4: add $s0, $s2, $s2
5: sw  $s5, 100($s2)
```
- `$s2` từ (1) dùng bởi (2)(3)(4)(5) → nhiều **EX/MEM**, **MEM/WB** forward.  
- Vẫn phải **stall 1 chu kỳ** nếu (1) là `lw` (load‑use).

---

## 11) Tóm tắt “Big Picture”

- **ISA ↔ Microarchitecture**: ảnh hưởng **lẫn nhau** (thiết kế datapath/control và tập lệnh).  
- **Pipelining** tăng **throughput** bằng **song song** theo stage; **latency** không giảm.  
- **Hazards**: structural (loại bỏ bằng thiết kế), data (RAW – re‑schedule/stall/forward), control (branch prediction).

---

## 12) Cheat Sheet (nhanh)

- **Stages**: IF/ID/EXE/MEM/WB; **Regs**: IF/ID, ID/EX, EX/MEM, MEM/WB.  
- **Control signals**: `RegWrite, MemRead, MemWrite, MemtoReg, ALUSrc, RegDst, Branch, PCSrc, Jump, ALUop`.  
- **ALUop**: `00` add (`lw/sw`), `01` sub (`beq`), `10` dùng `funct` (R‑type).  
- **Branch target**: `PC+4 + (SignExt(imm16) << 2)`; **Jump**: `{PC[31:28], addr26, 00}`.  
- **Forwarding**: từ **EX/MEM** (EX hazard) & **MEM/WB** (MEM hazard).  
- **Load‑use**: bắt tại **ID**, điều kiện `ID/EX.MemRead && (ID/EX.rt == IF/ID.rs || == IF/ID.rt)` → **stall**.  
- **Speed‑up pipeline** ≈ số stage (nếu cân bằng).

---

## 13) Q&A seeds (gợi ý prompt cho chatbot)

1) **Tại sao single‑cycle phải dùng chu kỳ dài nhất?** — Vì mọi lệnh hoàn tất trong 1 chu kỳ; chu kỳ phải bao trùm **đường găng** dài nhất (thường là `lw`).  
2) **ALUSrc dùng để làm gì?** — Chọn toán hạng 2 của ALU là **rt** hay **imm32**.  
3) **MemtoReg = 1 có nghĩa gì?** — Ghi về reg từ **ReadData** (kết quả `lw`), không phải từ `ALU_result`.  
4) **RegDst = 0/1 tương ứng?** — `0→rt` (I‑type), `1→rd` (R‑type).  
5) **Khi nào cần Branch=1?** — Với `beq` (và `bne` nếu có), để cho phép chọn `PC_branch` khi `zero=1` (hoặc logic tương ứng).  
6) **Vì sao cần forwarding?** — Để **tránh stall** bằng cách dùng **kết quả sớm** từ EX/MEM hoặc MEM/WB.  
7) **Load‑use không forward kịp vì sao?** — Dữ liệu về từ **MEM** quá trễ cho lệnh kế ngay ở **EXE** → phải **stall 1 chu kỳ**.  
8) **Static vs Dynamic branch prediction?** — Static dựa vào kiểu nhánh (vòng lặp/if), Dynamic dùng **phần cứng ghi lịch sử** để dự đoán.  
9) **ALUop=10 dùng cho trường hợp nào?** — **R‑type**; ALU Control nhìn vào `funct` để chọn phép cụ thể.  
10) **Pipeline tăng thông lượng hay độ trễ?** — Tăng **thông lượng**, **độ trễ** mỗi lệnh **không giảm**.

---

## 14) Bài tập (đề nghị luyện RAG)

- **Trace control**: Với `add $t0,$t1,$t2`, liệt kê **input/output** ở từng khối chính và giá trị **control signals** cần thiết.  
- **Reschedule**: Tìm sắp xếp lại chuỗi lệnh có 2 `lw` liên tiếp để loại bỏ **stall** cho `add` sau đó.  
- **Forwarding logic**: Viết **mã giả** cho forwarding unit (điều kiện EX/MEM & MEM/WB) đặt **F1/F2**.  
- **Load‑use detect**: Viết **logic** chèn bubble tại ID khi gặp điều kiện §8.3.  
- **Branch**: Mô tả **bộ dự đoán tĩnh** cho vòng lặp và ước lượng số stall khi dự đoán sai.

---

*End of Chapter 4 — Microarchitecture (detailed knowledge base)*

# COMPUTER ARCHITECTURE — Chapter 5: Memory Hierarchy

> **Course**: CO2007 – Computer Architecture (HCMUT)  
> **Chapter**: 5 — Memory Hierarchy  
> **Instructor (slides)**: Phạm Quốc Cường  
> **Purpose**: Tài liệu kiến thức **rất chi tiết**, tối ưu để **chunk** cho RAG/chatbot. Nội dung được biên soạn dựa trên slide, diễn giải lại dễ tra cứu.

---

## 0) Mục tiêu học tập (Learning Objectives)

Sau chương này, bạn có thể:
- Giải thích **nguyên lý địa phương** (*principle of locality*) và vì sao **phân cấp bộ nhớ** (*memory hierarchy*) hoạt động hiệu quả.  
- Mô tả **tổ chức cache**: **direct‑mapped**, **fully associative**, **n‑way set associative**; **tag/valid/dirty**, **index/offset**.  
- Phân tích **block size** và đánh đổi **miss rate vs pollution vs miss penalty**; hiểu **early restart/critical‑word‑first**.  
- Phân biệt **write‑through vs write‑back**, **write‑allocate vs write‑around**, **dirty bit**, **write buffer**.  
- Tính **AMAT**, **CPI thực** với **miss penalty**, dùng ví dụ định lượng.  
- Giải thích **multilevel caches (L1/L2/L3)**, mục tiêu thiết kế từng mức.  
- Trình bày **DRAM bandwidth**, **interleaving**, **wider memory** và tác động đến **miss penalty**.  
- Hiểu **cơ chế bộ nhớ ảo (virtual memory)**: **page**, **page table**, **TLB**, **page fault**, **bảo vệ**; tương tác **TLB–cache**.  
- Nhận diện **nguồn miss** (compulsory/capacity/conflict), **chính sách thay thế** (LRU/pseudo‑LRU/random).  
- Nhận biết **tối ưu hoá phần mềm** (blocking cho DGEMM) và ảnh hưởng tới cache behavior.

---

## 1) Động lực & Nguyên lý địa phương (Locality)

### 1.1 Ví dụ kệ sách — bộ nhớ
- **Secondary storage (disk/SSD)** ~ *nhà xuất bản* (rất lớn, chậm, rẻ).  
- **Main memory (DRAM)** ~ *bàn làm việc* (vừa, nhanh hơn).  
- **Cache (SRAM)** ~ *bàn tay/cạnh máy* (nhỏ, rất nhanh).

### 1.2 Nguyên lý địa phương
- **Temporal locality**: mục được truy cập **gần đây** có khả năng **được dùng lại sớm** (ví dụ: chỉ thị trong **vòng lặp**, **biến induction**).  
- **Spatial locality**: **lân cận** vị trí vừa truy cập có khả năng **sẽ được truy cập** (ví dụ: đọc chỉ thị **tuần tự**, **mảng**).

### 1.3 Tận dụng locality ⇒ Phân cấp bộ nhớ
- Mọi thứ ở **disk**; **copy** phần **mới dùng/gần kề** sang **DRAM** (main).  
- Từ **DRAM** lại **copy** phần **mới dùng/gần kề** sang **SRAM** (**cache**) **gần CPU**.  
- Đơn vị copy = **block/line** (thường vài chục đến vài trăm byte).

---

## 2) Khái niệm cơ bản của cache

- **Block (line)**: đơn vị chuyển dữ liệu giữa các mức.  
- **Hit**: dữ liệu có **ở mức trên** (upper level) ⇒ phục vụ ngay. **Hit ratio** = hits/accesses.  
- **Miss**: dữ liệu **vắng mặt** ⇒ nạp block từ mức dưới (**miss penalty**). **Miss ratio** = 1 − hit ratio.  
- Khi miss xong, truy cập tiếp theo được **phục vụ từ mức trên** (đã chứa block).

### 2.1 Công nghệ bộ nhớ (độ trễ & giá/GB, xấp xỉ)
| Công nghệ | Thời gian truy cập | Giá |
|---|---|---|
| **SRAM** | ~0.5–2.5 ns | ~$500–$1000/GiB |
| **DRAM** | ~50–70 ns | ~$3–$6/GB |
| **Flash** | ~5–50 μs | ~$0.06–$0.12/GiB |
| **Magnetic disk** | ~5–20 ms | ~$0.01–$0.02/GiB |

> **Lý tưởng** (không đạt được): thời gian **SRAM**, dung lượng/giá **disk**.

---

## 3) Direct‑Mapped Cache

### 3.1 Vị trí block được quyết định bởi địa chỉ
- **Direct‑mapped**: mỗi block bộ nhớ **chỉ có 1 vị trí** trong cache.  
- **Chỉ số (index)** = `(địa chỉ block) mod (#blocks in cache)` ⇒ dùng các **bit thấp** của địa chỉ.

### 3.2 Tag & Valid bit
- Với mỗi **entry** trong cache: lưu **Tag** (các bit địa chỉ **cao**) + **Valid** (1=có dữ liệu, 0=rỗng).  
- Khi **Valid=0**: vị trí **chưa chứa** block hợp lệ.

### 3.3 Chia địa chỉ (Address subdivision)
- **Offset**: chọn **byte/word** trong block.  
- **Index**: chọn **dòng cache**.  
- **Tag**: nhận diện **block** thực sự đang nằm ở dòng đó.

**Ví dụ (block lớn hơn):** 64 blocks, **16 B/block**. Địa chỉ **1200**:  
- **Block address** = ⌊1200/16⌋ = **75**; **Block #** = 75 mod 64 = **11** (vào set 11).

### 3.4 Ví dụ tiến hóa trạng thái
- Với **8 dòng**, **1 word/block**, các truy cập liên tiếp sẽ tạo **miss/hit** tuỳ **tag/index**; sau vài miss đầu (compulsory), các **hit** xuất hiện khi lặp lại địa phương.

---

## 4) Kích thước block & các đánh đổi

- **Block lớn** → **giảm miss rate** nhờ **spatial locality**.  
- Nhưng với **cache cố định dung lượng**: block lớn ⇒ **ít dòng hơn** ⇒ **đụng độ nhiều** (**conflict miss**) và **pollution**.  
- **Larger block ⇒ larger miss penalty** (nạp nhiều byte hơn). **Early restart**/**critical‑word‑first** giúp **giảm thời gian khởi động** dùng được từ sớm.

---

## 5) Miss handling & Pipeline

- **Hit**: CPU chạy bình thường.  
- **Miss**: **stall** pipeline; nạp block từ mức dưới.  
  - **I‑cache miss**: *restart* IF sau khi nạp.  
  - **D‑cache miss**: hoàn tất **data access** sau khi nạp.

---

## 6) Chính sách ghi (Writes)

### 6.1 Write‑through (WT)
- **Hit**: ghi **cache** *đồng thời* ghi **memory** ⇒ dữ liệu **nhất quán**.  
- **Nhược**: ghi **chậm** (mỗi store kéo dài).  
- **Write buffer**: đệm **đang chờ ghi** xuống memory, cho phép **CPU tiếp tục**; chỉ **stall** khi buffer **đầy**.

**Ví dụ CPI (minh hoạ):** `base CPI=1`, `10%` là store, mỗi ghi **100 cycles** ⇒ **CPI hiệu** = 1 + 0.1×100 = **11**. WT + **write buffer** giúp tránh tệ như vậy.

### 6.2 Write‑back (WB)
- **Hit**: chỉ ghi **trong cache**, đánh dấu **dirty**.  
- Khi **thay thế** dirty block ⇒ **ghi ngược** về memory (có thể qua **write buffer** để **đọc block mới** trước).

### 6.3 Write allocation
- **WT**: *allocate on miss* (nạp block) **hoặc** *write‑around* (không nạp). *Write‑around* hữu ích khi **khởi tạo** lớn.  
- **WB**: thường **allocate on miss** để cập nhật trong cache.

---

## 7) Liên kết kết hợp (Associativity)

### 7.1 Ba dạng tổ chức
- **Fully associative**: block có thể vào **bất kỳ entry** ⇒ cần **so sánh tag toàn bộ** (mắc tiền).  
- **n‑way set associative**: cache chia thành **sets**; mỗi set có **n entries**. **Index** chọn set; **so sánh n tag** trong set.  
- **Direct‑mapped**: **1‑way** đặc biệt của set associative.

### 7.2 Dải liên kết (ví dụ 8 entries)
- Từ **direct‑mapped** (1‑way) → **2‑way/4‑way/…** → **fully**. **Tăng associativity** ⇒ **giảm miss** nhưng **chi phí & hit time** tăng.

### 7.3 Ví dụ so sánh hit/miss
Chuỗi truy cập blocks: **0, 8, 0, 6, 8** trên cache 4‑block:  
- **Direct‑mapped**: miss, miss, **miss**, miss, miss (xung đột nặng).  
- **2‑way set**: miss, miss, **hit**, miss, miss.  
- **Fully**: miss, miss, **hit**, miss, **hit** (tốt nhất).

### 7.4 Bao nhiêu associativity là “đủ”?
- Mô phỏng (64KB D‑cache, 16 words/block, SPEC2000):  
  - **1‑way**: 10.3%  
  - **2‑way**: 8.6%  
  - **4‑way**: 8.3%  
  - **8‑way**: 8.1%  
→ **Lợi ích giảm dần** khi tăng way.

---

## 8) Chính sách thay thế (Replacement)

- **Direct‑mapped**: **không có lựa chọn** (vị trí duy nhất).  
- **Set associative**: ưu tiên **entry invalid**; nếu đầy:  
  - **LRU** (ít dùng lâu nhất): tốt nhưng **phức tạp** khi **way lớn** (≥8).  
  - **Pseudo‑LRU**: xấp xỉ LRU, **rẻ**.  
  - **Random**: gần LRU khi **associativity cao**, rất **đơn giản**.

---

## 9) Băng thông bộ nhớ chính & Miss penalty

### 9.1 DRAM + bus (ví dụ minh hoạ đọc 1 block 4 word, DRAM rộng 1 word)
- **1** chu kỳ bus cho **địa chỉ**, **15**/DRAM access/word, **1**/data transfer/word.  
- **Miss penalty** = 1 + 4×15 + 4×1 = **65** chu kỳ bus.  
- **Bandwidth** = 16 B / 65 cyc ≈ **0.25 B/cyc**.

### 9.2 Tăng băng thông
- **Wider memory (4‑word wide)**: miss penalty = **1 + 15 + 1 = 17** cyc ⇒ **0.94 B/cyc**.  
- **4‑bank interleaving**: miss penalty = **1 + 15 + 4×1 = 20** cyc ⇒ **0.8 B/cyc**.

---

## 10) Đo & mô hình hoá hiệu năng cache

### 10.1 Thành phần CPU time
- **Program execution cycles** (bao gồm hit time).  
- **Memory stall cycles** (chủ yếu do miss).

Với giả thiết đơn giản:
\`
Memory stall cycles per instruction
= Misses/Instruction × Miss penalty
= Memory accesses/Instruction × Miss rate × Miss penalty
\`

### 10.2 Ví dụ CPI
- **I‑miss rate** = 2%  
- **D‑miss rate** = 4%  
- **Miss penalty** = 100 cycles  
- **Base CPI (ideal cache)** = 2  
- **Load+Store** = 36% instr.  
⇒ **Miss cycles/inst** = I: 0.02×100 = **2**, D: 0.36×0.04×100 = **1.44**  
⇒ **CPI thực** = 2 + 2 + 1.44 = **5.44** ⇒ **CPU lý tưởng** nhanh **2.72×**.

### 10.3 AMAT (Average Memory Access Time)
\`
AMAT = Hit time + Miss rate × Miss penalty
\`
**Ví dụ**: clock 1 ns (1 cycle), hit = 1 cyc, miss penalty = 20 cyc, I‑miss = 5%  
⇒ **AMAT** = 1 + 0.05×20 = **2 ns** (≈ 2 cycles/access).

### 10.4 Tóm tắt hiệu năng
- Khi **base CPI giảm** hoặc **clock tăng**, **miss penalty** chiếm **tỷ trọng** lớn hơn ⇒ phải **tối ưu cache**.

---

## 11) Cache đa mức (Multilevel)

### 11.1 Ý tưởng
- **L1** gần CPU: **rất nhanh**, **nhỏ**.  
- **L2** phục vụ **miss của L1**: **lớn hơn**, **chậm hơn** nhưng vẫn **nhanh hơn DRAM**.  
- Có thể có **L3** (trên desktop/server).

### 11.2 Ví dụ định lượng
- **Base CPI**=1, **F=4 GHz** ⇒ **T=0.25 ns**/cycle.  
- **Miss rate/instruction** (L1) = 2%  
- **Main mem access** = 100 ns ⇒ **400 cycles**.  
- **Chỉ L1**: **CPI** = 1 + 0.02×400 = **9**.  
- **Thêm L2**: access L2 = **5 ns** ⇒ **20 cycles**; **global miss rate→mem** = **0.5%**.  
  - **Penalty khi L1 miss & L2 hit** = **20 cycles**.  
  - **Penalty thêm khi L2 miss** = **400 cycles**.  
  - **CPI** = 1 + 0.02×20 + 0.005×400 = **3.4** ⇒ **tăng 2.6×** so với chỉ L1.

### 11.3 Cân nhắc thiết kế
- **L1**: tối ưu **hit time** (nhỏ, đơn giản).  
- **L2**: tối ưu **miss rate** (lớn hơn, **block size** **lớn hơn** L1).

---

## 12) Tương tác với CPU hiện đại & phần mềm

### 12.1 Out‑of‑order (OOO)
- OOO có thể **tiếp tục** thực thi lệnh **độc lập** trong lúc **cache miss**. **Store** chưa commit ở **LSU**; **dependent** chờ tại **reservation station**.  
- Ảnh hưởng miss phụ thuộc **data‑flow** chương trình ⇒ **khó phân tích tĩnh**, cần **mô phỏng hệ thống**.

### 12.2 Ảnh hưởng phần mềm & compiler
- **Mẫu truy cập bộ nhớ** quyết định miss: thuật toán & **tối ưu hoá compiler** (loop interchange, blocking…).

### 12.3 Blocking cho DGEMM
- **Mục tiêu**: **tối đa** số truy cập tới **khối dữ liệu** trước khi bị thay thế.  
- Với **N=32**, 3 ma trận 32×32×8 bytes ≈ **24 KB** ≈ **L1 32 KB** (Core i7 Sandy Bridge).  
- **Khi N tăng**: miss tăng; **chia khối (BLOCKSIZE)** và **đi tuần khối** giữ locality tốt hơn (mẫu code `do_block`, `dgemm`).

---

## 13) Bộ nhớ ảo (Virtual Memory)

### 13.1 Tổng quan
- Dùng **main memory** như **cache** của **secondary storage**; được quản lý bởi **CPU HW + OS**.  
- Mỗi tiến trình có **không gian địa chỉ ảo riêng** (bảo vệ).  
- **Dịch địa chỉ**: ảo → vật lý; **đơn vị**: **page** (ví dụ 4 KB). **Miss** trong VM = **page fault**.

### 13.2 Page table & dịch địa chỉ
- **Page Table Entry (PTE)** chứa **physical page number** + **bit trạng thái** (valid/referenced/dirty/…); **PTE** nằm trong **DRAM**.  
- Thanh ghi **Page Table Base** trỏ tới trang chứa bảng.  
- Khi trang **không có** trong DRAM: PTE trỏ tới **khu swap** trên **disk**.

### 13.3 Page fault
- **Rất đắt**: **triệu chu kỳ**; do **OS** xử lý: định vị trang trên disk, chọn trang thay thế (nếu dirty → **ghi ra disk**), đọc vào DRAM, cập nhật PTE, **restart** chỉ thị.

### 13.4 TLB (Translation Look‑aside Buffer)
- **Cache PTE** nằm trong CPU; điển hình **16–512** mục; **hit** ~ **0.5–1 cyc**, **miss** ~ **10–100 cyc**, **miss rate** ~ **0.01–1%**.  
- **Miss** có thể xử lý bằng **phần cứng** hoặc **phần mềm** (exception tới handler tối ưu).

### 13.5 Tương tác TLB–cache
- Nếu **cache tag dùng _địa chỉ vật lý_**: cần **dịch địa chỉ trước** khi lookup cache.  
- Nếu dùng **_địa chỉ ảo_** cho tag: tránh dịch trước nhưng có **aliasing** khi **nhiều VA** trỏ tới **cùng PA** ⇒ phức tạp consistency.

### 13.6 Bảo vệ bộ nhớ & đặc quyền
- Hỗ trợ **Supervisor mode** (kernel) & **privileged instructions**.  
- PTE/OS state chỉ truy cập trong **kernel mode**. **System call** (ví dụ `syscall` MIPS) chuyển đặc quyền.

### 13.7 Bài tập TLB/Page table (minh hoạ)
- **4 KB page** ⇒ **12 bit offset**.  
- Với dãy VA `4669, 2227, 13916, 34587, 48870, 12608, 49225, …` ⇒ **VPN** lần lượt: `1, 0, 3, 8, 11, 3, 12, …`.  
- Xét **TLB fully associative + LRU**, page table **LRU**: xác định **trạng thái cuối** của **TLB** và **page table**; đổi sang **16 KB page** và so sánh.

---

## 14) Phân loại miss & Chính sách ghi (tổng quát)

### 14.1 Nguồn miss
- **Compulsory**: lần đầu truy cập block (không tránh được).  
- **Capacity**: dung lượng cache **không đủ**.  
- **Conflict**: cache **không fully associative** ⇒ **đụng độ set**.

### 14.2 Tìm block & so sánh tag
| Tổ chức | Cách định vị | So sánh tag |
|---|---|---|
| Direct‑mapped | **Index** | **1** |
| n‑way set | **Set index** → tìm trong **n entries** | **n** |
| Fully associative | **Bất kỳ** | **#entries** |
| VM (bảng trang) | **Bảng tra cứu đầy đủ** | **0** (so sánh gián tiếp) |

### 14.3 Chính sách ghi (tổng quát)
- **Write‑through**: ghi cả **trên & dưới**; đơn giản thay thế, cần **write buffer**.  
- **Write‑back**: ghi **trên**, ghi **dưới khi thay**; cần **dirty bit** và trạng thái nhiều hơn.  
- **VM**: thực tế chỉ **write‑back** do **latency disk**.

---

## 15) Tóm tắt “Big Picture”

- **Bộ nhớ nhanh thì nhỏ, bộ nhớ lớn thì chậm**; **cache** tạo **ảo tưởng** “vừa nhanh vừa lớn”.  
- **Locality** (temporal/spatial) là nền tảng cho **hierarchy**.  
- Thiết kế bộ nhớ/caches **rất quan trọng** cho hiệu năng hệ thống hiện đại (đặc biệt đa lõi).

---

## 16) Cheat Sheet (nhanh)

- **AMAT** = `Hit time + Miss rate × Miss penalty`.  
- **CPI thực** ≈ `Base CPI + Miss cycles/instruction`.  
- **Write policies**: WT (+buffer) vs WB (+dirty).  
- **Associativity**: 1‑way (DM) ↔ n‑way ↔ fully; tăng way **giảm miss** nhưng **tăng hit time/chi phí**.  
- **Replacement**: LRU (chính xác), **pseudo‑LRU** (xấp xỉ), **random** (đơn giản).  
- **DRAM penalty**: cải thiện bằng **wider memory** hoặc **interleaving**.  
- **Multilevel**: L1 **nhanh**, L2 **giảm miss tới DRAM**, đôi khi L3.  
- **VM**: Page, PTE, TLB, page fault rất đắt; **bảo vệ** bằng kernel mode.

---

## 17) Q&A Seeds (gợi ý prompt cho chatbot)

1) **Vì sao cache hoạt động hiệu quả?** — Do **temporal** và **spatial locality**.  
2) **Khác biệt WT vs WB?** — WT ghi cả cache & memory (cần **write buffer**); WB chỉ ghi cache, **dirty** rồi ghi về khi thay thế.  
3) **Write‑allocate vs write‑around?** — Allocate: nạp block khi write miss; Write‑around: ghi thẳng xuống dưới, **không nạp**.  
4) **Direct‑mapped khác set associative thế nào?** — DM mỗi block có **1 chỗ**; set assoc có **n chỗ** trong **set**.  
5) **Tag/Index/Offset là gì?** — Phân tách địa chỉ: **Tag** nhận diện block, **Index** chọn dòng/set, **Offset** chọn byte.  
6) **Nguồn miss gồm gì?** — **Compulsory/Capacity/Conflict**.  
7) **AMAT nghĩa là gì?** — **Average Memory Access Time** = hit time + miss rate × miss penalty.  
8) **Ví dụ CPI với miss penalty?** — Với số liệu I‑miss=2%, D‑miss=4%, penalty=100 cyc, base=2 ⇒ **CPI=5.44**.  
9) **Multilevel cache mang lại gì?** — **Giảm penalty** nhờ L2 hấp thụ L1 miss; ví dụ giảm CPI từ **9** còn **3.4**.  
10) **TLB dùng để làm gì?** — **Cache PTE** để dịch VA→PA nhanh; hit ~ **0.5–1 cyc**, miss ~ **10–100 cyc**.  
11) **Page fault là gì & đắt bao nhiêu?** — Trang không ở DRAM, phải đọc từ disk: **triệu chu kỳ**.  
12) **Interleaving DRAM là gì?** — Chia **n ngân hàng** phục vụ song song, tăng **băng thông hiệu dụng**.  
13) **LRU khó ở where?** — Khó/đắt khi **associativity cao**; dùng **pseudo‑LRU**/random.

---

## 18) Bài tập luyện

1) **Chia địa chỉ**: Cho cache 64 KB, 4‑way, 64 B/block. Tính số **sets**, số **bit offset/index/tag** với địa chỉ 32‑bit.  
2) **CPI & AMAT**: Với `hit time L1 = 1 cyc`, `miss rate L1 = 3%`, `L2 hit penalty = 12 cyc`, `global miss to mem = 0.7%`, `mem penalty = 180 cyc`. Tính **AMAT** và **CPI** (base=1.2, 30% là loads/stores).  
3) **WT vs WB**: Với workload ghi nặng, so sánh **băng thông ghi** yêu cầu ở **bus** cho WT (có write buffer) vs WB.  
4) **Blocking DGEMM**: Cho L1=32 KB, linesize=64 B. Chọn **BLOCKSIZE** sao cho ba **sub‑blocks** A/B/C nằm chủ yếu trong L1.  
5) **TLB**: Cho TLB 64 entries, fully associative, LRU. Dãy VA ảo; xác định **TLB hit/miss** và **page fault**.  
6) **Nguồn miss**: Thiết kế chuỗi địa chỉ gây **conflict miss** nặng trong DM cache, rồi so sánh với 2‑way cache cùng dung lượng.

---

*End of Chapter 5 — Memory Hierarchy (detailed knowledge base)*


