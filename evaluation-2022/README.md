# Evaluation for SLAM Challenge 2022

## Quick start
```
python3 batch_evaluation.py <submission_path> <output_path> <groundtruth_path>
```

- submission_path: Folder containing your .txt trajectories in TUM format.
- output_path: Where CSV/PNG outputs are copied.
- groundtruth_path: Path to the groundtruth folder (for example: ../groundtruth_2022).

## Single pair evaluation
```
python3 evaluation.py <tum_est_file> <tum_ref_file>
```
This prints APE statistics and writes a plot to test.png in the current directory.

## Outputs
- results.csv with per-dataset metrics and totals.
- score.png and combined.png plus per-dataset plots.

