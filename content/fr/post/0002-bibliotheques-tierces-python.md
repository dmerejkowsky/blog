---
slug: "bibliotheques-tierces-python"
date: "2019-05-05T12:10:25.152448+00:00"
draft: false
title: "Utiliser des bibliothèques tierces avec Python"
tags: ["python"]
authors: [dmerej]
feedback: true
---

Note : cet article reprend en grande partie le cours donné à [l'École du Logiciel Libre](https://e2li.org) le 4 mai 2019.

Quelques rappels pour commencer.

# Importer un module

Soit le code suivant :

```python
import foo
foo.bar()
```

Ce code fonctionne s'il y a un ficher `foo.py` quelque part qui contient la fonction `bar` [^1]

Ce fichier peut être présent soit dans le répertoire courant, soit dans la bibliothèque standard Python.

# La variable PATH

Vous connaissez peut-être le rôle de la variable d'environnement `PATH`. Celle-ci contient une liste de chemins,
et est utilisée par votre shell pour trouver le chemin complet des commandes que vous lancez.

Par exemple:

```bash
PATH="/bin:/usr/bin:/usr/sbin"
$ ifconfig
# résout sur /usr/sbin/ifconfig
$ ls
# résout sur /bin/ls
```

Le chemin est "résolu" par le shell en parcourant la liste de tout les segments de `PATH`, et en regardant si le chemin complet
existe. La résolution s'arrête dès le premier chemin trouvé.

Par exemple, si vous avez `PATH="/home/user/bin:/usr/bin"` et un fichier `ls` dans `/home/user/bin/ls`, c'est ce fichier-là
(et non `/bin/ls`) qui sera utilisé quand vous taperez `ls`

# sys.path

En Python, c'est pareil. Il existe une variable prédéfinie dans le module `sys` qui contient une liste de chemins.

Si j'essaye de l'afficher sur mon Arch Linux, voici ce que j'obtiens :

```python
>>> import sys
>>> sys.path
[
 "",
 "/usr/lib/python3.7",
 "/usr/lib/python3.7/lib-dynload",
 "/home/dmerej/.local/lib/python3.7/",
 "/usr/lib/python3.7/site-packages",
]
```

Notez que le résultat dépend de ma distribution, et de la présence ou non du répertoire `~/.local/lib/python3.7/` sur ma machine - cela prouve que `sys.path` est construit dynamiquement par l'interpréteur Python.

Notez également que `sys.path` commence par une chaîne vide. En pratique, cela signifie que le répertoire courant a la priorité sur tout le reste.

Ainsi, si vous avez un fichier `random.py` dans votre répertoire courant, et que vous lancez un script `foo.py` dans ce même répertoire, vous vous retrouvez à utiliser le code dans `random.py`, et non celui de la bibliothèque standard, donc gardez cela en tête. Pour information, la liste de tous les modules de la bibliothèque standard est présente dans [la documentation](https://docs.python.org/fr/3/library/index.html).

Un autre aspect notable de `sys.path` est qu'il ne contient que deux répertoires dans lesquels mon utilisateur courant peut potentiellement écrire : le chemin courant et le chemin dans `~/.local/lib`. Tous les autres (`/usr/lib/python3.7/`, etc.) sont des chemins "système" et ne peuvent être modifiés que par un compte administrateur (avec `root` ou `sudo`, donc).

La situation est semblable sur macOS et Windows [^2].

# Bibliothèques tierces

Prenons un exemple :

```python
# dans foo.py
import tabulate

scores = [
  ["John", 345],
  ["Mary-Jane", 2],
  ["Bob", 543],
]
table = tabulate.tabulate(scores)
print(table)
```

```
$ python3 foo.py
---------  ---
John       345
Mary-Jane    2
Bob        543
---------  ---
```

Ici, le module `tabulate` n'est ni dans la bibliothèque standard, ni écrit par l'auteur du script `foo.py`. On dit que c'est une bibliothèque tierce.

On peut trouver [le code source de tabulate](https://bitbucket.org/astanin/python-tabulate/src/master/) facilement. La question qui se pose alors est: comment s'assurer que `sys.path` contient le module `tabulate`?

Eh bien, plusieurs solutions s'offrent à vous.

# Le gestionnaire de paquets

Si vous utilisez une distribution Linux, peut-être pourrez-vous utiliser votre gestionnaire de paquets :

```bash
$ sudo apt install python3-tabulate
```

Comme vous lancez votre gestionnaire de paquets avec `sudo`, celui-ci sera capable d'écrire dans les chemins système de `sys.path`.

# À la main

Une autre méthode consiste à partir des sources - par exemple, si le paquet de votre distribution n'est pas assez récent, ou si vous avez besoin de modifier les sources de la bibliothèque en question.

Voici une marche à suivre possible :

1. Récupérer les sources de la version qui vous intéresse dans la [section téléchargement de bitbucket](https://bitbucket.org/astanin/python-tabulate/downloads/?tab=tags).
1. Extraire l'archive, par exemple dans `src/tabulate`
1. Se rendre dans `src/tabulate` et lancer `python3 setup.py install --user`

# Anatomie du fichier setup.py

La plupart des bibliothèques Python contiennent un `setup.py` à
la racine de leurs sources. Il sert à plein de choses, la commande `install`
n'étant qu'une parmi de nombreuses autres possibles.


Le fichier `setup.py` contient en général simplement un `import` de `setuptools`, et un appel à la fonction `setup()`, avec de nombreux arguments:

```python
# tabulate/setup.py
from setuptools import setup
setup(
  name='tabulate',
  version='0.8.1',
  description='Pretty-print tabular data',
  py_modules=["tabulate"],
  scripts=["bin/tabulate"],
  ...
)
```


# Résultat de l'invocation de setup.py


Par défaut, `setup.py` essaiera d'écrire dans un des chemins système de
`sys.path` [^3], d'où l'utilisation de l'option `--user`.

Voici à quoi ressemble la sortie de la commande :

```bash
$ cd src/tabulate
$ python3 setup.py install --user
running install
...
Copying tabulate-0.8.4-py3.7.egg to /home/dmerej/.local/lib/python3.7/site-packages
...
Installing tabulate script to /home/dmerej/.local/bin
```


Notez que module a été copié dans `~/.local/lib/python3.7/site-packages/` et le script dans `~/.local/bin`. Cela signifie que *tous* les scripts Python lancés par l'utilisateur courant auront accès au module `tabulate`.

Notez également qu'un script a été installé dans `~/.local/bin` - Une bibliothèque Python peut contenir aussi bien des modules que des scripts.

Un point important est que vous n'avez en général pas besoin de lancer le script directement. Vous pouvez utiliser `python3 -m tabulate`. Procéder de cette façon est intéressant puisque vous n'avez pas à vous soucier de rajouter le chemin d'installation des scripts dans la variable d'environnement PATH.


# Dépendances

Prenons une autre bibliothèque: `cli-ui`.

Elle permet d'afficher du texte en couleur dans un terminal

```python
import cli_ui

cli_ui.info("Ceci est en", cli_ui.red, "rouge")
```

Elle permet également afficher des tableaux en couleur:

```python
headers=["name", "score"]
data = [
  [(bold, "John"), (green, 10.0)],
  [(bold, "Jane"), (green, 5.0)],
]
cli_ui.info_table(data, headers=headers)
```

Pour se faire, elle repose sur la bibliothèque `tabulate` vue précédemment. On dit que `cli-ui` *dépend* de `tabulate`.

# Déclaration des dépendances

La déclaration de la dépendance de `cli-ui` vers `tabulate` s'effectue également dans le fichier `setup.py`:

```python
setup(
  name="cli-ui",
  version="0.9.1",
  install_requires=[
     "tabulate",
     ...
  ],
  ...
)
```

# pypi.org

On comprend dès lors qu'il doit nécessairement exister un *annuaire* permettant de relier les noms de dépendances à leur code source.

Cet annuaire, c'est le site [pypi.org](https://pypi.org/). Vous y trouverez les pages correspondant à [tabulate](https://pypi.org/project/tabulate/) et [cli-ui](https://pypi.org/project/python-cli-ui/).

# pip

`pip` est un outil qui vient par défaut avec Python3[^4]. Vous pouvez également l'installer grâce au script [get-pip.py](https://bootstrap.pypa.io/get-pip.py), en lançant `python3 get-pip.py --user`.

Il est conseillé de *toujours* lancer `pip` avec `python3 -m pip`. De cette façon, vous êtes certains d'utiliser le module `pip` correspondant à votre binaire `python3`, et vous ne dépendez pas de ce qu'il y a dans votre `PATH`.

`pip` est capable d'interroger le site `pypi.org` pour retrouver les dépendances, et également de lancer les différents scripts `setup.py`.

Comme de nombreux outils, il s'utilise à l'aide de *commandes*. Voici comment installer `cli-ui` à l'aide de la commande 'install' de  `pip`:

```bash
$ python3 -m pip install cli-ui --user
Collecting cli-ui
...
Requirement already satisfied: unidecode in /usr/lib/python3.7/site-packages (from cli-ui) (1.0.23)
Requirement already satisfied: colorama in /usr/lib/python3.7/site-packages (from cli-ui) (0.4.1)
Requirement already satisfied: tabulate in /mnt/data/dmerej/src/python-tabulate (from cli-ui) (0.8.4)
Installing collected packages: cli-ui
Successfully installed cli-ui-0.9.1
```

On constate ici quelques limitations de `pip`:

* Il faut penser à utiliser `--user` (de la même façon que lorsqu'on lance `setup.py` à la main)
* Si le paquet est déjà installé dans le système, pip ne saura pas le mettre à jour - il faudra passer par le gestionnaire de paquet de
  la distribution

En revanche, `pip` contient de nombreuses fonctionnalités intéressantes:

* Il est capable de désinstaller des bibliothèques (à condition toutefois qu'elles ne soit pas dans un répertoire système)
* Il est aussi capable d'afficher la liste complète des bibliothèques Python accessibles  par l'utilisateur courant avec `freeze`.

Voici un extrait de la commande `python3 -m pip freeze` au moment de la rédaction de cet article sur ma machine:

```
$ python3 -m pip freeze
apipkg==1.5
cli-ui==0.9.1
gaupol==1.5
tabulate==0.8.4
```

On y retrouve les bibliothèques `cli-ui` et `tabulate`, bien sûr, mais aussi la bibliothèque `gaupol`, qui correspond au [programme d'édition de sous-titres](https://otsaloma.io/gaupol/) que j'ai installé à l'aide du gestionnaire de paquets de ma distribution. Précisons que les modules de la bibliothèque standard et ceux utilisés directement par pip sont omis de la liste.

On constate également que chaque bibliothèque possède un *numéro de version*

# Numéro de versions

Les numéros de versions remplissent plusieurs rôles, mais l'un des principaux usages et de spécifier des changements incompatibles.

Par exemple, pour `cli-ui`, la façon d'appeler la fonction `ask_choice` a changé entre les versions 0.7 et 0.8, comme le montre cet extrait du [changelog](https://tankerhq.github.io/python-cli-ui/changelog.html#v0-8-0):

> the list of choices used by ask_choice is now a named keyword argument:

```python
# Old (<= 0.7)
ask_choice("select a fruit", ["apple", "banana"])
# New (>= 0.8)
ask_choice("select a fruit", choices=["apple", "banana"])
```

Ceci s'appelle un *changement d'API*.

# Réagir aux changements d'API

Plusieurs possibilités:

* On peut bien sûr adapter le code pour utiliser la nouvelle API, mais cela n'est pas toujours possible ni souhaitable.
* Une autre solution est de spécifier des *contraintes* sur le numéro de version dans la déclaration des dépendances. Par exemple:

```python
setup(
  install_requires=[
    "cli-ui < 0.8",
    ...
  ]
)
```

# Aparté : pourquoi éviter sudo pip

Souvenez vous que les fichiers systèmes sont contrôlés par votre gestionnaire de paquet.

Les mainteneurs de votre distribution font en sorte qu'ils fonctionnent bien  les uns
avec les autres. Par exemple, le paquet `python3-cli-ui` ne sera mis à jour que lorsque tous les paquets qui en dépendent seront prêts à utiliser la nouvelle API.

En revanche, si vous lancez `sudo pip` (où `pip` avec un compte root), vous allez écrire dans ces mêmes répertoire et vous risquez de casser votre système.

Mais il y a un autre problème encore pire.

# Conflit de dépendances

Supposons deux projets A et B dans votre répertoire personnel. Ils dépendent tous les deux de `cli-ui`, mais l'un des deux utilise `cli-ui 0.7` et l'autre `cli-ui 0.9`.

Certains langages de programmation (rust et Javascript entre autres) autorisent la même bibliothèque a être utilisée dans plusieurs versions différentes, mais pas Python.

Que faire donc ?

# Environnements virtuels

La solution est d'utiliser un environnement virtuel (*virtualenv* en abrégé). C'est un répertoire *isolé* du reste du système.

Il se crée par exemple avec la commande `python3 -m venv foo-venv`. où `foo-venv` est un répertoire quelconque.

## Aparté : python3 -m venv sur Debian

La commande `python3 -m venv` fonctionne en général partout, dès l'installation de Python3 (*out of the box*, comme disent les Anglais), *sauf* sur Debian et ses dérivées [^5].

Si vous utilisez Debian, la commande pourrait ne pas fonctionner. En fonction des messages d'erreur que vous obtenez, il est possible de les contourner en:

* Installant le paquet `python3-venv`
* Ou en utilisant d'abord `pip` pour installer `virtualenv`, avec `python3 -m pip install virtualenv --user` puis lancer `python3 -m virtualenv foo-venv`.

## Comportement de python dans le virtualenv

Ce répertoire contient de nombreux fichiers et dossiers, et notamment un binaire dans `foo-venv/bin/python3`.

Voyons comment il se comporte en le comparant au binaire `/usr/bin/python3` habituel:

```
$ python3 -c 'import sys; print(sys.path)'
['',
  ...
 '/usr/lib/python3.7',
 '/usr/lib/python3.7.zip',
 '/usr/lib/python3.7/lib-dynload',
 '/home/dmerej/.local/lib/python3.7/site-packages',
 '/usr/lib/python3.7/site-packages'
]

$ /home/dmerej/foo-venv/bin/python -c 'import sys; print(sys.path)'
['',
 '/usr/lib/python3.7',
 '/usr/lib/python3.7.zip',
 '/usr/lib/python3.7/lib-dynload',
 '/home/dmerej/foo-venv/lib/python3.7/site-packages,
]
```

À noter:

* Le répertoire "global" dans `~/.local/lib` a disparu
* Seuls quelques répertoires systèmes sont présents (ils correspondent plus ou moins à l'emplacement des modules de la bibliothèque standard)
* Un répertoire *au sein* du virtualenv a été rajouté

Ainsi, l'isolation du virtualenv vient uniquement de la différence dans la valeur de `sys.path`.

Il faut aussi préciser que le virtualenv n'est pas complètement isolé du reste du système. En particulier, il dépend encore du binaire Python utilisé pour le créer.

Par exemple, si vous avec un binaire `/usr/local/bin/python3.8`, vous pourrez créer un virtualenv `foo-38` utilisant `Python3.8` qui fonctionnera tant que Python3.8 sera installé sur votre système en lançant `/usr/local/bin/python3.8 foo-3.8`.

Cela signifie également qu'il est possible qu'en mettant à jour le paquet `python3` sur votre distribution, vous risquez de casser les virtualenvs créés avec l'ancienne version du paquet.


## Comportement de pip dans le virtualenv

D'après ce qui précède, le virtualenv ne devrait contenir aucun module en dehors de la bibliothèque standard et de `pip` lui-même.

On peut le vérifier en lançant `python3 -m pip freeze` depuis le virtualenv et en vérifiant que rien ne s'affiche.

```
$ python3 -m pip freeze
# de nombreuse bibliothèques en dehors du virtualenv
apipkg==1.5
cli-ui==0.9.1
gaupol==1.5
tabulate==0.8.4

$ /home/dmerej/foo-venv/bin/python3 -m pip freeze
# rien :)
```

On peut alors utiliser le module `pip` du virtualenv pour installer des bibliothèques dans celui-ci:

```
$ /home/dmerej/foo-venv/bin/python3 -m pip install cli-ui
Collecting cli-ui
  Using cached https://files.pythonhosted.org/packages/37/74/051dfaa17fd87ca0e5e7ab08f6c675afd5c707d8d92c40db59573ac99914/cli_ui-0.9.1-py3-none-any.whl
Collecting colorama (from cli-ui)
  Using cached https://files.pythonhosted.org/packages/4f/a6/728666f39bfff1719fc94c481890b2106837da9318031f71a8424b662e12/colorama-0.4.1-py2.py3-none-any.whl
Collecting unidecode (from cli-ui)
  Using cached https://files.pythonhosted.org/packages/31/39/53096f9217b057cb049fe872b7fc7ce799a1a89b76cf917d9639e7a558b5/Unidecode-1.0.23-py2.py3-none-any.whl
Collecting tabulate (from cli-ui)
Installing collected packages: colorama, unidecode, tabulate, cli-ui
Successfully installed cli-ui-0.9.1 colorama-0.4.1 tabulate-0.8.3 unidecode-1.0.23
```

Cette fois, aucune bibliothèque n'est marquée comme déjà installée, et on récupère donc `cli-ui` et toutes ses dépendances.

On a enfin notre solution pour résoudre notre conflit de dépendances:
on peut simplement créer un virtualenv par projet. Ceci nous permettra
d'avoir effectivement deux versions différentes de `cli-ui`, isolées les
unes des autres.

# Activer un virtualenv

Devoir préciser le chemin du virtualenv en entier pour chaque commande peut devenir fastidieux.

Heureusement, il est possible *d'activer* un virtualenv, en lançant une des commandes suivantes:

* `source foo-venv/bin/activate` - si vous utilisez un shell POSIX
* `source foo-venv/bin/activate.fish` - si vous utilisez Fish
* `foo-venv\bin\activate.bat` - sous Windows

Une fois le virtualenv activé, taper `python`, `python3` ou `pip` utilisera les binaires correspondants dans le virtualenv automatiquement,
et ce, tant que la session du shell sera ouverte.

Le script d'activation ne fait en réalité pas grand chose à part modifier la variable `PATH` et rajouter le nom du virtualenv au début de l'invite de commande

Pour sortir du virtualenv, entrez la commande `deactivate`.

# Conclusion

Le système de gestions des dépendances de Python peut paraître compliqué et bizarre, surtout venant d'autres langages.

Mon conseil est de toujours suivre ces deux règles:

* Un virtualenv par projet et par version de Python
* Toujours utiliser `pip` *depuis* un virtualenv

Certes, cela peut paraître fastidieux, mais c'est une méthode qui vous évitera probablement de vous arracher les cheveux (croyez-en mon expérience).

Dans un futur article, nous approfondirons la question, en évoquant d'autres sujets comme `PYTHONPATH`, le fichier `requirements.txt` ou des outils comme `poetry` ou `pipenv`. À très vite.


[^1]: C'est une condition suffisante, mais pas nécessaire - on y reviendra.
[^2]: Presque. Il peut arriver que votre utilisateur courant ait les droits d'écriture dans tous les segments de `sys.path`, en fonction de votre installation de Python. Cela dit, vous retrouvez toujours un segment au sein du répertoire personnel de l'utilisateur courant.
[^3]: Cela peut vous paraître étrange à première vue. Il y a de nombreuses raisons historiques à se comportement, et il n'est pas sûr qu'il puisse être changé un jour.
[^4]: Presque. Parfois il faut installer un paquet supplémentaire, notamment sur les distributions basées sur Debian
[^5]: Je n'ai pas réussi à trouver une explication satisfaisante à ce choix des mainteneurs Debian. Si vous avez des informations à ce sujet, je suis preneur.
