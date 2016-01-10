#!/usr/bin/env python
# -*- coding: utf8 -*-
import os, sys, io, csv, argparse
from bs4 import BeautifulSoup

# Paramètres

parser = argparse.ArgumentParser()

parser.add_argument('-f', '--file',
                    required=True,
                    type=str,
                    default=False,
                    dest="file",
                    metavar="<fichier xml à parser>",
                    help="Le fichier xml à parser. Celui-ci doit avoir été obtenu avec pdftohtml de poppler-utils en utilisant son paramètre ""xml"" (Ex: pdftohtml -xml -i fichier.pdf")

parser.add_argument('-n', '--nbcells',
                    required=False,
                    type=int,
                    default=False,
                    dest="nbcells",
                    metavar="<nombre de cellulles par lignes>",
                    help="Forcer un nombre de cellules attendu par ligne en cas de détection automatique erronée.")

parser.add_argument('-m', '--margin',
                    required=False,
                    type=int,
                    default=False,
                    dest="margin",
                    metavar="<marge des intervalles en nombre de pixels>",
                    help="Permet de choisir une marge en nombre de pixels pour décaler les intervalles de détection des colonnes (vaut 10 par défaut, peut prendre une valeur négative).\n\nExemple: Si une colonne est détectée à 90 pixels et une suivante à 120 pixels, avec une valeur de 10 pour ce paramètre, l'interval de détection de la 1ère colonne sera de 80 à 109 (90 - m = 80 et 120 - m - 1 = 109). Toutes les cellulles dont le début est situé entre ces valeurs sera attribué à la première colonne, etc. Par défaut ce paramètre vaut 10.")

parser.add_argument('-s', '--showgrid',
                    required=False,
                    default=False,
                    dest="showgrid",
                    action='store_const',
                    const=True,
                    metavar="<Afficher matrice>",
                    help="Générer une image SVG de la matrice des colonnes. Visible dans un navigateur web via le fichier grid.html")

args = parser.parse_args()

# Récupérer et stocker les données dans "data"

soup = BeautifulSoup(open(args.file), "lxml-xml")

data = {}

for page in soup.find_all('page'):

  pgnb = int(page.get('number'))
  pgheight = int(page.get('height'))
  pgwidth = int(page.get('width'))

  data[pgnb] = {}

  for text in page.find_all('text'):

    top = int(text.get('top'))

    if data[pgnb].has_key(top) is False:
      data[pgnb][top] = {}

    left = int(text.get('left'))

    data[pgnb][top][left] = text.get_text()

# Nombre de cellules par ligne attendu (via paramètre -n ou par défaut le maximum détecté)

if args.nbcells is False:
  nbcells = 0
  for page in data:
    for line in data[page]:
      cells = len(data[page][line])
      if nbcells < cells:
        nbcells = cells
else:
  nbcells = args.nbcells

# Récuperer les positions approximatives des colonnes

poscols = {}

for page in data:
  for line in data[page]:
    for cell in data[page][line]:
      if poscols.has_key(cell) is False:
        poscols[cell] = 1
      else:
        poscols[cell] += 1

cols = []

# On prend les plus fréquentes en limitant au nombre de cellules attendu

for cell in sorted(poscols, key=poscols.get, reverse=True):
  if len(cols) < nbcells:
    cols.append(cell)

cols.sort()

# Créer des intervalles mini/maxi des positions possibles (forcer une marge avec le paramêtre -m ou 10 pixels par défaut)

if args.margin is False:
  margin = 10
else:
  margin = args.margin

ranges = {}

for k, col in enumerate(cols):
  mini = col-margin
  if k == 0:
    mini = 0
  try:
    maxi = cols[k+1]-margin-1
  except IndexError:
    maxi = col*2
  ranges[col] = {'mini': mini, 'maxi': maxi}

# Trier et afficher les données

sorted_data = sorted(data)

for page in sorted_data:

  sorted_page = sorted(data[page])

  for line in sorted_page:

    sorted_line = sorted(data[page][line])

    nb = len(sorted_line)

    row = {}

    # S'il y a moins de cellules que prévu

    if nb < nbcells:

      # On crée une structure vide avec autant de colonnes qu'attendu

      for r in ranges:
        row[r] = ''

      # Qu'on remplit avec les valeurs selon leurs positions

      for cell in sorted_line:

        ok = False

        for r in ranges:

          if cell >= ranges[r]['mini'] and cell <= ranges[r]['maxi']:

            row[r] = data[page][line][cell]

            ok = True

        if ok is False:
          print(cell)
          print("Not found in ranges")

    else:

      for cell in sorted_line:

        row[cell] = data[page][line][cell]

    output = io.BytesIO()
    writer = csv.DictWriter(output, fieldnames=sorted(row.keys()), quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow({k:v.encode('utf8') for k,v in row.items()})
    print(output.getvalue().strip())

if args.showgrid:

  soup = BeautifulSoup(open('blank_grid.svg'), "lxml-xml")

  tag = soup.svg
  tag['height'] = '200px'
  tag['width'] = str(pgwidth)+'px'

  cols = soup.find_all(id="cols")[0]

  i = 1

  for r in ranges:
    if ranges[r]['mini'] + (ranges[r]['maxi']-ranges[r]['mini']) > pgwidth:
      colwidth = pgwidth - ranges[r]['mini']
    else:
      colwidth = ranges[r]['maxi']-ranges[r]['mini']

    new_col = soup.new_tag("rect", title=str(ranges[r]['mini'])+" <-> "+str(ranges[r]['maxi']), x=ranges[r]['mini'] , y="0" , height="200px" , width=colwidth , id="colid_"+str(i) , style="fill:none;stroke:blue;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1")
    cols.append(new_col)
    i += 1

  with open("grid.svg", "wb") as file:
    file.write(soup.prettify("utf-8"))

  soup = BeautifulSoup(open('grid.html'), "lxml-xml")

  embed = soup.find_all('embed')[0]
  embed['src'] = os.path.splitext(os.path.split(args.file)[1])[0]+'.pdf'

  with open("grid.html", "wb") as file:
    file.write(soup.prettify("utf-8"))









