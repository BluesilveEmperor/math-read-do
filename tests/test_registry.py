from fin_tool import registry as R


def test_ten_experiments():
    assert len(R.REGISTRY) == 10
    assert sorted(R.REGISTRY) == [f"{i:02d}" for i in range(1, 11)]


def test_status_counts_match_repro_status_md():
    s = R.summary()
    # 01,02,05,07,09 done | 03,04,10 partial | 06,08 blocked
    assert s == {R.DONE: 5, R.PARTIAL: 3, R.BLOCKED: 2}


def test_every_non_done_experiment_states_a_blocker():
    for e in R.REGISTRY.values():
        if e.status != R.DONE:
            assert e.blockers, f"{e.eid} has no blocker recorded"


def test_env_is_one_of_the_two_conda_envs():
    for e in R.REGISTRY.values():
        assert e.env in (R.ENV_TF, R.ENV_TORCH)


def test_experiment_07_metrics():
    e = R.get("7")
    assert e.name == "Network Superhedging"
    assert e.metrics["lam200_price"] == 1.3274
    assert e.metrics["lam200_hedge_prob"] == 0.4072
    assert e.metrics["params"] == 11191


def test_experiment_02_records_the_discriminator_fix():
    e = R.get("02")
    assert e.fixes and "input_dim" in e.fixes[0]


def test_by_status():
    assert {e.eid for e in R.by_status(R.BLOCKED)} == {"06", "08"}
