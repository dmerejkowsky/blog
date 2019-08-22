---
slug: "bibliotheques-tierces-python-2"
date: "2019-08-21T12:10:25.152448+00:00"
draft: true
title: "Utiliser des bibliothèques tierces avec Python - chapitre 2"
tags: ["python"]
authors: [dmerej]
feedback: true
summary: "Gestions des bibliothèques tierces en Python - pipenv, PYTHONPATH et autres"
---

Note: cet article fait suite à [Utiliser des bibliothèques tierces avec Python]({{< ref "0002-bibliotheques-tierces-python.md" >}}). Il est recommandé d'avoir lu celui-ci
auparavant.

# Compléments sur le méchanisme d'import de Python

## PYTHONPATH

Le comportement de l'interpréteur Python peut être modifié par plusieurs variables d'environnement.
TOOD: voir la liste complète dans la doc

PYTHONPATH est l'une de ces variables, et se comporte à peu près comme la variable d'environnement `$PATH`.

Elle peut contenir une liste de répertoires séparés par des `:`. Voici un example, en supposant qu'il existe un fichier `foo.py` dans le répertoire `toto` et un fichier `bar.py` dans un répertoire `tutu`

```
$ export PYTHONPATH=toto:tutu
$ python
> import foo
> foo
<module 'foo' from 'toto/foo.py'>
> import bar
> bar
<module 'bar' from 'tutu/bar.py'>
```

Cette technique peut avoir son intérêt dans quelques cas précis. Notez que vous pouvez obtenir un résultat équivalent en manipulant la variable `sys.path` directement:

```python
import sys

sys.path.insert(0, "toto")
import foo

sys.path.insert(0, "tutu")
import bar
```

Notez l'utilisation de 'insert(0)' pour être sûr que les répertoires qui nous intéressent apparaissent en premier dans la liste.

## fichiers .pth

## site.py

addsitedir

# Compléments sur `setup.py`

* `develop`
* `extras_require`

# Compléments sur `pip`

* `install -e`
* `requirements.txt`

# pipenv

Dans la première partie j'ai expliqué qu'il était préferable de toujours utiliser `pip` dans un virtualenv, et d'utiliser un virtualenv par projet et par version de python.

Admettons que vous vouliez travailler sur le projet `flask` avec Python3.7, et pour cela, lancer les tests du projet. Il va vous falloir:

* Créer un virtualenv spécifique à `flask` et `python 3.7`
* Activer ce virtualenv
* Installer les dépendances listées dans le fichier `setup.py` du projet `flask`
* Installer les dépendances spécifiques aux tests - donc typiquement, une *autre* liste que celle spécifiée dans la section `install_requires` de `setup.py`.

Voici ce que ça donnerait:

# pipenv
