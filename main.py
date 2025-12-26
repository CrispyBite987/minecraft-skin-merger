import os
from tkinter import Tk, filedialog, messagebox, BooleanVar
from tkinter import ttk
from PIL import Image


# ================== OVERLAY MAPS ==================

HEAD_OVERLAY = [
    (8, 0, 40, 0, 8, 8),
    (16, 0, 48, 0, 8, 8),
    (0, 8, 32, 8, 8, 8),
    (8, 8, 40, 8, 8, 8),
    (16, 8, 48, 8, 8, 8),
    (24, 8, 56, 8, 8, 8),
]


# ================== CORE LOGIC ==================

def merge_overlay(img, regions):
    pixels = img.load()
    w, h = img.size

    for bx, by, ox, oy, rw, rh in regions:
        for y in range(rh):
            for x in range(rw):
                sx, sy = ox + x, oy + y
                dx, dy = bx + x, by + y

                if not (0 <= sx < w and 0 <= sy < h):
                    continue
                if not (0 <= dx < w and 0 <= dy < h):
                    continue

                r, g, b, a = pixels[sx, sy]
                if a > 0:
                    pixels[dx, dy] = (r, g, b, a)

                pixels[sx, sy] = (0, 0, 0, 0)


def keep_only_head(img):
    pixels = img.load()
    for y in range(64):
        for x in range(64):
            if not (0 <= x < 32 and 0 <= y < 16):
                pixels[x, y] = (0, 0, 0, 0)


def process_skin(path, out_path, head_only):
    img = Image.open(path).convert("RGBA")

    if img.size != (64, 64):
        return

    merge_overlay(img, HEAD_OVERLAY)

    if head_only:
        keep_only_head(img)

    img.save(out_path, "PNG")


# ================== MODERN UI ==================

class App:
    def __init__(self, root):
        self.root = root
        root.title("Minecraft Skin Merger")
        root.resizable(False, False)

        self.paths = []
        self.head_only = BooleanVar()

        style = ttk.Style()
        style.theme_use("clam")

        main = ttk.Frame(root, padding=16)
        main.grid()

        title = ttk.Label(
            main,
            text="Minecraft Skin Merger",
            font=("Segoe UI", 14, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 12))

        ttk.Button(main, text="Select Image", command=self.one_file)\
            .grid(row=1, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(main, text="Select Folder", command=self.folder)\
            .grid(row=1, column=1, sticky="ew")

        options = ttk.LabelFrame(main, text="Options", padding=10)
        options.grid(row=2, column=0, columnspan=2, pady=12, sticky="ew")

        ttk.Checkbutton(
            options,
            text="After merging keep only head",
            variable=self.head_only
        ).grid(sticky="w")

        actions = ttk.Frame(main)
        actions.grid(row=3, column=0, columnspan=2, sticky="ew")

        ttk.Button(actions, text="Save", command=lambda: self.run(False))\
            .grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(actions, text="Save As", command=lambda: self.run(True))\
            .grid(row=0, column=1, sticky="ew")

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)


    def one_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("PNG images", "*.png")]
        )
        self.paths = [path] if path else []


    def folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.paths = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(".png")
        ]


    def run(self, save_as):
        if not self.paths:
            messagebox.showerror("Error", "No files selected")
            return

        if save_as:
            out_dir = filedialog.askdirectory()
            if not out_dir:
                return
        else:
            base = os.path.dirname(os.path.abspath(__file__))
            out_dir = os.path.join(base, "edited")
            os.makedirs(out_dir, exist_ok=True)

        for path in self.paths:
            out_path = os.path.join(out_dir, os.path.basename(path))
            process_skin(path, out_path, self.head_only.get())

        messagebox.showinfo("Done", "Processing complete")


# ================== RUN ==================

if __name__ == "__main__":
    root = Tk()
    App(root)
    root.mainloop()
