import os
import shutil
from pathlib import Path

# 원본 루트 폴더
source_root = Path(r"Z:\연구2팀")

# 복사할 대상 폴더
destination = Path() / "설문지" / "연구2팀"

# 2018 ~ 2025까지 순회
for year in range(2018, 2026):
    
    year_folder = source_root / str(year) / "프로젝트"
    if not year_folder.exists():
        continue

    # 하위 프로젝트 폴더 탐색
    for project_path in year_folder.glob("*"):
        survey_path = project_path / "1. 설문지"
        if not survey_path.exists():
            continue

        # 설문지 폴더 안의 .hwp 파일 복사
        for hwp_file in survey_path.glob("*.hwp"):
            # 파일 이름이 중복되지 않도록 상위 폴더 경로 일부를 붙임
            relative_path = hwp_file.parent.relative_to(source_root)
            safe_name = str(relative_path).replace("\\", "_").replace("/", "_") + "_" + hwp_file.name
            destination_file = destination / safe_name

            shutil.copy2(hwp_file, destination_file)
            print(f"복사 완료: {os.path.basename(hwp_file)}")

print("\n✅ 모든 설문지 복사 완료!")
print(f"저장 위치: {destination}")
