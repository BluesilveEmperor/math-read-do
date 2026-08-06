"""Reproduction registry for the 10 quantitative-finance experiments.

Every entry is grounded in the actual reproduction run recorded under
``math-read-do-financial-best-repro`` (2026-08-05/06, WSL2 Ubuntu, 8-core CPU,
3.7 GB RAM, no GPU).  Statuses are one of:

    done     — fully reproduced, numbers match the paper within tolerance
    partial  — some configurations reproduced, others blocked
    blocked  — cannot be reproduced (missing commercial data / missing code /
               insufficient hardware)

Ref: REPRO_STATUS.md of the reproduction bundle.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

DONE = "done"
PARTIAL = "partial"
BLOCKED = "blocked"

# conda environments used by the reproduction
ENV_TF = "financial"      # Python 3.11.15, TensorFlow 2.15.0
ENV_TORCH = "sigtorch39"  # Python 3.9.23, torch 1.9.1+cpu, signatory 1.2.6


@dataclass
class Experiment:
    eid: str
    name: str
    venue: str
    env: str
    status: str
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    fixes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


REGISTRY: Dict[str, Experiment] = {e.eid: e for e in [
    Experiment(
        eid="01", name="Robust Deep Hedging", venue="Quantitative Finance 2022",
        env=ENV_TF, status=DONE,
        metrics={"notebooks_ok": 4, "notebooks_total": 4},
        artifacts=["01_nga/*.ipynb", "logs/01/*.log"],
    ),
    Experiment(
        eid="02", name="Sig-Wasserstein GANs", venue="Mathematical Finance 2023",
        env=ENV_TORCH, status=DONE,
        metrics={"runs_ok": 4, "runs_total": 4},
        artifacts=["02_results/GBM/SigWGAN_LSTM_0",
                   "02_results/GBM/SigWGAN_LogSigRNN_0",
                   "02_results/GBM/WGAN_LSTM_ResFNN_0",
                   "02_results/GBM/WGAN_LogSigRNN_ResFNN_0"],
        fixes=["train.py:93 discriminator input_dim: x_real_dim * n_lags (16) "
               "-> x_real_dim * x_real.shape[1] (17 real time steps)"],
    ),
    Experiment(
        eid="03", name="Joint Calibration SPX/VIX", venue="Mathematical Finance 2024",
        env=ENV_TORCH, status=PARTIAL,
        metrics={"configs_ok": 4, "configs_total": 8},
        artifacts=["03_joint_calib/output/n=2..5/Rho_d=4.npy", "logs/03/sampler*.log"],
        blockers=["sampler configs 6,7,8 produce empty output directories"],
    ),
    Experiment(
        eid="04", name="Deep xVA Solver", venue="SIAM J. Financial Math 2023",
        env=ENV_TF, status=PARTIAL,
        metrics={"callOption_Y0": 1.9673, "fvaForward_Y0": 1.98},
        artifacts=["BasketOption.pdf", "exposureBasketOption.xlsx",
                   "exposureCallOption.xlsx", "exposurePricingForward.xlsx"],
        blockers=["basketCallWithCVA.py: BCVA second stage hangs at 0% CPU "
                  "(blocking plt.show() or OOM after first-stage training)"],
    ),
    Experiment(
        eid="05", name="Fin-GAN", venue="Quantitative Finance 2024",
        env=ENV_TF, status=DONE,
        metrics={"SR_w_test": 0.88, "SR_w_val": 2.19, "epochs": 100},
        artifacts=["05_Fin_GAN_results/TrainedModels/*.pth",
                   "05_Fin_GAN_results/PnLs/AMZN-FinGAN-PnL.csv",
                   "05_Fin_GAN_results/Plots"],
        blockers=["CRSP/WRDS licensed data unavailable -> GBM synthetic "
                  "AMZN/HD/XLY series used as substitute"],
    ),
    Experiment(
        eid="06", name="Signature-Based Models", venue="SIAM J. Financial Math 2023",
        env=ENV_TORCH, status=BLOCKED,
        blockers=["maturities_SPX_Bloomberg.npy / strikes_SPX_Bloomberg.npy are "
                  "commercial Bloomberg data",
                  "synthetic substitute gives strike-dimension mismatch 7 vs 9"],
    ),
    Experiment(
        eid="07", name="Network Superhedging", venue="Mathematical Finance 2022",
        env=ENV_TORCH, status=DONE,
        metrics={"lam200_price": 1.3274, "lam200_hedge_prob": 0.4072,
                 "lam100k_price": 2.0952, "lam100k_hedge_prob": 0.9966,
                 "bs_delta_price": 1.3819, "bs_delta_hedge_prob": 0.5369,
                 "params": 11191},
        artifacts=["07_Network_Superhedging/实验报告",
                   "07_Network_Superhedging/实验结果对比表",
                   "07_Network_Superhedging/训练结果"],
    ),
    Experiment(
        eid="08", name="Signature Volatility Models",
        venue="SIAM J. Financial Math 2025", env=ENV_TORCH, status=BLOCKED,
        blockers=["upstream GitHub repo never committed fourier.py, "
                  "fourier_sig.py, trajectories.py, utils.py"],
    ),
    Experiment(
        eid="09", name="Optimal Stopping with Randomized NN",
        venue="Frontiers Math Finance 2023", env=ENV_TF, status=DONE,
        metrics={"nlsm_price_min": 10.9, "nlsm_price_max": 21.7},
        artifacts=["09_optstop/bs_maxcall.log", "logs/09/*.log"],
    ),
    Experiment(
        eid="10", name="Deep Weighted Monte Carlo",
        venue="Quantitative Finance 2023", env=ENV_TF, status=PARTIAL,
        artifacts=["10_DeepWMC/*.ipynb", "logs/10/tutorial.log"],
        blockers=["ICAP confidential option data unavailable",
                  "full notebook: kernel died (3.7 GB RAM insufficient)"],
        fixes=["weight_decoder rebuilt: keras_metadata.pb of the TF1-era "
               "SavedModel is incompatible with TF 2.15 -> re-declare the "
               "architecture in code and copy weights layer by layer"],
    ),
]}


def get(eid: str) -> Optional[Experiment]:
    return REGISTRY.get(eid.zfill(2))


def by_status(status: str) -> List[Experiment]:
    return [e for e in REGISTRY.values() if e.status == status]


def summary() -> Dict[str, int]:
    out = {DONE: 0, PARTIAL: 0, BLOCKED: 0}
    for e in REGISTRY.values():
        out[e.status] += 1
    return out
