from pathlib import Path
import win32com.client as win32
import re 
import os
import shutil


# -----------------------
# 설문지 리스트 출력 및 복사
# -----------------------
root_folder = Path('./data/설문지')
sav_folder = root_folder / "PDF" / "전체"

# 존재하지 않으면 생성
sav_folder.mkdir(parents=True, exist_ok=True)

# 파일 복사
for dirpath, _, filenames in os.walk(root_folder):
    for filename in filenames:
        src = Path(dirpath) / filename  # 원본 파일 경로
        dst = sav_folder / filename     # 복사될 경로
        
        # 자기 자신(sav_folder) 내부 파일은 제외
        if sav_folder in src.parents:
            continue
        
        shutil.copy2(src, dst)  # 메타데이터 포함 복사
        print(f"복사 완료: {src} → {dst}")

print("모든 파일 복사 완료!")


# -----------------------
# HWP TO PDF 
# -----------------------

def hwp2pdf(folder_path, sav_path):
    
    # 한글 기본 설정 
    hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    #파일 경로
    source_folder = os.path.abspath(folder_path)
    files = [f for f in os.listdir(source_folder) if re.match('.*[.]hwp', f)]
    
    print(f'hwp file {len(files)}개 변환 시작')
    
    for file in files:
        hwp.Open(os.path.join(source_folder, file))  # 파일 열기

        # 저장 경로
        filename = os.path.abspath(os.path.join(sav_path, file).replace('hwp', 'pdf'))
        print(filename)
        
        # PDF 저장 
        act = hwp.CreateAction("Print")
        pset = act.CreateSet()
        act.GetDefault(pset)
        pset.SetItem("FileName", filename)  
        pset.SetItem("PrinterName", "Microsoft Print to PDF") 
        pset.SetItem("PrintMethod", 0)   
        act.Execute(pset)
        
        hwp.Run("FileClose")  
        
        print(f'{file} 변환 완료')

    hwp.Quit() 

pdf_folder = root_folder / "PDF"

hwp2pdf(sav_folder, pdf_folder)

# -----------------------
# PDF 파일 도메인별 폴더화
# -----------------------

base_dir = Path(r"C:\Users\rmsgh\Desktop\WIP\AutoSurvey-Agent\data\설문지")

hwp_root = base_dir / "HWP"
pdf_root = base_dir / "PDF"

# === HWP 파일 경로 매핑 (파일명 → 도메인)
hwp_map = {}

for domain_folder in hwp_root.iterdir():
    if domain_folder.is_dir():
        for hwp_file in domain_folder.glob("*.hwp"):
            name_key = hwp_file.stem.strip()  # 확장자 제외 이름
            hwp_map[name_key] = domain_folder.name

print(f"HWP 파일 매핑 완료 ({len(hwp_map)}건)")

# === PDF 파일 완전 일치 기반 이동
for pdf_file in pdf_root.glob("*.pdf"):
    pdf_key = pdf_file.stem.strip()
    
    if pdf_key in hwp_map:
        domain = hwp_map[pdf_key]
        dest_folder = pdf_root / domain
        dest_folder.mkdir(exist_ok=True)
        dest_path = dest_folder / pdf_file.name
        
        shutil.move(str(pdf_file), dest_path)
        print(f"이동 완료 → [{domain}] {pdf_file.name}")
    else:
        print(f"일치 없음 → {pdf_file.name}")

print("\n모든 PDF 분류 완료!")