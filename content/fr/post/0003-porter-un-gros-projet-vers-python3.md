---
authors: [dmerej]
slug: porter-un-gros-projet-vers-python3
date: 2017-07-09T11:38:15.606610+00:00
draft: true
title: Porter un gros project vers Python3
tags: ["python"]
---

# Port d'un gros projet vers Python3 - Retour d'expérience

## Introduction : le projet en question

Il s'agit d'une collection d'outils en ligne de commande que j'ai
développé dans mon ancienne boîte, les points importants étant

* la taille du projet: un peu moins de 30,000 lignes de code, et
* l'ancienneté du code: près de 6 ans, qui initialement a tourné avec Python 2.6 (eh oui)

## Le challenge

On veut garder la rétro-compat vers Python2.7, histoire que la transition
se fasse en douceur.

On veut aussi pouvoir continuer les développements en Python2 sans attendre
la fin du port.

## À faire avant de commencer à porter

### Visez la bonne version de Python

Déjà, si vous supportez à la fois Python2 et Python3, vous pouvez
(et devez) **ignorer les versions de Python comprises entre 3.0 et 3.2
inclus**.

Les utilisateurs de distros "archaïques" (genre Ubuntu 12.04)
avec un vieux Python3 pourront tout à fait continuer à utiliser la version Python2.

### Ayez une bonne couverture de tests

**Ne vous lancez pas dans le port sans une bonne couverture de tests**.

Les changements entre Python2 et Python3 sont parfois très subtils,
donc sans une bonne couverture de tests vous risquez d'introduire
pas mal de régressions.

Dans mon cas, j'avais une couverture de 80%, et la plupart des problèmes ont été
trouvés par les (nombreux) tests automatiques (un peu plus de 900)


## Le port proprement dit

### Marche à suivre

Voici les étapes que j'ai suivies. Il faut savoir qu'à la base je comptais
passer directement en Python3, sans être compatible Python2, mais en cours
de route je me suis aperçu que ça ne coûtait pas très cher de rendre
le code "polyglotte" (c'est comme ça qu'on dit) une fois le gros du travail
pour Python3 effectué.

1. Lancez `2to3` et faites un commit avec le patch généré
2. Lancez les tests en Python3 jusqu'à ce qu'ils passent tous
3. Relancez tous les tests en Python2, en utilisant `six` pour rendre
   le code polyglotte.
4. Assurez vous que tous les tests continuent à passer en Python3, commitez
   et poussez.

