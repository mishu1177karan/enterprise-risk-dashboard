f = open('app.py', 'r', encoding='utf-8')
content = f.read()
f.close()

content = content.replace('—', '-')
content = content.replace('≥', '>=')
content = content.replace('≤', '<=')
content = content.replace('→', '->')
content = content.replace('←', '<-')

f = open('app.py', 'w', encoding='utf-8')
f.write(content)
f.close()

print('Done! All fixed.')
