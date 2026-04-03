from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from commandes.models import Order

@login_required
def generer_facture(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{order.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elements = []

    # Style titre
    style_titre = ParagraphStyle('titre',
        fontSize=24, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#C8102E'),
        spaceAfter=6, alignment=TA_CENTER)

    style_sous_titre = ParagraphStyle('sous_titre',
        fontSize=10, fontName='Helvetica',
        textColor=colors.HexColor('#666666'),
        spaceAfter=4, alignment=TA_CENTER)

    style_section = ParagraphStyle('section',
        fontSize=11, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0A0A0A'),
        spaceBefore=12, spaceAfter=6)

    style_normal = ParagraphStyle('normal',
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#333333'),
        spaceAfter=3)

    style_right = ParagraphStyle('right',
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#333333'),
        alignment=TA_RIGHT)

    # EN-TÊTE
    elements.append(Paragraph("Dulce y Fuego", style_titre))
    elements.append(Paragraph("Restaurant · Casablanca, Maroc", style_sous_titre))
    elements.append(Spacer(1, 0.5*cm))

    # Ligne rouge séparatrice
    table_ligne = Table([['']], colWidths=[17*cm], rowHeights=[2])
    table_ligne.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#C8102E')),
        ('LINEBELOW', (0,0), (-1,-1), 0, colors.white),
    ]))
    elements.append(table_ligne)
    elements.append(Spacer(1, 0.5*cm))

    # INFOS FACTURE
    elements.append(Paragraph("FACTURE", style_section))

    infos_data = [
        ['N° Facture :', f'FAC-{order.id:04d}',
         'Date :', order.created_at.strftime('%d/%m/%Y')],
        ['Client :', order.user.get_full_name() or order.user.username,
         'Statut :', order.get_statut_display()],
    ]
    if order.adresse_livraison:
        infos_data.append(['Adresse :', order.adresse_livraison, '', ''])

    table_infos = Table(infos_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    table_infos.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(table_infos)
    elements.append(Spacer(1, 0.8*cm))

    # TABLEAU DES ARTICLES
    elements.append(Paragraph("DÉTAIL DE LA COMMANDE", style_section))

    # En-tête du tableau
    articles_data = [['Plat', 'Quantité', 'Prix unitaire', 'Sous-total']]

    for item in order.order_items.all():
        articles_data.append([
            item.plat.nom,
            str(item.quantite),
            f'{item.prix} DH',
            f'{item.quantite * item.prix} DH',
        ])

    # Ligne total
    articles_data.append(['', '', 'TOTAL', f'{order.total} DH'])

    table_articles = Table(articles_data,
                           colWidths=[8*cm, 2.5*cm, 3.5*cm, 3*cm])
    table_articles.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A0A0A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),

        # Corps
        ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TEXTCOLOR', (0,1), (-1,-2), colors.HexColor('#333333')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),

        # Ligne totale
        ('BACKGROUND', (-2,-1), (-1,-1), colors.HexColor('#C8102E')),
        ('TEXTCOLOR', (-2,-1), (-1,-1), colors.white),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2,-1), (-1,-1), 10),

        # Grille
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#C8102E')),

        # Padding
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),

        # Alternance lignes
        ('ROWBACKGROUNDS', (0,1), (-1,-2),
         [colors.white, colors.HexColor('#F9F9F9')]),
    ]))
    elements.append(table_articles)
    elements.append(Spacer(1, 1*cm))

    # PIED DE PAGE
    table_pied = Table([[
        Paragraph('Merci pour votre confiance · Dulce y Fuego · contact@dulceyfuego.ma',
                  style_sous_titre)
    ]], colWidths=[17*cm])
    table_pied.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#C8102E')),
    ]))
    elements.append(table_pied)

    doc.build(elements)
    return response