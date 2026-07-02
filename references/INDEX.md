# Domain Routing Reference / 领域路由参考

## 领域检测关键词 / Domain Detection Keywords

### Numerical Computing / 数值计算
- PDE, ODE, finite element, finite difference, FEM, FDM, FVM
- solver, iteration, convergence, discretization
- mesh, grid, time step, CFL
- LINPACK, BLAS, LAPACK, PETSc, Trilinos
- Examples: FEniCS, deal.II, OpenFOAM, MFEM

### Symbolic Algebra / 符号代数
- Groebner basis, polynomial, ideal, ring, module
- symbolic computation, computer algebra
- CAS, Macaulay2, Singular, OSCAR, SageMath
- proof, theorem, lemma, formal verification

### AI4Math / AI for Mathematics
- PINN, neural network, deep learning
- PDE solver with neural nets
- operator learning, DeepONet, Fourier Neural Operator
- scientific machine learning, SciML

### Statistics / 统计学
- MCMC, Monte Carlo, Bayesian
- hypothesis test, confidence interval, p-value
- random effect, mixed model
- Stan, PyMC, R-INLA

### Optimization / 优化
- convex, non-convex, combinatorial optimization
- gradient descent, Newton method, ADMM, PPA
- linear programming, mixed-integer programming
- Gurobi, MOSEK, CPLEX, JuMP, CVXPY

## 三方视角领域适配 / Three-Perspective Domain Adaptation

| 领域 Domain | 研究生视角焦点 | 导师视角焦点 | 审稿人视角焦点 |
|------------|---------------|-------------|---------------|
| 数值计算 Numerical | 离散化方案、误差估计、收敛阶 | PETSc/FEniCS版本、BLAS变体、网格生成工具 | 数值稳定性、迭代收敛判据、网格无关性验证 |
| 符号代数 Symbolic | Groebner基算法、理想运算、环论概念 | CAS版本精确匹配、计算复杂度 | 算法正确性证明、复杂度分析、终止性 |
| AI4Math | 网络架构、损失函数、训练策略 | CUDA版本、框架版本、数据生成流程 | 随机种子管理、训练/测试泄露、消融完整性 |
| 统计 Statistics | MCMC收敛诊断、后验分布理解 | Stan/PyMC版本、RNG版本、链数设置 | 先验敏感性、多重比较校正、计算稳定性 |
| 优化 Optimization | 算法迭代逻辑、收敛条件、停机准则 | 求解器版本、许可证限制、精度设置 | 最优性条件验证、对偶间隙、数值退化 |

## 验证策略 Verdict Strategy

| Domain | Default Tolerance | Verification Method |
|--------|------------------|-------------------|
| numerical | 5% | CI + tolerance band |
| symbolic | N/A | Equivalence check |
| ai4math | 5% or CI | CI + ablation |
| statistics | CI | CI + hypothesis test |
| optimization | 1% or CI | Convergence + objective value |
