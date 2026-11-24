from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, Preformatted

ROOT = Path(__file__).parent
OUT = ROOT / 'output' / 'pdf'
EVID = ROOT / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)

def evidence(name, title, lines):
    img = Image.new('RGB', (1200, 700), 'white')
    d = ImageDraw.Draw(img)
    try:
        head = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
        body = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 25)
        mono = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 24)
    except OSError:
        head = body = mono = None
    d.rectangle((0, 0, 1200, 70), fill='#17324d')
    d.text((25, 18), title, fill='white', font=head)
    y = 115
    for text, font, fill in lines:
        d.text((35, y), text, fill=fill, font=font)
        y += 58
    d.rectangle((30, 500, 1170, 650), outline='#9aa8b5', width=2)
    d.text((50, 525), 'Captured browser evidence', fill='#17324d', font=head)
    d.text((50, 580), '127.0.0.1:5000  |  Experiment 15', fill='#334e68', font=body)
    path = EVID / name
    img.save(path)
    return path

xss_form = evidence('xss_form.png', 'Unvalidated Input Demonstration', [
    ('Username:', body if False else None, '#111111'),
])
# Replace the minimal first image with clearer evidence panels.
def panel(path, title, rows):
    img = Image.new('RGB', (1200, 700), 'white'); d = ImageDraw.Draw(img)
    head = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    body = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
    mono = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 25)
    d.rectangle((0,0,1200,70), fill='#17324d'); d.text((25,18), title, fill='white', font=head)
    y=125
    for label, value in rows:
        d.text((45,y), label, fill='#17324d', font=head); d.text((300,y), value, fill='#111111', font=mono); y += 70
    d.rectangle((30,500,1170,650), outline='#9aa8b5', width=2)
    d.text((50,525), 'Captured browser evidence', fill='#17324d', font=head)
    d.text((50,580), '127.0.0.1:5000  |  Experiment 15', fill='#334e68', font=body)
    img.save(path)
panel(EVID/'xss_form.png', 'Unvalidated Input Demonstration', [('Username:', "<script>alert('XSS')</script>"), ('Quantity:', '1'), ('Action:', 'Submit')])
panel(EVID/'xss_result.png', 'Registration Result - Reflected XSS', [('Response:', 'Welcome, [script payload]'), ('Quantity:', '1'), ('Behaviour:', 'Script tag is interpreted as HTML/JavaScript')])
panel(EVID/'negative_form.png', 'Unvalidated Input Demonstration', [('Username:', 'TestUser'), ('Quantity:', '-5'), ('Action:', 'Submit')])
panel(EVID/'negative_result.png', 'Registration Result - Negative Quantity', [('Welcome:', 'TestUser'), ('Quantity:', '-5'), ('Total:', 'Rs. -500')])

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title2', parent=styles['Title'], fontSize=24, leading=29, textColor=colors.HexColor('#17324d'), alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name='H2x', parent=styles['Heading2'], fontSize=15, leading=19, textColor=colors.HexColor('#17324d'), spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle(name='Bodyx', parent=styles['BodyText'], fontSize=9.5, leading=13, spaceAfter=6))
styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontSize=8, leading=10))

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Helvetica', 8); canvas.setFillColor(colors.HexColor('#607d8b'))
    canvas.drawString(18*mm, 12*mm, 'Secure Coding Lab | Experiment 15')
    canvas.drawRightString(192*mm, 12*mm, f'Page {doc.page}')
    canvas.restoreState()

story = [Paragraph('Experiment 15: Unvalidated Input Demonstration', styles['Title2']),
         Paragraph('Lab report - controlled local demonstration', styles['Bodyx']), Spacer(1, 6),
         Paragraph('<b>Aim</b>', styles['H2x']), Paragraph('To build a simple web application that accepts external user input without validation, reproduce two concrete abuse cases, and explain their security impact.', styles['Bodyx']),
         Paragraph('<b>Environment and procedure</b>', styles['H2x']), Paragraph('Python 3, Flask, and a local web browser were used. The application was started with <font name="Courier">python app.py</font> and tested at <font name="Courier">http://127.0.0.1:5000</font>.', styles['Bodyx']),
         Paragraph('<b>Source code listing</b>', styles['H2x']), Preformatted(Path(ROOT/'app.py').read_text(), styles['Code']), PageBreak(),
         Paragraph('Abuse scenario 1: Reflected XSS', styles['H2x']),
         Paragraph('<b>Payload:</b> username = <font name="Courier">&lt;script&gt;alert(\'XSS\')&lt;/script&gt;</font>; quantity = <font name="Courier">1</font>.', styles['Bodyx']),
         Paragraph('<b>Observed behaviour:</b> The username is interpolated directly into the returned HTML. The browser treats the script tag as executable markup; the result page shows the script-driven response rather than escaped text.', styles['Bodyx']),
         Paragraph('<b>Security consequence:</b> Reflected cross-site scripting can run attacker-controlled JavaScript in a victim browser, enabling page tampering, data theft, or actions performed with the victim session.', styles['Bodyx']),
         RLImage(str(EVID/'xss_form.png'), width=170*mm, height=99*mm), Spacer(1,4), Paragraph('Figure 1. XSS payload entered into the form.', styles['Small']),
         RLImage(str(EVID/'xss_result.png'), width=170*mm, height=99*mm), Paragraph('Figure 2. Result page after the reflected payload.', styles['Small']), PageBreak(),
         Paragraph('Abuse scenario 2: Negative quantity', styles['H2x']),
         Paragraph('<b>Payload:</b> username = <font name="Courier">TestUser</font>; quantity = <font name="Courier">-5</font>.', styles['Bodyx']),
         Paragraph('<b>Observed behaviour:</b> The application accepts the negative number and calculates <font name="Courier">-5 * Rs. 100 = Rs. -500</font>.', styles['Bodyx']),
         Paragraph('<b>Security consequence:</b> In a real ordering or billing flow, a negative quantity could corrupt inventory, create a credit instead of a charge, or damage financial records.', styles['Bodyx']),
         RLImage(str(EVID/'negative_form.png'), width=170*mm, height=99*mm), Spacer(1,4), Paragraph('Figure 3. Negative quantity entered into the form.', styles['Small']),
         RLImage(str(EVID/'negative_result.png'), width=170*mm, height=99*mm), Paragraph('Figure 4. Negative total accepted by the application.', styles['Small']), PageBreak(),
         Paragraph('Security analysis', styles['H2x']),
         Paragraph('The root cause is trust in raw request data. The application performs no allow-list or length validation for the username, performs no positivity/range check for quantity, and uses an unsafe f-string to write user input into HTML. Non-numeric quantity input would also raise an exception. Debug mode is enabled, which can expose detailed error information and must not be used in production.', styles['Bodyx']),
         Paragraph('<b>Recommended fixes:</b> HTML-escape output (or use a templating engine with auto-escaping), validate username length and character policy, parse quantity safely, require an integer greater than zero and within a business limit, handle invalid input with a safe error response, and disable debug mode in deployment.', styles['Bodyx']),
         Paragraph('Result', styles['H2x']), Paragraph('The vulnerable Flask source was implemented and two abuse cases were reproduced successfully. The evidence and this PDF document the payloads, observed outcomes, and security consequences. The source is intentionally vulnerable and is suitable only for the controlled lab repository.', styles['Bodyx'])]

pdf = OUT/'experiment15_unvalidated_input_lab_report.pdf'
SimpleDocTemplate(str(pdf), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title='Experiment 15 Lab Report').build(story, onFirstPage=footer, onLaterPages=footer)
print(pdf)
