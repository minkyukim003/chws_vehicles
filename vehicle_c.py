# vehicle_c.py -----------------------------------------------------
import time, os

FRAME_INTERVAL = 0.1
RESULTS_FILE = "vehicle_c_results.csv"

def load_hazard_indices(path="./hazard_idx.txt"):
    with open(path, "r") as f:
        return [int(x.strip()) for x in f.readlines()]


def scenario_params(scenario, hazard_idx):
    if scenario == 1:
        return 0, hazard_idx - 50
    if scenario == 2:
        return 0, hazard_idx - 30
    if scenario == 3:
        return 0, hazard_idx - 20
    if scenario == 4:
        return 0, hazard_idx - 10
    if scenario == 5:
        return 0, hazard_idx


def run_trial(trial, hazard_idx, scenario):

    A_start, B_start = scenario_params(scenario, hazard_idx)
    B_start = max(B_start, 0)

    frames = hazard_idx - B_start
    t_local = frames * FRAME_INTERVAL

    print(f"\n[C] Trial {trial}")
    print(f"scenario={scenario}, hazard_idx={hazard_idx}, B_start={B_start}")
    print(f"[C] Local-only detection time = {t_local:.3f} sec")

    # Write to CSV
    with open(RESULTS_FILE, "a") as f:
        f.write(f"{trial},{scenario},{hazard_idx},{B_start},{t_local}\n")

    return t_local


def main():
    # Initialize CSV if not exists
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w") as f:
            f.write("trial,scenario,hazard_idx,B_start,t_local\n")

    hazard_list = load_hazard_indices("./hazard_idx.txt")
    scenario_list = [1,2,3,4,5]

    for trial, hazard_idx in enumerate(hazard_list, start=1):
        scenario = scenario_list[(trial-1) % 5]
        run_trial(trial, hazard_idx, scenario)


if __name__ == "__main__":
    main()
