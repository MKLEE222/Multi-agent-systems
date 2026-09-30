# OACR Reference Authority v1

**Date:** 2026-09-30  
**Purpose:** authoritative bibliography/claim map for manuscript citations. Metadata below has been externally checked before manuscript insertion.

## Formal inheritance

### Ranzato & Tapparo — strong preservation

Francesco Ranzato and Francesco Tapparo.  
**Strong Preservation as Completeness in Abstract Interpretation.**  
In *Programming Languages and Systems — ESOP 2004*, LNCS 2986, pp. 18–32, 2004.  
DOI: \`10.1007/978-3-540-24725-8_3\`.

Use for:

- minimal refinement relative to a specification language/operator family;
- completeness/strong-preservation correspondence;
- behavioral equivalences characterized as abstract-interpretation refinements.

### Ranzato & Tapparo — generalized strong preservation

Francesco Ranzato and Francesco Tapparo.  
**Generalized Strong Preservation by Abstract Interpretation.**  
*Journal of Logic and Computation* 17(1):157–197, 2007.  
DOI: \`10.1093/logcom/exl035\`.

Use for:

- generalized abstraction beyond partition-only abstract Kripke structures;
- fixed-point characterization of strongly preserving abstractions.

### Mitchell — representation independence

John C. Mitchell.  
**Representation Independence and Data Abstraction.**  
POPL 1986, pp. 263–276.  
DOI: \`10.1145/512644.512669\`.

Use for:

- operation-preserved representation relations;
- client inability to distinguish internal ADT representations through abstract operations.

### Ahmed, Dreyer & Rossberg — state-dependent representation independence

Amal Ahmed, Derek Dreyer, Andreas Rossberg.  
**State-Dependent Representation Independence.**  
POPL 2009, pp. 340–353.  
DOI: \`10.1145/1480881.1480925\`.

Use for:

- explicit boundary against claiming state-dependent representation relations as novel;
- mutable local state and representation independence.

### Darwiche & Marquis — knowledge compilation

Adnan Darwiche and Pierre Marquis.  
**A Knowledge Compilation Map.**  
*Journal of Artificial Intelligence Research* 17:229–264, 2002.  
DOI: \`10.1613/JAIR.989\`.

Use for:

- representation languages evaluated by supported queries and transformations;
- succinctness vs operational capability tradeoffs.

## Learned editing boundary

### Li & Chu — sequential knowledge attenuation

Qi Li and Xiaowen Chu.  
**Can We Continually Edit Language Models? On the Knowledge Attenuation in Sequential Model Editing.**  
*Findings of ACL 2024*, pp. 5438–5455.  
DOI: \`10.18653/v1/2024.findings-acl.323\`.

Use for:

- established sequential-edit interference / attenuation;
- boundary against claiming repeated-edit interference as OACR novelty.

### Lyu et al. — EvoEdit

Sicheng Lyu, Yu Gu, Xinyu Wang, Jerry Huang, Sitao Luan, Yufei Cui, Xiao-Wen Chang, Peng Lu.  
**EvoEdit: Evolving Null-space Alignment for Robust and Efficient Knowledge Editing.**  
*Findings of ACL 2026*, pp. 1520–1540.  
DOI: \`10.18653/v1/2026.findings-acl.75\`.

Use for:

- sequential-edit catastrophic interference as current active literature;
- preservation of prior/original knowledge under edit sequences.

### Zhang et al. — sequential editing collapse

Chi Zhang, Mengqi Zhang, Xiaotian Ye, Runxi Cheng, Zisheng Zhou, Ying Zhou, Pengjie Ren, Zhumin Chen.  
**Spectral Characterization and Mitigation of Sequential Knowledge Editing Collapse.**  
*ACL 2026*, pp. 30009–30032.  
DOI: \`10.18653/v1/2026.acl-long.1384\`.

Use for:

- long-horizon sequential-edit degradation;
- boundary against generic "composition of edits causes collapse" novelty.

### Caddeo, Sanguinetti & Atzori — behavioral reversibility

Emanuele Caddeo, Manuela Sanguinetti, Maurizio Atzori.  
**On Reversibility as Language Model Behavioral Property in Parametric Knowledge Editing.**  
*Applied Sciences* 16(13):6567, 2026.  
DOI: \`10.3390/app16136567\`.

Use for:

- edit→revert behavioral recovery already directly studied;
- boundary against claiming reversibility, behavioral recovery, or parameter non-restoration as OACR novelty.

## Citation discipline

Related Work should distinguish:

1. **inherited mathematical object**
   - strong preservation / behavioral equivalence / representation independence;
2. **representation-operation capability precedent**
   - knowledge compilation;
3. **carrier literature**
   - model editing, version history, dynamic qualification;
4. **OACR paper contribution**
   - implemented-representation audit under prospectively registered native mutation contracts;
   - directional under/over-refinement;
   - same-contract causal discipline;
   - audit-to-repair native replay in multiple substrates.

Do not use any citation to imply that the predecessor is weaker than it actually is.
