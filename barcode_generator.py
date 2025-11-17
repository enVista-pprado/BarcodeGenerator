import pandas as pd
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

# =============================================================================
# GLOBAL CONSTANTS — PDF LAYOUT CONFIGURATION
# =============================================================================

PAGE_WIDTH, PAGE_HEIGHT = letter            # Letter-size page

LEFT_MARGIN = 40                             # Horizontal padding from left
ROW_HEIGHT = 150                             # Vertical spacing between barcode slots
COLUMNS_PER_ROW = 3                          # Number of barcodes per row
BOTTOM_MARGIN = 120                          # Page break threshold
GRID_START_Y = PAGE_HEIGHT - 100             # Vertical start of barcode grid

# (Optional) Path for custom fonts if used later
BARCODE_FONT_PATH = "fonts/DejaVuSans.ttf"


# =============================================================================
# BARCODE GENERATION (BARS-ONLY, NO HUMAN-READABLE TEXT)
# =============================================================================

def generate_barcode_image(value: str) -> Image.Image:
    """
    Generate a Code128 barcode image WITHOUT the built-in human-readable
    text that python-barcode normally prints. We override the writer to ensure
    no text is ever rendered, then return a clean PNG as a PIL Image.
    """
    CODE = barcode.get_barcode_class("code128")
    buffer = io.BytesIO()

    # Failsafe — permanently disable python-barcode's default text drawing
    barcode.base.Barcode.default_writer_options['write_text'] = False

    # Custom writer class that does NOT draw text at all
    class NoTextWriter(ImageWriter):
        def _write_text(self, code):
            return  # Override internal text rendering

    writer = NoTextWriter()

    # Additional writer options (mostly irrelevant since text is off)
    writer.text = ""
    writer.set_options({
        "write_text": False,
        "font_size": 1,
        "text_distance": 10,
        "quiet_zone": 2,
        "module_height": 18,
    })

    # Generate barcode into memory buffer
    CODE(value, writer=writer).write(buffer)
    buffer.seek(0)

    return Image.open(buffer)


# =============================================================================
# PDF DRAWING FUNCTIONS
# =============================================================================

def draw_barcode_on_pdf(c: canvas.Canvas, img: Image.Image, x: int, y: int, value: str):
    """
    Draw the barcode image onto the PDF and manually add a human-readable
    label underneath (our custom text). The barcode image contains bars only.
    """

    img_reader = ImageReader(img)

    # Scale barcode to a fixed width while preserving aspect ratio
    MAX_WIDTH = 160
    original_width, original_height = img.size
    scale = MAX_WIDTH / original_width

    final_width = MAX_WIDTH
    final_height = original_height * scale

    # Draw the barcode image
    c.drawImage(
        img_reader,
        x,
        y - final_height,
        width=final_width,
        height=final_height
    )

    # Choose font size based on text length (auto-shrinking)
    if len(value) <= 15:
        font_size = 12
    elif len(value) <= 25:
        font_size = 10
    elif len(value) <= 35:
        font_size = 8
    else:
        font_size = 6

    c.setFont("Helvetica", font_size)

    # Center the human-readable label below the barcode
    c.drawCentredString(
        x + final_width / 2,
        y - final_height - 12,
        value
    )


# =============================================================================
# MAIN PDF GENERATOR
# =============================================================================

def generate_pdf_from_csv(csv_path: str, output_path: str = "output.pdf", columns_per_row: int = COLUMNS_PER_ROW):
    """
    Convert a CSV into a multi-page barcode PDF.
    
    Each column in the CSV becomes its own section with:
    - A header (column name)
    - A grid of barcodes (bars + custom readable text)
    - Automatic page breaks when page is full
    """

    df = pd.read_csv(csv_path)
    c = canvas.Canvas(output_path, pagesize=letter)

    HEADER_FONT_SIZE = 28
    HEADER_Y = PAGE_HEIGHT - 80

    def draw_header(title: str):
        """Draw a page header with the column name."""
        c.setFont("Helvetica-Bold", HEADER_FONT_SIZE)
        c.drawCentredString(PAGE_WIDTH / 2, HEADER_Y, title)
        c.setFont("Helvetica", 12)

    # Each CSV column becomes its own pages
    for col_idx, column_name in enumerate(df.columns):

        # New page except on first column
        if col_idx != 0:
            c.showPage()

        draw_header(column_name)
        current_row = 0

        values = df[column_name].astype(str)

        for i, value in enumerate(values):
            grid_col = i % columns_per_row

            # Compute barcode coordinates
            x = LEFT_MARGIN + (grid_col * ((PAGE_WIDTH - 2 * LEFT_MARGIN) / columns_per_row))
            y = GRID_START_Y - (current_row * ROW_HEIGHT)

            # Page break check
            if y < BOTTOM_MARGIN:
                c.showPage()
                draw_header(column_name)
                current_row = 0
                y = GRID_START_Y
                grid_col = 0
                x = LEFT_MARGIN

            # Create barcode image
            img = generate_barcode_image(value)

            # Draw barcode + readable text
            draw_barcode_on_pdf(c, img, x, y, value)

            # Move to the next row after completing one row of columns
            if grid_col == columns_per_row - 1:
                current_row += 1

    c.save()
    print(f"PDF generated: {output_path}")
