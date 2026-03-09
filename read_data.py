import openpyxl

wb = openpyxl.load_workbook(r'C:\Users\samar\Downloads\Data_Lineage 1.xlsx')
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
print('Headers:', rows[0])
print('Row 1:', rows[1])
print('Total rows:', len(rows))
objs = set()
child_objs = set()
for row in rows[1:]:
    if row[1]: objs.add(str(row[1]).strip())
    if row[4]: child_objs.add(str(row[4]).strip())
print()
print('Parent Objects:')
for o in sorted(objs): print(' ', o)
print()
print('Child Objects:')
for o in sorted(child_objs): print(' ', o)
