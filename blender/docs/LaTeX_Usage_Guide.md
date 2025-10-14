# LaTeX Documentation for VESPER Interaction System

This folder contains LaTeX documentation for the VESPER Interaction and Time Tracking System, formatted for inclusion in research papers.

## 📄 Files Included

### 1. `VESPER_Interaction_System_LaTeX.tex` (FULL VERSION)
**Size**: ~8-10 pages  
**Use for**: Full technical papers, conference proceedings, journal articles with no page limit

**Contents**:
- Complete system architecture description
- All 4 detailed tables (sensors, devices, time profiles, validation)
- Mathematical formulations (3 equations)
- 4 code listings (CASAS format, JSON logs)
- Integration details
- Evaluation results

**Best for**: IEEE, ACM full papers, technical reports

---

### 2. `VESPER_Tables_and_Figures.tex` (MODULAR)
**Size**: Individual components  
**Use for**: Copy-paste specific tables/figures into your existing paper

**Contents**:
- 4 full tables (ready to copy)
- 3 compact table alternatives
- 3 key equations
- 4 code listing examples
- Inline text alternatives
- Figure suggestions (for you to create)

**Best for**: Adapting to existing paper structure

---

### 3. `VESPER_Compact_LaTeX.tex` (COMPACT VERSION)
**Size**: 1-2 pages  
**Use for**: Papers with strict page limits (workshops, short papers, poster abstracts)

**Contents**:
- 3 concise paragraphs
- 1-3 compact tables (choose based on space)
- Key statistics as inline text
- Ultra-compact 1-paragraph version
- Discussion points

**Best for**: Workshop papers, arXiv shorts, poster submissions

---

## 🎯 Quick Selection Guide

### I have unlimited space → Use `VESPER_Interaction_System_LaTeX.tex`
Compile as standalone document or copy entire section

### I need specific tables → Use `VESPER_Tables_and_Figures.tex`
Pick and choose components

### I have 1-2 pages max → Use `VESPER_Compact_LaTeX.tex`
Concise version with essential information

---

## 📊 Table Selection Guide

Based on what you want to emphasize:

| Table | Emphasis | When to Use |
|-------|----------|-------------|
| `tab:item_sensors` | Sensor coverage | Emphasizing CASAS compatibility |
| `tab:virtual_devices` | Smart home features | Emphasizing IoT/automation |
| `tab:time_profiles` | **Time acceleration** | Emphasizing efficiency/novelty ⭐ |
| `tab:validation_results` | System validation | Emphasizing it works |
| `tab:sensor_summary` | Quick overview | Space-limited papers |
| `tab:time_acceleration_compact` | **Time efficiency** | Best compact choice ⭐ |

**Recommended**: Include `tab:time_acceleration_compact` - it's the most impressive/novel feature.

---

## 🔧 How to Use

### Option A: Standalone Compilation
```bash
pdflatex VESPER_Interaction_System_LaTeX.tex
```

### Option B: Copy into Existing Paper
1. Open `VESPER_Tables_and_Figures.tex`
2. Copy desired tables/equations
3. Paste into your paper's appropriate section
4. Adjust labels if needed

### Option C: Use Compact Version
1. Open `VESPER_Compact_LaTeX.tex`
2. Copy the 3-paragraph subsection
3. Choose 1-2 compact tables
4. Paste into your methodology/implementation section

---

## 📝 Customization Tips

### Change Table Labels
```latex
% Original
\label{tab:item_sensors}

% Your paper's convention
\label{tab:vesper_sensors}
```

### Adjust Table Size
```latex
% Make smaller
\begin{table}[t]
\centering
\small  % or \footnotesize
\caption{...}
...

% Wider tables
\begin{table*}[t]  % Two-column width
...
\end{table*}
```

### Combine Tables
If space is very limited, combine sensors + devices:

```latex
\begin{table}[t]
\caption{VESPER Interaction Components}
\begin{tabular}{lrl}
\toprule
\textbf{Component} & \textbf{Count} & \textbf{Examples} \\
\midrule
Item Sensors & 19 & Sink, Stove, Phone, TV \\
Virtual Devices & 11 & Lights (5), Appliances (6) \\
Time Profiles & 24 & Sleep, Cook, Eat, Clean \\
\bottomrule
\end{tabular}
\end{table}
```

---

## 📈 Key Statistics to Highlight

Include these impressive numbers in your text:

