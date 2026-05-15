import os
folders = ['templates', 'css', 'js']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"✅ Created {folder} folder")
    else:
        print(f"✅ {folder} folder already exists")

print("\n📁 Current structure:")
print(f"  - {os.getcwd()}")
print(f"  - templates/ {'✅' if os.path.exists('templates') else '❌'}")
print(f"  - css/ {'✅' if os.path.exists('css') else '❌'}")
print(f"  - js/ {'✅' if os.path.exists('js') else '❌'}")

if os.path.exists('templates/login.html'):
    print(f"\n✅ login.html exists in templates folder")
else:
    print(f"\n❌ login.html NOT found in templates folder")
    print("Please create templates/login.html with the HTML code provided")