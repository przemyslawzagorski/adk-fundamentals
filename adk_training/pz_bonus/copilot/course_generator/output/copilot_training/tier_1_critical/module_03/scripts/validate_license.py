import os
import sys

def validate_license(project_root):
    license_path = os.path.join(project_root, "LICENSE")
    if not os.path.exists(license_path):
        print(f"BŁĄD: Plik LICENCJI nie został znaleziony w katalogu głównym projektu: {project_root}", file=sys.stderr)
        print("Operacja Copilota została zablokowana. Utwórz plik LICENSE, aby kontynuować.", file=sys.stderr)
        sys.exit(1) # Zakończ z kodem błędu, aby zasygnalizować niepowodzenie hooka
    print(f"INFO: Plik LICENCJI znaleziony pod adresem: {license_path}")
    sys.exit(0) # Zakończ z kodem sukcesu

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python validate_license.py <project_root>", file=sys.stderr)
        sys.exit(1)
    project_root = sys.argv[1]
    validate_license(project_root)
