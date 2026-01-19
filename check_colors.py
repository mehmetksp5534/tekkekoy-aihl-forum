import sqlite3

c = sqlite3.connect('forum.db').cursor()
c.execute('SELECT id, name, color_code, gradient_code FROM background_colors')

print("Background Colors:")
print("=" * 80)
for row in c.fetchall():
    color_id, name, color_code, gradient_code = row
    grad = gradient_code[:60] + "..." if gradient_code and len(gradient_code) > 60 else gradient_code
    print(f"ID: {color_id} | Name: {name}")
    print(f"  Color: {color_code} | Gradient: {grad}")
    print()
