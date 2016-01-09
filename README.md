# pdf2xmlOTE

pdf2xml Output Table Extractor est un outil pour extraire des tableaux du XML généré par "pdf2html -xml" au format CSV.

Il exploite les positions des cellules fournies par pdf2html (valeurs top et left).

Il utilise Beautifulsoup 4 avec lxml et fonctionne avec python 2.7

## Usage :

$ python parser.py -f file.xml > new_file.csv

## Usage avancé :

pdf2xmlOTE compte le nombre de cellules par lignes et utilise le nombre maximum trouvé pour créer une matrice de colonnes virtuelles. Dans certains cas difficiles il peut être utile de forcer un nombre de colonnes différent. Ceci peut être effectué avec le paramètre -n :

$ python parser.py -f file.xml -n 10 > new_file.csv

La matrice de colonnes virtuelle comporte pour chaque colonne un interval de positions possibles déterminé grâce aux valeurs de "left" fournies par pdf2html. Par exemple, une première colonne est détectée comme commencant à 90 pixels (du coté gauche de la page) et la suivante commence à 120 pixels. L'interval de positions possibles pour la 1ère colonne est donc de 90 à 119 pixels, ainsi toute cellule ayant pour valeur de left une valeur comprise dans cet interval sera assignée à cette colonne. Il est possible de décaler cette matrice avec une valeur en pixel via le paramètre -m :

$ python parser.py -f file.xml -m 10 > new_file.csv

Ceci a pour effet de décaler la matrice vers la gauche de 10 pixels (10 est d'ailleurs la valeur par défaut). L'interval de positions cité précédemment devient donc : de 80 à 109.

Ce paramètre peut prendre une valeur négative :

$ python parser.py -f file.xml -m -10 > new_file.csv

Ceci a pour effet de décaler la matrice vers la droite de 10 pixels. L'interval de positions cité précédemment devient donc : de 100 à 129.

Pour obtenir l'aide :

$ python parser.py -h

### Générer des XML avec pdf2html :

Comme pdf2xmlOTE essaye de générer les cellules vides non présentes dans la sortie de pdf2html, il est important de parser séparément des tableaux comportant des structures différentes.

Exemple :

Vous souhaitez obtenir les tableaux situés de la page 4 à 10 de votre document PDF. Les tableaux de la page 4 à 6 ne comportent pas le même nombre de colonnes que ceux des pages 7 à 10. Heureusement, pdf2html comporte les paramètres : -f (pour first) permettant d'indiquer la première page à extraire et -l (pour last) permettant d'indiquer la dernière page à extraire.

Vous procéderez donc en deux temps :

Obtenir les pages 4 à 6 :

$ pdf2html -xml -i -f 4 -l 6 fichier.pdf

Cette commande génère un fichier XML utilisable avec pdf2xmlOTE. Ce fichier portant le même nom que votre fichier PDF pensez donc à le renommer avant d'exécuter la commande suivante.

Obtenir les pages 7 à 10 :

$ pdf2html -xml -i -f 7 -l 10 fichier.pdf

Note : le paramètre -i utilisé dans cet exemple permet d'ignorer les images contenues dans le PDF.
