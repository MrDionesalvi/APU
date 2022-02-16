from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date


from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from utils import *
import random

pdfmetrics.registerFont(TTFont('Plex', 'template/IBMPlexSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('PlexBold', 'template/IBMPlexSerif-Bold.ttf'))


def create_invoice(id, owner, amount, doc):
    outfile = "/home/dionesalvi/public_html/APU/assets/invoices/result_"+str(id)+".pdf"
    today = date.today()
    datetoPrint = today.strftime('%d-%m-%Y')

    template = PdfReader("template/APU.pdf", decompress=False).pages[0]
    template_obj = pagexobj(template)

    canvas = Canvas(outfile)

    xobj_name = makerl(canvas, template_obj)
    canvas.doForm(xobj_name)

    rows = [555]
    locations = {}

    for i in json.loads(get_Beehives(owner)):
        locations[rows[-1]] = i['name']
        rows.append(rows[-1]-50)
    
    rows.pop(-1)

    # Prepared by
    canvas.setFont('Plex', 12)
    canvas.drawString(130, 648, owner)
    canvas.drawString(130, 632, str(id))
    canvas.drawString(130, 616, doc)


    for i in locations:
        canvas.drawString(60, i, locations[i])

        canvas.drawString(175, i, "omiss")
        canvas.drawString(300, i, "omiss")
        """
        canvas.drawString(175, i, str(random.randrange(0, 20, 1))+"x Comuni")
        canvas.drawString(175, i-10, str(random.randrange(0, 20, 1))+"x Rare")
        canvas.drawString(175, i-20, str(random.randrange(0, 20, 1))+"x Preziose")
        canvas.drawString(175, i-30, str(random.randrange(0, 20, 1))+"x Nether")

        canvas.drawString(300, i, str(random.randrange(0, 20, 1))+" Alveari")
        canvas.drawString(420, i, str(random.randrange(0, 20000000, 1))+"IC")
        """
    canvas.drawString(420, rows[-1]-15, str(amount) +"IC")
    canvas.line(60, rows[-1]-35,535 , rows[-1]-35)

    canvas.setFont('PlexBold', 12)
    canvas.drawString(60, rows[-1]-55, "Totale da Pagare: " + str(amount) + "IC")
    canvas.drawString(60, rows[-1]-65, "Pagato attraverso conto nPay: APU")
    canvas.drawString(60, rows[-1]-80, "Fattura saldata il " + str(datetoPrint))



    canvas.save()
