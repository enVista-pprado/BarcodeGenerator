import pandas as pd
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

# ===================================================================
# GLOBAL CONFIGURATION
# ===================================================================

# PDF page dimensions (Letter size)
PAGE_WIDTH, PAGE_HEIGHT = letter

# Layout configuration for barcode grid
LEFT_MARGIN = 40                 # Left margin
ROW_HEIGHT = 150                 # Vertical space per barcode slot
COLUMNS_PER_ROW = 3              # Number of barcodes per row
BOTTOM_MARGIN = 120              # Page break trigger (y < this value)
GRID_START_Y = PAGE_HEIGHT - 100 # Where barcodes start under header

# Optional font path if you want to embed TTF fonts later
BARCODE_FONT_PATH = "fonts/DejaVuSans.ttf"


# ===================================================================
# BARCODE IMAGE GENERATION — WITHOUT EMBEDDED TEXT
# ===================================================================

def generate_barcode_image(value: str) -> Image.Image:
    """
    Generates a Code128 barcode PNG with *no human-readable text*.
    Returns a PIL Image object.
    """

    CODE = barcode.get_barcode_class("code128")
    buffer = io.BytesIO()

    # Ensure python-barcode NEVER adds text globally (failsafe)
    barcode.base.Barcode.default_writer_options['write_text'] = False

    # Custom writer to suppress internal text drawing
    class NoTextWriter(ImageWriter):
        def _write_text(self, code):
            return  # Override: disable writing text entirely

    writer = NoTextWriter()

    # Extra safety — prevent any unexpected text output
    writer.text = ""
    writer.set_options({
        "write_text": False,
        "font_size": 1,          # Ignored, but kept for clarity
        "text_distance": 10,     # Ignored
        "quiet_zone": 2,         # White space around barcode
        "module_height": 18,     # Height of bars
    })

    # Generate barcode into memory buffer
    CODE(value, writer=writer).write(buffer)
    buffer.seek(0)

    return Image.open(buffer)


# ===================================================================
# DRAW BARCODE (IMAGE + CUSTOM TEXT) ONTO PDF
# ===================================================================

def draw_barcode_on_pdf(c: canvas.Canvas, img: Image.Image, x: int, y: int, value: str):
    """
    Draws the barcode image (bars only) onto the PDF,
    then adds a human-readable label below it.
    """

    img_reader = ImageReader(img)

    # Scaling so all barcodes fit a consistent width
    MAX_WIDTH = 160
    img_width, img_height = img.size

    scale = MAX_WIDTH / img_width
    final_width = MAX_WIDTH
    final_height = img_height * scale

    # Draw barcode image (bars only)
    c.drawImage(img_reader, x, y - final_height, width=final_width, height=final_height)

    # Determine font size based on text length
    if len(value) <= 15:
        font_size = 12
    elif len(value) <= 25:
        font_size = 10
    elif len(value) <= 35:
        font_size = 8
    else:
        font_size = 6

    c.setFont("Helvetica", font_size)

    # Draw user-controlled human-readable text
    c.drawCentredString(
        x + final_width / 2,      # Center under barcode
        y - final_height - 12,    # Slightly below bars
        value
    )


# ===================================================================
# MAIN PDF GENERATION LOGIC
# ===================================================================

def generate_pdf_from_csv(csv_path: str, output_path: str = "output.pdf", columns_per_row: int = COLUMNS_PER_ROW):
    """
    Reads a CSV, and for each column:
        - creates a new page
        - prints the column name as a header
        - prints all values as barcodes arranged in a grid
    """

    df = pd.read_csv(csv_path)

    # PDF canvas
    c = canvas.Canvas(output_path, pagesize=letter)

    HEADER_FONT_SIZE = 28
    HEADER_Y = PAGE_HEIGHT - 80

    def draw_header(title: str):
        """Draw page header for each column."""
        c.setFont("Helvetica-Bold", HEADER_FONT_SIZE)
        c.drawCentredString(PAGE_WIDTH / 2, HEADER_Y, title)
        c.setFont("Helvetica", 12)

    # Iterate over each column → each becomes its own "section"
    for col_idx, column in enumerate(df.columns):

        # Start a new page except for the very first column
        if col_idx != 0:
            c.showPage()

        draw_header(column)
        current_row = 0

        # Convert column values to strings (barcodes require strings)
        values = df[column].astype(str)

        for i, value in enumerate(values):

            # Determine horizontal position (column index in the row)
            grid_col = i % columns_per_row

            # Compute coordinates for the barcode cell
            x = LEFT_MARGIN + (grid_col * ((PAGE_WIDTH - 2 * LEFT_MARGIN) / columns_per_row))
            y = GRID_START_Y - (current_row * ROW_HEIGHT)

            # If barcode would be too low, start a new page
            if y < BOTTOM_MARGIN:
                c.showPage()
                draw_header(column)
                current_row = 0
                y = GRID_START_Y
                grid_col = 0
                x = LEFT_MARGIN

            # Generate clean barcode (bars only)
            img = generate_barcode_image(value)

            # Draw barcode + human-readable text
            draw_barcode_on_pdf(c, img, x, y, value)

            # Move to next row after filling the last column
            if grid_col == columns_per_row - 1:
                current_row += 1

    c.save()
    print(f"PDF generated: {output_path}")


# ===================================================================
# RUN SCRIPT
# ===================================================================

if __name__ == "__main__":
    generate_pdf_from_csv("input.csv")