- **5760×** time acceleration (8 hours → 5 seconds)
- **19** CASAS-compatible sensors
- **24** task-specific time profiles
- **41 minutes → 13 seconds** (validation)
- **Millisecond precision** timestamps
- **4 export formats** (CASAS, JSON, SmartThings, time logs)

---

## 🎨 Figure Suggestions

You should create these figures (not included in text files):

### Figure 1: System Architecture
```
┌─────────────────────┐
│   VLM Navigation    │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │ Interaction │
    │   System    │
    └──────┬──────┘
           │
    ┌──────┴──────────────┬────────────┐
    │                     │            │
┌───▼────┐      ┌────▼─────┐   ┌──▼──────┐
│  Item  │      │ Virtual  │   │  Time   │
│Sensors │      │ Devices  │   │ Manager │
└───┬────┘      └────┬─────┘   └──┬──────┘
    └─────────┬──────┴────────────┘
              │
         ┌────▼─────┐
         │  CASAS   │
         │  Export  │
         └──────────┘
```

### Figure 2: Time Acceleration Comparison
Bar chart showing:
- X-axis: Task types (Sleep, Cook, Eat, etc.)
- Y-axis: Time (seconds, log scale)
- Two bars: Virtual time (blue) vs Real time (red)

### Figure 3: Sample Output
Side-by-side comparison:
- Left: VESPER output
- Right: Real CASAS dataset
- Highlight identical format

---

## 📚 Required LaTeX Packages

Make sure your paper includes:

```latex
\usepackage{amsmath}        % For equations
\usepackage{booktabs}       % For nice tables
\usepackage{multirow}       % For complex tables
\usepackage{listings}       % For code listings
```

---

## 🔗 Citation Suggestions

Include these relevant citations:

**CASAS Dataset**:
```
@article{cook2012casas,
  title={CASAS: A smart home in a box},
  author={Cook, Diane J and Crandall, Aaron S and Thomas, Brian L and Krishnan, Narayanan C},
  journal={Computer},
  volume={45},
  number={7},
  pages={62--69},
  year={2012},
  publisher={IEEE}
}
```

**Activity Recognition in Smart Homes**:
```
@article{rashidi2009keeping,
  title={Keeping the resident in the loop: Adapting the smart home to the user},
  author={Rashidi, Parisa and Cook, Diane J},
  journal={IEEE Transactions on Systems, Man, and Cybernetics-Part A: Systems and Humans},
  volume={39},
  number={5},
  pages={949--959},
  year={2009},
  publisher={IEEE}
}
```

---

## ✅ Checklist Before Submission

- [ ] Chose appropriate version (full/compact)
- [ ] Selected relevant tables (1-4 tables)
- [ ] Updated table labels to match your paper
- [ ] Checked table fits in column width
- [ ] Included required packages
- [ ] Cited CASAS dataset
- [ ] Cross-referenced tables in text
- [ ] Spell-checked sensor/device names
- [ ] Verified all numbers are accurate
- [ ] Compiled without errors

---

## 📧 Notes for Co-Authors

**What to emphasize**:
1. **Time acceleration** - Most novel aspect (5760× for sleep)
2. **CASAS compatibility** - Enables direct comparison with real data
3. **Efficiency** - 41 min → 13 sec execution
4. **Format compliance** - Millisecond precision, standard formats

**What not to over-emphasize**:
- Specific sensor counts (19) - less important than coverage
- Number of devices (11) - standard smart home setup
- Implementation details - focus on capabilities

**Positioning**:
- **Methodology section**: How the system works
- **Implementation section**: Technical details
- **Evaluation section**: Validation results
- **Discussion section**: Benefits for ADL research

---

## 🎯 Target Venues

This content is appropriate for:

### Full Version:
- IEEE Pervasive Computing
- ACM Transactions on Intelligent Systems
- Sensors (MDPI)
- IEEE Access
- Conference full papers (8-10 pages)

### Compact Version:
- Workshop papers (4-6 pages)
- Short papers (2-4 pages)
- Poster abstracts (1-2 pages)
- arXiv technical reports

---

## 🔄 Version History

- **v1.0** (2024-10-14): Initial LaTeX documentation
  - Full version with all tables and figures
  - Modular tables for flexible use
  - Compact version for page-limited venues

---

**Questions?** Check the main documentation in `../README_INTERACTION_SYSTEM.md`
