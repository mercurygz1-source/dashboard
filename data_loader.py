import os
import glob
import openpyxl
import pandas as pd

BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

REMICON_FACTORIES = [
    '안양', '인천', '파주', '김포', '부산', '서부산', '김해',
    '정관', '양산', '창원', '대구', '울산', '아산', '전주',
    '군산', '원주', '제주'
]

REGION_ROWS = ['수도권', '영남권', '중부권', '레미콘 계']
SUMMARY_ROWS = ['건자재', '골재 계', '기타', '합계']


def get_available_years():
    years = []
    for name in os.listdir(BASE_PATH):
        full = os.path.join(BASE_PATH, name)
        if os.path.isdir(full) and name.isdigit() and len(name) == 4:
            years.append(name)
    return sorted(years, reverse=True)


def get_available_months(year):
    months = []
    year_folder = os.path.join(BASE_PATH, str(year))
    if not os.path.exists(year_folder):
        return months
    for f in os.listdir(year_folder):
        if f.startswith('손익보고서(') and f.endswith('.xlsx') and not f.startswith('~$'):
            try:
                month = f.split('-')[1].replace(').xlsx', '')
                months.append(int(month))
            except:
                pass
    return sorted(set(months))


def find_report_file(year, month):
    month_str = f"{int(month):02d}"
    path = os.path.join(BASE_PATH, str(year), f"손익보고서({year}-{month_str}).xlsx")
    return path if os.path.exists(path) else None


def load_factory_data(year, month):
    filepath = find_report_file(year, month)
    if not filepath:
        return None

    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)

    rows_data = []
    if '사업장별(당월)' in wb.sheetnames:
        ws = wb['사업장별(당월)']
        for row in ws.iter_rows(min_row=7, max_row=50, values_only=True):
            name = row[8]  # 공장명 (열 I)
            if name and isinstance(name, str):
                rows_data.append({
                    '공장명': name,
                    '물량_계획': row[9],
                    '물량_실적': row[10],
                    '물량_차이': row[11],
                    '물량_전년': row[12],
                    '매출_계획': row[14],
                    '매출_실적': row[15],
                    '매출_차이': row[16],
                    '매출_전년': row[17],
                    '영업이익_계획': row[19],
                    '영업이익_실적': row[20],
                    '영업이익_차이': row[21],
                    '영업이익_전년': row[22],
                    '판매단가_계획': row[24],
                    '판매단가_실적': row[25],
                    '판매단가_전년': row[26],
                    '변동비_계획': row[27],
                    '변동비_실적': row[28],
                    '변동비_전년': row[29],
                    '공헌이익_계획': row[30],
                    '공헌이익_실적': row[31],
                    '공헌이익_전년': row[32],
                })
    wb.close()

    df = pd.DataFrame(rows_data)
    df['연도'] = int(year)
    df['월'] = int(month)
    return df


def load_remicon_factories(year, month):
    df = load_factory_data(year, month)
    if df is None:
        return None
    return df[df['공장명'].isin(REMICON_FACTORIES)].copy()


def load_summary_data(year, month):
    df = load_factory_data(year, month)
    if df is None:
        return None
    summary_names = ['레미콘 계', '건자재', '골재 계', '기타', '합계']
    return df[df['공장명'].isin(summary_names)].copy()