Note 1 : je ne connaissais pas [python-future](http://python-future.org/) à
l'époque. Il contient un outil appelé `futurize` qui transforme directement
du code Python2 en code polyglotte. Si vous avez des retours à faire sur cet
outil, partagez !

Note 2 : Vous n'êtes bien sûr pas obligés d'utiliser `six` si vous n'avez pas
envie. Vous pouvez vous en sortir avec des `if sys.version_info()[1] < 3`, et autres
`from __future__ import` (voir plus bas). Mais certaines fonctionnalités de `six`
sont compliquées à ré-implémenter à la main.

Note 3 : il existe aussi [pies](https://github.com/timothycrosley/pies)
comme alternative à `six`. Voir
[ici](https://github.com/timothycrosley/pies#how-does-pies-differ-from-six)
pour une liste des différences avec `six`. Personnellement, je trouve
`pies` un peu trop "magique" et je préfère rester explicite. De plus,
`six` semble être devenu le "standard" pour le code Python polyglotte.

Voyons maintenant quelques exemples de modifications à effectuer.

### print

C'est le changement qui a fait le plus de bruit. Il est très facile
de faire du code polyglotte quand on utilise `print`. Il suffit de faire le bon import au début du fichier.

```python
from __future__ import print


print("bar:", bar)
```

Notes:

* L'import de `__future__` doit être fait en premier

* Il faut le faire sur *tous* les fichiers qui utilisent `print`

* Il est nécessaire pour avoir le même comportement en Python2 et
  Pyton3. En effet, sans la ligne d'import, `print("bar:", "bar")` en
  Python2 est lu comme "afficher le tuple `("foo", bar)`", ce qui n'est
  probablement pas le comportement attendu.

### bytes, str, unicode

Ça c'est le gros morceau.

Il n'y a pas de solution miracle, partout où vous avez des chaînes de
caractères, il va falloir savoir si vous voulez une chaîne de caractères
"encodée" (`str` en Python2, `bytes` en Python3) ou "décodée" (`unicode` en
Python2, `str` en Python3)

Deux articles de Sam qui abordent très bien la question:


* [L'encoding en Python, une bonne fois pour toute](http://sametmax.com/lencoding-en-python-une-bonne-fois-pour-toute/)
* [En Python3 le type bytes est un tableau d'entiers](http://sametmax.com/en-python-3-le-type-bytes-est-un-array-dentiers/)

Allez les (re)-lire si c'est pas déjà fait.

En résumé :

* Utilisez UTF-8
* Décodez toutes les entrées
* Encodez toutes les sorties

J'ai vu conseiller de faire `from __future__ import unicode_literals`:

```python
# avec from __future__ import unicode_literals
a = "foo"
>>> type(a)
<type 'unicode'>

# sans
a = "foo"
>>> type(a)
<type 'str'>
```

Personnellement je m'en suis sorti sans. À vous de voir.

### Les imports relatifs et absolus

Personnellement, j'ai tendance à n'utiliser *que* des imports absolus.

Faisons l'hypothèse que vous avez installé un module externe `bar`,
dans votre système (ou dans votre virtualenv) et que vous avez déjà un fichier
`bar.py` dans vos sources.

Les imports absolus ne changent pas l'ordre de résolution quand
vous n'êtes pas dans un paquet. Si vous avez un fichier `foo.py` et un
fichier `bar.py` côte à côte, Python trouvera `bar` dans le répertoire courant.

En revanche, si vous avec une arborescence comme suit :

```
src
  foo
      __init__.py
      bar.py
```

Avec

```python
# in foo/__init__.py
import bar
```

En Python2, c'est `foo/bar.py` qui sera utilisé, et non `lib/site-packages/bar.py`. En Python3 ce sera l'inverse,
le fichier `bar.py`, *relatif* à `foo/__init__` aura la priorité.

Pour vous éviter ce genre de problèmes, utilisez donc :

```python
from __future__ import absolute_import

```

Ou bien rendez votre code plus explicite en utilisant un point :

```python
from . import bar

```

Vous pouvez aussi:

* Changer le nom de votre module pour éviter les conflits.
* Utiliser systématiquement `import foo.bar` (C'est ma solution
  préférée)

### La division

Même principe que pour `print`. Vous pouvez faire

```python
from __future__ import division
```

et ``/`` fera toujours une division flottante, même utilisé avec des entiers.

Pour retrouver la division entière, utilisez `//`.

Example:

```python
>>> 5/2
>>> 2.5

>>> 3
```

Note: celui-ci est assez vicieux à détecter ...

### Les changements de noms

De manière générale, le module `six.moves` contient tout ce qu'il faut
pour résoudre les problèmes de changement de noms.

Allez voir la table des cas traités par `six`
[ici](https://pythonhosted.org/six/#module-six.moves)

`six` est notamment indispensable pour supporter les métaclasses, dont
la syntaxe a complètement changé entre Python2 et Python3. (Ne vous amusez
pas à recoder ça vous-mêmes, c'est velu)

Avec `six`, vous pouvez écrire

```python
@six.add_metaclass(Meta)
class Foo:
    pass
```

### range et xrange

En Python2, `range()` est "gourmand" et retourne la liste entière dès qu'on
l'appelle, alors qu'en Python3, `range()` est "feignant" et retourne un
itérateur produisant les éléments sur demande. En Python2, si vous
voulez un itérateur, il faut utiliser `xrange()`.

Partant de là, vous avez deux solutions:

* Utiliser `range` tout le temps, même quand vous utilisiez
  `xrange` en Python2. Bien sûr il y aura un coût en performance, mais
  à vous de voir s'il est négligeable ou non.

* Ou bien utiliser `six.moves.range()` qui vous retourne un itérateur
  dans tous les cas.

```python
import six

my_iterator = six.moves.range(0, 3)
```


### Les "vues" des dictionnaires

On va prendre un exemple:

```python
my_dict = { "a" : 1 }
keys = my_dict.keys()
```

Quand vous lancez `2to3`, ce code est remplacé par:

```python
my_dict = { "a" : 1 }
keys = list(my_dict.keys())
```

C'est très laid :/

En fait en Python3, `keys()` retourne une "vue", ce qui est différent de
la liste que vous avez en Python2, mais qui est *aussi* différent de l'itérateur
que vous obtenez avec `iterkeys()` en Python2. En vrai ce sont des
[view objects](https://docs.python.org/2/library/stdtypes.html#dictionary-view-objects).

La plupart du temps, cependant, vous voulez juste itérer sur les clés
et donc je recommande d'utiliser `2to3` avec `--nofix=dict`.

Bien sûr, `keys()` est plus lent en Python2, mais comme pour
`range` vous pouvez ignorer ce détail la plupart du temps.

Faites attention cependant, le code plantera si vous faites :

```python
my_dict = { "a" : 1 }
keys = my_dict.keys()
keys.sort()
```

La raison est que les vues n'ont pas de méthode `sort`. À la place, utilisez :

```python
my_dict = { "a" : 1 }
keys = sorted(my_dict.keys())
```

Enfin, il existe un cas pathologique : celui où le dictionnaire change
pendant que vous itérez sur les clés, par exemple:

```python
for key in my_dict.keys():
    if something(key):
        del my_dict[key]
```

Là, pas le choix, il faut faire :

```python
for key in list(my_dict.keys()):
    if something(key):
        del my_dict[key]
```

Ou

```python
for key in list(six.iterkeys(my_dict)):
    if something(key):
        del my_dict[key]
```

si vous préférez.

### Les exceptions

En Python2, vous pouvez toujours écrire:

```python
raise MyException, message

try:
    # ....
except MyException, e:
    # ...
    # Do something with e.message
```

C'est une très vielle syntaxe.

Le code peut être réécrit comme suit, et sera polyglotte :

```python
raise MyException(message)

try:
    # ....
except MyException as e:
    # ....
    # Do something with e.args
```

Notez l'utilisation de `e.args` (une liste), et non
`e.message`. L'attribut `message` (une string) n'existe que dans
Python2. Vous pouvez utiliser `.args[0]` pour récupérer le message d'une
façon polyglotte.

### Comparer des pommes et des bananes

En `Python2`, tout est ordonné:

```python
>>> print sorted(["1", 0, None])
[None, 0, "1"]
```

L'interpréteur n'a aucun souci avec le fait que vous tentiez d'ordonner une
string et un nombre.


En Python3, ça crashe:
```
TypeError: '<' not supported between instances of 'int' and 'str'
```

Pensez y si vous avez des tris sur des classes à vous. La technique recommandée
c'est d'utiliser `@functools.total_ordering` et de définir `__lt__`:

```python
@functools.total_ordering
class MaClassPerso():
    ...

    def __lt__(self, other):
        return self.quelque_chose < other.quelque_chose

```

### Le ficher setup.py

Assurez vous de spécifier les versions de Python supportées dans votre
`setup.py`

Par exemple, si vous supportez à la fois Python2 et Python3, utilisez :

```python

from setuptools import setup, find_packages

setup(name="foo",
      # ...
      classifiers = [
        # ...
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
      ],
      # ...
)
```

Et ajoutez un `setup.cfg` comme suit :

```python
[bdist_wheel]
universal = 1
```

pour générer une `wheel` compatible Python2 et Python3.


## Deux trois mots sur l'intégration continue

Comme mentionné plus haut, le développement du projet a dû continuer
sans attendre que le support de Python3 soit mergé.

Le port a donc dû se faire dans une autre branche (que j'ai appelé `six`)

Du coup, comment faire pour que la branche 'six' reste à jour ?

La solution passe par l'intégration continue. Dans mon cas j'utilise
[jenkins](https://jenkins-ci.org/)

À chaque commit sur la branche de développement, voici ce qu'il se passe:

* La branche 'six' est rebasée
* Les tests sont lancés avec Python2 puis Python3
* La branche est poussée (avec `--force`).

Si l'une des étapes ne fonctionne pas (par exemple, le rebase ne
passe pas à cause de conflits, ou bien l'une des suites de test échoue),
l'équipe est prévenue par mail.

Ainsi la branche `six` continue d'être "vivante" et il est trivial et
sans risque de la fusionner dans la branche de développement au moment
opportun.

## Conclusion

J'aimerais remercier Eric S. Raymond qui m'a donné l'idée de ce billet suite
à [un article sur son blog](http://esr.ibiblio.org/?p=7039) et m'a autorisé
à contribuer à son
[HOWTO](http://www.catb.org/esr/faqs/practical-python-porting/), suite
à ma
[réponse](https://github.com/dmerejkowsky/response-to-practical-python-porting-by-esr)

N'hésitez pas en commentaire à partager votre propre expérience
(surtout si vous avez procédé différemment) ou vos questions, j'essaierai
d'y répondre.

Il vous reste jusqu'à la fin de l'année avant l'arrêt du support de Python2 en 2020,
et ce coup-là il n'y aura probablement pas de report.
