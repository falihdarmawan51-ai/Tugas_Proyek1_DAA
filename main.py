"""
Program DAA - Kasus C: Rekonsiliasi Finansial (Dirty OCR)
Algoritma:
1. Membaca dataset token dari file teks.
2. Menghitung jarak edit menggunakan Levenshtein (Dynamic Programming).
3. Membangun BK-Tree untuk pencarian token dengan jarak <= 1.
4. Mengurutkan hasil menggunakan Merge Sort.

Cara menjalankan:
- Simpan file ini dengan nama main.py.
- Letakkan file "contoh code03.txt" di folder yang sama dengan main.py.
- Buka folder tersebut di VS Code.
- Jalankan: python main.py
"""

from pathlib import Path


DATASET_NAME = "contoh code03.txt"
REFERENCE_CODES = [
    "0000OOOO",
    "3M2I3QM6",
    "4ORAC8CY",
]
MAX_DISTANCE = 1


def levenshtein(a: str, b: str) -> int:
    """Menghitung jarak Levenshtein dengan DP dua baris."""
    previous = list(range(len(b) + 1))

    for i, char_a in enumerate(a, start=1):
        current = [i] + [0] * len(b)

        for j, char_b in enumerate(b, start=1):
            cost = 0 if char_a == char_b else 1
            current[j] = min(
                current[j - 1] + 1,       # insertion
                previous[j] + 1,          # deletion
                previous[j - 1] + cost,   # substitution
            )

        previous = current

    return previous[-1]


class BKNode:
    """Satu simpul pada BK-Tree."""

    def __init__(self, token: str, index: int):
        self.token = token
        self.indices = [index]
        self.children = {}


class BKTree:
    """BK-Tree untuk mencari string berdasarkan jarak Levenshtein."""

    def __init__(self):
        self.root = None

    def insert(self, token: str, index: int) -> None:
        """Memasukkan token ke pohon."""
        if self.root is None:
            self.root = BKNode(token, index)
            return

        current = self.root

        while True:
            distance = levenshtein(token, current.token)

            # Jika token sudah ada, simpan indeks tambahannya.
            if distance == 0:
                current.indices.append(index)
                return

            if distance not in current.children:
                current.children[distance] = BKNode(token, index)
                return

            current = current.children[distance]

    def search(self, query: str, radius: int = 1):
        """
        Mencari token yang jaraknya <= radius.
        Mengembalikan (hasil, jumlah_node_dikunjungi).
        """
        results = []
        visited_nodes = 0

        if self.root is None:
            return results, visited_nodes

        stack = [self.root]

        while stack:
            node = stack.pop()
            visited_nodes += 1

            distance = levenshtein(query, node.token)

            if distance <= radius:
                for index in node.indices:
                    results.append({
                        "token": node.token,
                        "index": index,
                        "distance": distance,
                    })

            # Sifat metrik BK-Tree: hanya cabang dalam rentang ini
            # yang mungkin memiliki kandidat dengan jarak <= radius.
            lower_bound = distance - radius
            upper_bound = distance + radius

            for edge_distance, child in node.children.items():
                if lower_bound <= edge_distance <= upper_bound:
                    stack.append(child)

        return results, visited_nodes


def merge_sort(items):
    """Mengurutkan hasil berdasarkan jarak, lalu nomor baris."""
    if len(items) <= 1:
        return items

    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])

    return merge(left, right)


def merge(left, right):
    """Menggabungkan dua bagian yang sudah terurut."""
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        key_left = (left[i]["distance"], left[i]["index"])
        key_right = (right[j]["distance"], right[j]["index"])

        if key_left <= key_right:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def load_dataset(file_path: Path):
    """Membaca satu token per baris dari file dataset."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: {file_path}\n"
            f"Pastikan '{DATASET_NAME}' berada di folder yang sama dengan main.py."
        )

    tokens = []
    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            token = line.strip().upper()

            # Abaikan baris kosong.
            if not token:
                continue

            # Dataset kasus ini menggunakan A-Z dan 0-9.
            if not all(char.isalnum() and char.isascii() for char in token):
                print(
                    f"Peringatan: baris {line_number} dilewati "
                    f"karena berisi karakter yang tidak sesuai: {token}"
                )
                continue

            tokens.append((token, line_number))

    return tokens


def main():
    print("=" * 65)
    print("PROGRAM DAA - KASUS C: REKONSILIASI FINANSIAL (DIRTY OCR)")
    print("=" * 65)

    # Cari dataset di folder yang sama dengan file main.py.
    dataset_path = Path(__file__).resolve().parent / DATASET_NAME

    try:
        dataset = load_dataset(dataset_path)
    except (FileNotFoundError, OSError) as error:
        print(f"\nERROR: {error}")
        input("\nTekan Enter untuk keluar...")
        return

    if not dataset:
        print("Dataset kosong. Tidak ada data yang dapat diproses.")
        input("\nTekan Enter untuk keluar...")
        return

    print(f"\nDataset berhasil dibaca : {DATASET_NAME}")
    print(f"Jumlah token             : {len(dataset)}")
    print("Sedang membangun BK-Tree...")

    tree = BKTree()
    for token, line_number in dataset:
        tree.insert(token, line_number)

    print("BK-Tree berhasil dibuat.")

    print("\nPOLA REFERENSI YANG DIUJI")
    print("-" * 65)

    for query in REFERENCE_CODES:
        print(f"\nPola referensi: {query}")

        results, visited = tree.search(query, MAX_DISTANCE)
        sorted_results = merge_sort(results)

        print(f"Node BK-Tree dikunjungi: {visited}")
        print(f"Jumlah hasil ditemukan: {len(sorted_results)}")

        if not sorted_results:
            print("Tidak ditemukan token dengan jarak edit <= 1.")
            continue

        print("\nHasil pencarian:")
        print(f"{'No.':<5}{'Token':<15}{'Baris dataset':<18}{'Jarak edit':<12}")
        print("-" * 50)

        for number, result in enumerate(sorted_results, start=1):
            print(
                f"{number:<5}"
                f"{result['token']:<15}"
                f"{result['index']:<18}"
                f"{result['distance']:<12}"
            )

    print("\n" + "=" * 65)
    print("Program selesai.")
    print("=" * 65)
    input("\nTekan Enter untuk menutup program...")


if __name__ == "__main__":
    main()
