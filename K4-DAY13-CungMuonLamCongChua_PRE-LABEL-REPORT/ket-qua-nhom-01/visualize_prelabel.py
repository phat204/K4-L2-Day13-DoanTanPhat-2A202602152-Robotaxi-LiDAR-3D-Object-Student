from pathlib import Path
import csv
import json

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception as exc:  # pragma: no cover
    raise SystemExit(f'Matplotlib is required: {exc}')

base_dir = Path(__file__).resolve().parent
runs = []
for folder in ['run-A', 'run-B', 'run-C']:
    summary_path = base_dir / folder / 'summary.csv'
    with summary_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)
    runs.append({
        'label': folder.replace('run-', 'Run ').upper(),
        'name': folder,
        'delta': int(float(row['delta'])),
        'voxel': float(row['voxel_size']),
        'boxes': int(row['n_boxes']),
        'mean_z': float(row['mean_z']),
    })

manifest_path = base_dir / 'qc-cases' / 'manifest.json'
with manifest_path.open(encoding='utf-8') as f:
    manifest = json.load(f)

case_labels = ['correct', 'batch-z', 'one-box-z']
case_boxes = {
    'correct': 0,
    'batch-z': 13,
    'one-box-z': 1,
}
case_colors = ['#2ca02c', '#d62728', '#ff7f0e']

fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

# Left subplot: A/B/C comparison
labels = [r['label'] for r in runs]
box_counts = [r['boxes'] for r in runs]
mean_z = [r['mean_z'] for r in runs]

ax = axes[0]
bar = ax.bar(labels, box_counts, color=['#4C72B0', '#55A868', '#C44E52'], width=0.6)
ax.set_title('A/B/C: số hộp dự đoán theo cấu hình', fontsize=12, fontweight='bold')
ax.set_ylabel('Số hộp', color='#1f1f1f')
ax.set_ylim(0, max(box_counts) + 3)
for b, v in zip(bar, box_counts):
    ax.text(b.get_x() + b.get_width()/2, v + 0.3, str(v), ha='center', va='bottom', fontsize=10)

ax2 = ax.twinx()
ax2.plot(labels, mean_z, color='#B22222', marker='o', linewidth=2.5, markersize=8)
ax2.set_ylabel('mean_z', color='#B22222')

# Right subplot: QC cases
ax = axes[1]
case_values = [case_boxes[k] for k in case_labels]
ax.bar(case_labels, case_values, color=case_colors, width=0.6)
ax.set_title('QC cases: số hộp lệch z', fontsize=12, fontweight='bold')
ax.set_ylabel('Số hộp lệch')
ax.set_ylim(0, 14)
ax.set_xticks(range(len(case_labels)))
ax.set_xticklabels(['correct', 'batch-z', 'one-box-z'], rotation=0)
for i, v in enumerate(case_values):
    ax.text(i, v + 0.4, str(v), ha='center', va='bottom', fontsize=10)

fig.suptitle('PointPillars pre-label: A/B/C và QC cases', fontsize=16, fontweight='bold')
output_file = base_dir / 'prelabel-visualization.png'
plt.savefig(output_file, dpi=200)
print(f'Created visualization: {output_file}')
print('A/B/C:', runs)
print('QC:', case_boxes)
