---
authors: [dmerej]
slug: tester-en-python-pytest-et-tdd
date: 2019-06-01T17:21:28.749210+00:00
draft: false
title: "Écriture de tests en Python: pytest et TDD"
tags: [python]
---


Note&nbsp;: cet article reprend en grande partie le cours donné à [l'École
du Logiciel Libre](https://e2li.org) le 18 mai 2019.
Il s'inspire également des travaux de Robert C. Martin (alias Uncle Bob) sur la question,
notamment sa série de vidéos sur
[cleancoders.com](https://cleancoders.com/videos/clean-code) [^1]


# Assertions

En guise d'introduction, penchons-nous un peu sur le mot-clé `assert`.

```python
def faire_le_café(au_régime=False, sucre=True):
     if au_régime:
         assert not sucre

```

Que se passe-t-il lorsque ce code tourne avec `au_régime` à `True` et `sucre` à `True`&nbsp;?

```python
>>> faire_le_café(au_régime=True, sucre=True)
Traceback (most recent call last):
  File "foo.py", line 7, in <module>
    faire_le_café()
  File "foo.py", line 5, in faire_le_café
    assert not sucre
AssertionError
```


On constate que `assert` a évalué la condition et comme celle-ci était "falsy", il a levé une exception nommée `AssertionError`

On peut modifier le message de l'assertion en rajoutant une chaîne de caractères après la virgule&nbsp;:

```python
def faire_le_café(au_régime=False, sucre=True):
     if au_régime:
         assert not sucre, "tu es au régime: pas de sucre dans le café!"
```

Et on peut aussi vérifier que `assert` ne fait rien si la condition est "truthy":

```python
>>> x = 42
>>> assert x
# rien
```


# À quoi servent les assertions

Comme on l'a vu, utiliser `assert` ressemble fortement à lever une exception. Dans les deux cas, on veut signaler
à celui qui appelle notre code que quelque chose ne va pas. Mais `assert` est différent par deux aspects&nbsp;:

* Il peut arrive que la ligne contenant `assert` soit tout simplement ignorée [^8].
* `assert` et souvent utilisé pour signaler qu'il y a une erreur *dans le code* qui a appelé la fonction, et
  non à cause d'une erreur "extérieure"

Voir [cet article de Sam & Max](http://sametmax.com/programmation-par-contrat-avec-assert/) pour plus de détails.

# Qu'est-ce qu'un test&nbsp;?

Voici un exemple minimal&nbsp;:

```python
# dans calc.py
def add_one(x):
     return x + 2
```

```python
# dans test_calc.py
import calc

result = calc.add_one(3)
assert result == 4, "result != 4"
```

On retrouve l'idée d'utiliser `assert` pour indiquer une erreur *interne* au code. En l'occurrence, si on lance le script `test_calc.py`, on va obtenir&nbsp;:

```bash
$ python3 test_calc.py
Traceback (most recent call last):
  File "test_calc.py", line 4, in <module>
    assert result == 4, "result != 4"
AssertionError: result != 4
```

Notez que le message d'erreur ne nous indique pas la *valeur effective* de `result`, juste sa *valeur attendue*.

Quoi qu'il en soit, le code dans `test_calc.py` nous a permis de trouver un bug dans la fonction `add_one` de  `calc.py`

# Code de test et code de production

On dit que `calc.py` et le code *de production*, et `test_calc.py` le code *de test*. Comme son nom l'indique, le code de production sert de base à un *produit* - un programme, un site web, etc.

On sépare souvent le code de production et le code de test dans des fichiers différents, tout simplement parce que le code de test ne sert pas directement aux utilisateurs du produit. Le code de test ne sert en général qu'aux *auteurs* du code.

# Les deux valeurs du code

Une petite digression s'impose ici. Selon Robert C. Martin, le code possède une *valeur primaire* et une *valeur secondaire*.

* La valeur primaire est le *comportement* du code - ce que j'ai appelé le *produit* ci-dessus
* La valeur secondaire est le fait que le code (et donc le produit) peut être *modifié*.

Selon lui, la valeur secondaire (en dépit de son nom) est la plus importante&nbsp;: dans `software`, il y a "soft", par opposition à `hardware`. Si vous avez un produit qui fonctionne bien mais que le code est impossible à changer, vous
risquez de vous faire de ne pas réussir à rajouter de nouvelles fonctionnalités,
de ne pas pouvoir corriger les bugs suffisamment rapidement, et de vous faire dépasser par la concurrence.

Ainsi, si le code de test n'a *a priori* pas d'effet sur la valeur *primaire* du code (après tout, l'utilisateur
du produit n'est en général même pas *conscient* de son existence), il a un effet très important sur la valeur *secondaire*, comme on le verra par la suite.

# pytest

On a vu plus haut comment écrire du code de test "à la main" avec `assert`. Étoffons un peu l'exemple&nbsp;:

```python
# dans calc.py

def add_one(x):
     return x + 2

def add_two(x):
     return x + 2
```

```python
# dans test_calc.py

result = calc.add_one(3)
assert result == 4

result = calc.add_two(5)
assert result == 7
```

On constate que tester le code ainsi est fastidieux&nbsp;:

* Les valeurs effectives ne sont pas affichées par défaut
* Le programme de test va s'arrêter à la première erreur, donc si `calc_one` est cassé, on ne saura rien sur l'état de `calc_two`
* On ne peut pas facilement isoler les tests à lancer

C'est là que `pytest` entre en jeu.

On commence par créer un virtualenv pour `calc` et par installer `pytest` dedans [^2]

```bash
$ mkdir -p venvs && cd venvs
$ python3 -m venv calc
$ source calc/bin/activate
(calc) $ pip install pytest
```

Ensuite, on transforme chaque assertion en une fonction commençant par `test_`:

```python
import calc

def test_add_one():
    result = calc.add_one(3)
    assert result == 4, "result != 4"


def test_add_two():
    result = calc.add_two(5)
    assert result == 7
```

... et on corrige les bugs&nbsp;:

```python
def add_one(x):
     return x + 1


def add_two(x):
    return x + 2
```

Enfin, on lance `pytest` en précisant le chemin de fichier de test&nbsp;:

```
$ pytest test_calc.py
============================= test session starts ==============================
test_calc.py ..                                                          [100%]
========================== 2 passed in 0.01 seconds ===========================
```


Chaque point après `test_calc.py` représente un test qui passe. Voyons ce qui arrive si
on ré-introduit un bug&nbsp;:


```python
def add_one(x):
     return x + 3


def add_two(x):
    return x + 2
```

```
$ pytest test_calc.py
============================= test session starts ==============================
test_calc.py F.                                                          [100%]

=================================== FAILURES ===================================
_________________________________ test_add_one _________________________________

    def test_add_one():
        result = calc.add_one(3)
>       assert result == 4
E       assert 6 == 4

test_calc.py:5: AssertionError
```

À noter :

* Le test pour `add_two` a quand même été lancé
* La valeur *effective* est affiché sous la ligne d'assert
* La backtrace a été affiché
* On a une vue du code qui a produit le bug
* Le test qui a échoué est affiché avec un `F` majuscule

On peut aussi dire à pytest de ne lancer *que les tests qui ont échoué* à la session précédente&nbsp;:

```
$ pytest test_calc.py --last-failed
run-last-failure: rerun previous 1 failure

test_calc.py
=================================== FAILURES ===================================
_________________________________ test_add_one _________________________________
```

Cool, non ?

# Limites des tests

Avant de poursuivre, penchons-nous sur deux limitations importantes des tests.

Premièrement, les tests peuvent échouer même si le code de production est correct :

```python
def test_add_one():
   result = add_one(2)
   assert result == 4
```

Ici on a un *faux négatif*. L'exemple peut vous faire sourire, mais c'est un problème plus
fréquent que ce que l'on croit.

Ensuite, les tests peuvent passer *en dépit* de bugs dans le code. Par exemple, si
on oublie une assertion&nbsp;:

```python
def add_two(x):
    return x + 3

def test_add_two():
    result = calc.add_two(3)
    # fin du test
```

Ici, on a juste vérifié qu'appeler `add_two(3)` ne provoque pas d'erreur. On dit
qu'on a un *faux positif*, ou un *bug silencieux*.

Autre exemple :

```python
def fonction_complexe():
   if condition_a:
       ...
   if condition_b:
      ...
```

Ici, même s'il n'y a que deux lignes commençant par `if`, pour être
exhaustif, il faut tester 4 possibilités, correspondant aux 4 valeurs
combinées des deux conditions. On comprend bien que plus le code devient
complexe, plus le nombre de cas à tester devient gigantesque.

Dans le même ordre d'idée, les tests ne pourront *jamais* vérifier le
comportement entier du code. On peut tester `add_one()` avec des exemples,
mais on voit difficilement commeent tester `add_one()` avec tous les entiers
possibles. [^3]


Cela dit, maintenant qu'on sait comment écrire et lancer des tests,
revenons sur les bénéfices des tests sur la valeur secondaire du code.

# Empêcher les régressions

On a vu comment les tests peuvent mettre en évidence des bugs présents dans le code.

Ainsi, à tout moment, on peut lancer la suite de tests pour vérifier (une partie) du
comportement du code, notamment après toute *modification* du code de production.

On a donc une chance de trouver des bugs bien avant que les utilisateurs du produit
l'aient entre les mains.

# Refactorer sans peur

Le deuxième effet bénéfique est lié au premier.

Imaginez un code avec un comportement assez complexe. Vous avez une nouvelle fonctionnalité à
rajouter, mais le code dans son état actuel ne s'y prête pas.

Une des solutions est de commencer par effectuer un *refactoring*, c'est-à dire de commencer
par *adapter* le code mais *sans changer son comportement* (donc sans introduire de bugs). Une fois ce refactoring effectué,
le code sera prêt à être modifié et il deviendra facile d'ajouter la fonctionnalité.

Ainsi, disposer d'une batterie de tests qui vérifient le comportement du programme automatiquement et de manière exhaustive
est très utile. Si, à la fin du refactoring vous pouvez lancer les tests et constater qu'ils passent tous, vous serez plus confiant sur le fait que votre refactoring n'a pas introduit de nouveaux bugs.


# Une discipline

Cela peut paraître surprenant, surtout à la lumière des exemples basiques que je vous ai montrés, mais écrire des tests est un art *difficile* à maîtriser. Cela demande un état d'esprit *différent*
de celui qu'on a quand on écrit du code de production. En fait, écrire des bons tests est une compétence
qui s'apprend.

Ce que je vous propose ici c'est une *discipline*&nbsp;: un ensemble de règles et une façon de faire qui vous
aidera à développer cette compétence. Plus vous pratiquerez cette discipline, meilleur sera votre code
de test, et, par extension, votre code de production.

Commençons par les règles&nbsp;:

* Règle 1 : Il est interdit d'écrire du code de production, *sauf* si c'est pour faire passer un test qui
  a échoué.
* Règle 2 : Il est interdit d'écrire plus de code que celui qui est nécessaire pour provoquer une erreur
  dans les tests (n'importe quelle erreur)
* Règle 3 : Il est interdit d'écrire plus de code que celui qui est nécessaire pour faire passer
  un test qui a échoué
* Règle 4 : Une fois que tous les tests passent, il est interdit de modifier le code sans s'arrêter
  pour considérer la possibilité d'un refactoring. [^4]

Et voici une procédure pour appliquer ces règles: suivre le *cycle* de dévelopement suivant:

* Écrire un test qui échoue - étape "red"
* Faire passer le test - étape "green"
* Refactorer à la fois le code de production et le code de test - étape "refactor"
* Retour à l'étape "red".

# TDD en pratique

Si tout cela peut vous semble abstrait, je vous propose une démonstration.

Pour cela, on va utilser les [règles du bowling](https://fr.wikipedia.org/wiki/Bowling#R%C3%A8gles).

Comme on code en anglais[^5], on va utiliser les termes anglophones. Voici les règles:

* Un jeu de bowling comporte 10 carreaux (ou *frames*).
* Chaque frame comporte deux lancers (ou *roll*) et 10 quilles (ou *pins*)
* Si on renverse toutes les quilles en un lancer, on marque un abat (ou *strike*)
* Si on renverse toutes les quilles dans un même carreau, on marque une réserve (ou *spare*)

On calcule le score frame par frame:

* Si on fait un strike, on marque 10 points, plus les points obtenus à la frame suivante (donc 2 rolls)
* Si on fait une spare, on marque 10 points, plus les points obtenus au lancer suivant (donc juste le roll suivant)
* Sinon on marque le total de quilles renversées dans la frame

La dernière frame est spéciale: si on fait un strike, on a droit à deux rolls supplémentaires, et si on fait une spare,
on a droit à un roll en plus.

# Un peu d'architecture

La règle 0 de tout bon programmeur est: "réfléchir avant de coder". Prenons le temps de réfléchir un peu, donc.

On peut se dire que pour calculer le score, une bonne façon sera d'avoir une classe `Game` avec deux méthodes:

* `roll()`, qui sera appellée à chaque lancer avec le nombre de quilles renversées en paramètre
* `score()`, qui renvera le score final

Au niveau du découpage en classes, on peut partir du diagramme suivant:


![class diagram](/pics/bowling.png)

On a:

* Une classe `Game` qui contient des `frames`
* Chaque frame est une instance de la class `Frame`
* Chaque frame contient une aux deux instance de la class `Roll`
* Une classe `Roll` contenant un attribut `pins` correspondant au nombre
  de quilles renversées.
* Une classe `TenthFrame`, qui hérite de la classe `Frame` et implémente
  les règles spécifiques au dernier lancer.

# C'est parti

Retours aux régles:

* Règle 1: Il est interdit d'écrire du code de production, *sauf* si c'est pour faire passer un test qui
  a échoué.
* Règle 2: Il est interdit d'ecrire plus de code que celui qui est nécessaire pour provoquer une erreur
  dans les tests (n'importe quelle erreur)
* Règle 3: Il est interdit d'écrire plus de code que celui qui est nécessaire pour faire passer
  un test qui a échoué
* Règle 4: Une fois que tous les tests passent, il est interdit de modifier le code sans s'arrêter
  pour considérer la possibilité d'un refactoring. [^4]


Comme pour l'instant on a aucun code, la seule chose qu'on puisse faire c'est écrire un test qui échoue.

<center>⁂ RED⁂</center>

On crée un virtualenv pour notre code:

```bash
$ python3 -m venvs/bowling
$ source venvs/bowling/bin/activate
$ pip install pytest
```

On créé un fichier `test_bowling.py` qui contient *juste une ligne*:

```python
import bowling
```

On lance les tests:

```bash
$ pytest test_bowling.py
test_bowling.py:1: in <module>
    import bowling
E   ModuleNotFoundError: No module named 'bowling'
```

On a une erreur, donc on arrête d'écrire du code de test (règle 2), et on passe
à l'état suivant.

<center>⁂ GREEN⁂</center>

Pour faire passer le test, il suffit de créer un fichier `bowling.py` vide.


```
$ pytest test_bowling.py
collected 0 items

========================= no tests ran in 0.34 seconds ========================
```

Bon, clairement ici il n'y a rien à refacter (règle 4), donc on repart au début du cycle.


<center>⁂ RED⁂</center>

Ici on cherche à faire échouer le test le plus simplement possible.

Commençons simplement par véfier qu'on peut instancier la class Game&nbsp;:

```python
import bowling

def test_can_create_game():
    game = bowling.Game()
```

```
$ pytest test_bowling.py
>       game = bowling.Game()
E       AttributeError: module 'bowling' has no attribute 'Game'
```

Le test échoue, faisons-le passer:

<center>⁂GREEN⁂</center>

```python
class Game:
    pass
```

Tojours rien à refactorer ...

<center>⁂RED⁂</center>


Écrivons un test pour `roll()`:

```python
def test_can_roll():
    game = bowling.Game()
    game.roll(0)
```

```
$ pytest test_bowling.py
>       game.roll(0)
E       AttributeError: 'Game' object has no attribute 'roll'
```


<center>⁂GREEN⁂</center>

Faisons passer les tests en rajoutant une méthode:

```python
class Game:
    def roll(self, pins):
        pass
```

Toujours pas de refactoring en vue. En même temps, on n'a que 6 lignes de test
et 3 lignes de code de production ...

<center>⁂RED⁂</center>

On continue à tester les méthodes de la classe Game, de la façon la plus simple possible&nbsp;:

```python
def test_can_score():
    game = bowling.Game()
    game.roll(0)
    score = game.score()
```

```
$ pytest test_bowling.py
>       game.roll(0)
E       AttributeError: 'Game' object has no attribute 'roll'
```

<center>⁂GREEN⁂</center>

On fait passer le test, toujours de la façon la plus simple possible&nbsp;:

```python
class Game:
    def roll(self, pins):
        pass

    def score(self):
    	pass
```

<center>⁂ REFACTOR⁂</center>

Le code production a l'air impossible à refactorer, mais jetons un œil aux tests:

```python
import bowling

def test_can_create_game():
    game = bowling.Game()


def test_can_roll():
    game = bowling.Game()
    game.roll(0)


def test_can_score():
    game = bowling.Game()
    game.roll(0)
    game.score()

```

Hum. Le premier et le deuxième test sont inclus *exactement* dans le dernier test. Ils ne servent donc à rien, et
peuvent être supprimés.


<center>⁂RED⁂</center>

En y réflchéssant, `can_score()` ne vérifie même pas la valeur de retour de `score()`. Écrivons un test légèrement différent&nbsp;:

```python
def test_score_is_zero_after_gutter():
    game = bowling.Game()
    game.roll(0)
    score = game.score()
    assert score == 0
```


`gutter` signifie "goutière" en anglais et désigne un lancer qui finit dans la rigole (et donc ne renverse aucune quille)

```
$ pytest test_bowling.py
>       assert score == 0
E       assert None == 0
```

<center>⁂GREEN⁂</center>

Faisons le passer:

```python
class Game:
    def roll(self, pins):
        pass

    def score(self):
        return 0
```

Notez qu'on a fait passer le test en écrivant du code que l'on *sait* être incorrect. Mais la règle 3 nous interdit d'aller plus loin.

Vous pouvez voir cela comme une contrainte arbitraire (et c'en est est une), mais j'aimerais vous faire remarquer qu'on en a fait *spécifié*
l'API de la classe Game. Le test, bien qu'il ne fasse que quelques lignes,
nous indique l'existence des métode `roll()` et `score()`, les paramètres
qu'elles attendent et, à un certain point, la façon dont elles intéragissent

C'est une autre facette des tests: ils vous permettent de transformer une
spécification en code éxecutable. Ou, dit autrement, ils vous permettent
d'écrire des exemples d'utilisation de votre API *pendant que vous
l'implémentez*. Et, en vous forçant à ne pas écrire trop de code de production,
vous avez la possibilité de vous concentrer *uniquement* sur l'API de votre code,
sans vous soucier de l'implémentation.

Bon, on a enlevé plein de tests, du coup il n'y a encore plus grand-chose à refactorer,
passons au prochain.

<center>⁂RED⁂</center>

Rappelez-vous, on vient de dire que le code de `score()` est incorrect. La question devient donc: quel test pouvons-nous
écrire pour nous forcer à écrire un code un peu plus correct?

Une possible idée est d'écrire un test pour un jeu ou tous les lancers renversent exactement une quille:

```python
def test_all_ones():
    game = bowling.Game()
    for roll in range(20):
        game.roll(1)
    score = game.score()
    assert score == 20
```

```
>       assert score == 20
E       assert 0 == 20
```

<center>⁂GREEN⁂</center>

Ici la boucle dans le test nous force à *changer* l'état de la
class Game à chaque appel à `roll()`, ce que nous pouvouns faire
en rajoutant un attribut qui conmpte le nombre de quilles
renversées

```python
class Game:
    def __init__(self):
        self.knocked_pins = 0

    def roll(self, pins):
        self.knocked_pins += pins

    def score(self):
        return self.knocked_pins
```

Les deux tests passent, mission accomplie.

<center>⁂REFACTOR⁂</center>

Encore une fois, concentrous-nous sur les tests.

```python
def test_score_is_zero_after_gutter():
    game = bowling.Game()
    game.roll(0)
    score = game.score()
    assert score == 0


def test_all_ones():
    game = bowling.Game()
    for roll in range(20):
        game.roll(1)
    score = game.score()
    assert score == 20
```

Ces deux tests nous montre une *ambiguïté* dans les specifications. Veut-on pouvoir obtenir le score en temps réel, ou voulons-nous
simplement appeler `score` à la fin de la partie&nbsp;?

On retrouve ce lien intéressant entre tests et API: aurions-nous découvert cette ambiguïté sans avoir écrit aucun test&nbsp;?

Ici, on va décider que `score()` n'est appelé qu'à la fin de la partie, et donc réécrire les tests ainsi&nbsp;:

```python
def test_gutter_game():
    game = bowling.Game()
    for roll in range(20):
        game.roll(0)
    score = game.score()
    assert score == 0


def test_all_ones():
    game = bowling.Game()
    for roll in range(20):
        game.roll(1)
    score = game.score()
    assert score == 20
```

Les tests continuent à passer. On peut maintenant réduire la duplication en introduisant une fonction `roll_many`&nbsp;:

```python
def roll_many(game, count, value):
    for roll in range(count):
        game.roll(value)

def test_gutter_game():
    game = bowling.Game()
    roll_many(game, 20, 0)
    score = game.score()
    assert score == 0


def test_all_ones():
    game = bowling.Game()
    roll_many(game, 20, 1)
    score = game.score()
    assert score == 20
```


<center>⁂RED⁂</center>

L'algorithme utilisé (rajouter les quilles renversées au score à chaque lancer) semble fonctionner tant qu'il n'y a ni spare ni strike.

Du coup, rajoutons un test sur les spares:

```python
def test_one_spare():
    game = bowling.Game()
    game.roll(5)
    game.roll(5)  # spare, next roll should be counted twice
    game.roll(3)
    roll_many(game, 17, 0)
    score = game.score()
    assert score == 16
```

```
        score = game.score()
>       assert score == 16
E       assert 13 == 16
```


<center>⁂GREEN⁂</center>


Et là, on se retrouve *coincé*. Il semble impossible d'implémenter la gestion des spares sans revoir le code de production en profondeur:

```python
    def roll(self, pins):
        # TODO: get the knocked pin in the next
        # roll if we are in a spare ???
        self.knocked_pins += pins
```

C'est un état dans lequel on peut parfois se retrouver. La solution&nbsp;? Faire un pas en arrière pour prendre du recul.

On peut commencer par désactiver le test qui nous ennuie&nbsp;:

```python
import pytest


@pytest.mark.skip
def test_one_spare():
   ...
```

Ensuite, on peut regarder le code de production dans le blanc des yeux&nbsp;:

```python
    def roll(self, pins):
        self.knocked_pins += pins

    def score(self):
        return self.knocked_pins
```

Ce code a un problème&nbsp;: en fait, c'est la méthode `roll()` qui calcule le score, et non la fonction `score()`&nbsp;!

On comprend que `roll()` doit simplement enregistrer l'ensemble des résultats des lancers, et qu'ensuite seulement,
`score()` pourra parcourir les frames et calculer le score.

<center>⁂REFACTOR⁂</center>

On remplace donc l'attribut `knocked_pins()` par une liste de rolls et un index:

```python
class Game:
    def __init__(self):
        self.rolls = [0] * 21
        self.roll_index = 0

    def roll(self, pins):
        self.rolls[self.current_roll] = pins
        self.current_roll += 1

    def score(self):
        result = 0
        for roll in self.rolls:
            result += roll
        return result
```

Petit apparté sur le nombre 21. Ici ce qu'on veut c'est le nombre maximum de frames.
On peut s'assurer que 21 est bien le nombre maximum en énumérant les cas possibles
de la dernière frame, et en supposant qu'il n'y a eu ni spare ni strike au cours
du début de partie (donc 20 lancers, 2 pour chacune des 10 premières frame)

* spare: on va avoir droit à un un lancer en plus: 20 + 1 = 21
* strike: par défnition, on n'a fait qu'un lancer à la dernière frame, donc au plus 19 lancers, et 19 plus 2 font bien 21.
* sinon: pas de lancer supplémentaire, on reste à 20 lancers.

Relançons les tests:

```
test_bowling.py ..s                                                      [100%]

===================== 2 passed, 1 skipped in 0.01 seconds ======================
```

(notez le 's' pour 'skipped')

L'algorithme est toujours éronné, mais on sent qu'on une meilleure chance de réussir à gérer les spares.

<center>⁂RED⁂</center>

On ré-active le test en enlevant la ligne `@pytest.mark.skip` et on retombe évidemment sur la même erreur:

```
>       assert score == 16
E       assert 13 == 16
```

<center>⁂GREEN⁂</center>

Pour faire passer le test, on peut simplement itérer sur les frames une par une, en utilisant
une variable `i` qui vaut l'index du premier lancer de la prochaine frame:

```python
    def score(self):
        result = 0
        i = 0
        for frame in range(10):
            if self.rolls[i] + self.rolls[i + 1] == 10:  # spare
                result += 10
                result += self.rolls[i + 2]
                i += 2
            else:
                result += self.rolls[i]
                result += self.rolls[i + 1]
                i += 2
        return result
```

Mon Dieu que c'est moche! Mais cela me permet d'aborder un autre aspect du TDD. Ici, on est dans la phase "green". On fait tout ce qu'on peut
pour faire passer le tests et rien d'autre. C'est un état d'esprit particulier, on était concentré sur l'algorithme en lui même.


<center>⁂REFACTOR⁂</center>

Par contraste, ici on *sait* que l'algorithme est correct. Notre *unique* objectif est de rendre le code plus lisible. Un des avantages de TDD est qu'on passe d'un objectif précis à l'autre, au lieu d'essayer de tout faire en même temps.

Bref, une façon de refactorer est d'introduire une nouvelle méthode&nbsp;:

```python
    # note: i represents the index of the
    # first roll of the current frame
    def is_spare(self, i):
        return self.rolls[i] + self.rolls[i + 1] == 10

    def score(self):
        result = 0
        i = 0
        for frame in range(10):
            if self.is_spare(i):
                result += 10
                result += self.rolls[i + 2]
                i += 2
            else:
                result += self.rolls[i]
                result += self.rolls[i + 1]
                i += 2

```

En passant, on s'est débarrassé du commentaire "# spare" à la fin du `if`, vu qu'il n'était plus utile. En revanche, on a gardé un commentaire au-dessus
de la méthode `is_spare()`. En effet, il n'est pas évident de comprendre la valeur représentée par l'index `i` juste en lisant le code. [^6]

On voit aussi qu'on a gardé un peu de duplication. Ce n'est pas forcément très grave, surtout que l'algorithme est loin d'être terminé. Il faut encore gérer les strikes et la dernière frame.

Mais avant cela, revons sur les tests (règle 4)

```python
def test_one_spare():
    game = bowling.Game()
    game.roll(5)
    game.roll(5)  # spare, next roll should be counted twice
    game.roll(3)
    roll_many(game, 17, 0)
    score = game.score()
    assert score == 16
```

On a le même genre de commentaire qui nous suggère qu'il manque une abstraction quelque part&nbsp;: une fonction `roll_spare`:


```python
import bowling
import pytest

def roll_many(game, count, value):
    for roll in range(count):
        game.roll(value)


def roll_spare(game):
    game.roll(5)
    game.roll(5)


def test_one_spare():
    game = bowling.Game()
    roll_spare(game)
    game.roll(3)
    roll_many(game, 17, 0)
    score = game.score()
    assert score == 16
```

Les tests continuent à passer, tout va bien.

Mais le code de test peut *encore* être amélioré. On voit qu'on a deux fonctions qui prennent chacune le même paramètre en premier argument.

Souvent, c'est le signe qu'une classe se cache quelque part.

On peut créer une classe `GameTest` qui hérite de `Game` et contient les méthodes `roll_many()` et `roll_spare()`&nbsp;:


```python
import bowling
import pytest


class GameTest(bowling.Game):
    def roll_many(self, count, value):
        for roll in range(count):
            self.roll(value)

    def roll_spare(self):
        self.roll(5)
        self.roll(5)


def test_gutter_game():
    game = GameTest()
    game.roll_many(20, 0)
    score = game.score()
    assert score == 0


def test_all_ones():
    game = bowling.GameTest()
    game.roll_many(20, 1)
    score = game.score()
    assert score == 20


def test_one_spare():
    game = GameTest()
    game.roll_spare()
    game.roll(3)
    game.roll_many(17, 0)
    score = game.score()
    assert score == 16
```

Ouf! Suffisasemment de refactoring pour l'instant, retour au rouge.

<center>⁂RED⁂</center>

Avec notre nouvelle classe définie au sein de `test_bowling.py` (au dit souvent "test helper"), on peut facilement rajouter le test sur les strikes&nbsp;:


```python
def test_one_strike():
    game = GameTest()
    game.roll_strike()
    game.roll(3)
    game.roll(4)
    game.roll_many(16, 0)
    score = game.score()
    assert score == 24
```

A piori, tous les tests devraient passer sauf le dernier, et on devrait avoir une erreur de genre `x != 24`, avec x légèrement en-dessous de 24:

```
________________________________ test_all_ones _________________________________

    def test_all_ones():
>       game = bowling.GameTest()
E       AttributeError: module 'bowling' has no attribute 'GameTest'

_______________________________ test_one_strike ________________________________

    def test_one_strike():
        game = GameTest()
        game.roll_strike()
        game.roll(3)
        game.roll(4)
        game.roll_many(16, 0)
        score = game.score()
>       assert score == 24
E       assert 17 == 24

test_bowling.py:48: AssertionError
```

Oups, deux erreurs! Il se trouve qu'on a oublié de lancer les tests à la fin du dernier refactoring. En fait, il y a une ligne qui a été changée de façon incorrecte: ``` game = bowling.GameTest()``` au lieu de ```game = GameTest()```. L'aviez-vous remarqué?

Cela illustre deux points:

1. Il faut toujours avoir une vague idée des tests qui vont échouer et de quelle manière
2. Il est important de garder le cycle de TDD court. En effet, ici on *sait* que seuls les tests ont changé depuis la dernière session de test, donc on *sait* que le problème vient des tests et non du code de production.

On peut maintenant corriger notre faux positif, relancer les tests, vérifier qu'ils échouent *pour la bonne raison* et passer à l'étape suivante.

```
______________________________ test_one_strike ________________________________

    def test_one_strike():
        game = GameTest()
        game.roll_strike()
        game.roll(3)
        game.roll(4)
        game.roll_many(16, 0)
        score = game.score()
>       assert score == 24
E       assert 17 == 24

test_bowling.py:48: AssertionError
```

<center>⁂GREEN⁂</center>

Là encore, on a tous les éléments pour implémenter la gestion de strikes correctement, grâce aux refactorings précédents et au fait qu'on a implémenté l'algorithme de façon *incrémentale*, un petit bout à la fois.


```python
class Game:
    ...

    def is_spare(self, i):
        return self.rolls[i] + self.rolls[i + 1] == 10

    def is_strike(self, i):
        return self.rolls[i] == 10

    def score(self):
        result = 0
        i = 0
        for frame in range(10):
            if self.is_strike(i):
                result += 10
                result += self.rolls[i + 1]
                result += self.rolls[i + 2]
                i += 1
            elif self.is_spare(i):
                result += 10
                result += self.rolls[i + 2]
                i += 2
            else:
                result += self.rolls[i]
                result += self.rolls[i + 1]
                i += 2
        return result
```

J'espère que vous ressentez ce sentiment que le code "s'écrit tout seul". Par contraste, rappelez-vous la difficulté pour implémenter les spares et imaginez à quel point cela aurait été difficile de gérer les spares *et* les strikes en un seul morceau!


<center>⁂REFACTOR⁂</center>

On a mantenant une boucle avec *trois* branches. Il est plus facile maintenant de finir le refactoring commencé précédement, et d'isoler les lignes qui se ressemblent des lignes qui différent&nbsp;:

```python
class Game:
    ...
    def is_strike(self, i):
        return self.rolls[i] == 10

    def is_spare(self, i):
        return self.rolls[i] + self.rolls[i + 1] == 10

    def next_two_rolls_for_strike(self, i):
        return self.rolls[i + 1] + self.rolls[i + 2]

    def next_roll_for_spare(self, i):
        return self.rolls[i + 2]

    def rolls_in_frame(self, i):
        return self.rolls[i] + self.rolls[i + 1]

    def score(self):
        result = 0
        i = 0
        for frame in range(10):
            if self.is_strike(i):
                result += 10
                result += self.next_two_rolls_for_strike(i)
                i += 1
            elif self.is_spare(i):
                result += 10
                result += self.next_roll_for_spare(i)
                i += 2
            else:
                result += self.rolls_in_frame(i)
                i += 2
        return result
```

On approche du but, il ne reste plus qu'à gérer la dernière frame.

<center>⁂RED⁂</center>

Écrivons maintenant le test du jeu parfait, on le joueur fait un stirke à chaque essai. Il y a donc 10 frames de strike, puis deux strikes (pour les deux derniers lancers de la dernière frame) soit 12 strikes en tout.

Et comme tout joueur de bowling le sait, le score maximum au bowling est 300&nbsp;:

```python
def test_perfect_game():
    game = GameTest()
    for i in range(0, 12):
        game.roll_strike()
    assert game.score() == 300
```

On lance les tests, et...

```
collected 5 items

test_bowling.py .....                                                          [100%]
============================= 5 passed in 0.02 seconds ==============================
```

Ils passent?

Ici je vais vous laisser 5 minutes de refléxion pour vous convaincre qu'en realité, la dernière
frame n'a absolument rien de spécial, et que c'est la raison pour laquelle notre algorithme
fonctionne.

# Conclusions

D'abord, je trouve qu'on peut être fier du code auquel on a abouti:

```python
        result = 0
        i = 0
        for frame in range(10):
            if self.is_strike(i):
                result += 10
                result += self.next_two_rolls_for_strike(i)
                i += 1
            elif self.is_spare(i):
                result += 10
                result += self.next_roll_for_spare(i)
                i += 2
            else:
                result += self.rolls_in_frame(i)
                i += 2
```

Le code se "lit" quasiment comme les règles du bowling. Il a l'air correct, et il *est* correct.

Ensuite, même si notre refléxion initiale nous a guidé (notamment avec la classe Game et ses deux méthodes),
notez qu'on a pas eu besoin des classes `Frame` ou `Roll`, ni de la classe fille `TenthFrame`. En ce sens, on peut dire que TDD est égalemnent
une façon de *concevoir* le code, et pas juste une façon de faire évoluer le code de production et le code de test en parralèle.

Enfin, on avait un moyen de savoir quand le code était *fini*. Quand on pratique TDD, on sait qu'on peut s'arrêter dès que tous les tests
passent. Et, d'après l'ensemble des règles, on sait qu'on a écrit *uniquement* le code *nécessaire*.


# Pour aller plus loin

Plusieurs remarques:

1/ La méthode `roll()` peut être appelée un nombre trop grand de fois, comme le prouve le test suivant:

```python
def test_two_many_rolls():
   game = GameTest()
   game.roll_many(21, 1)
   assert game.score() == 20
```

Savoir ci c'est un bug ou non dépend des spécifications.

2/ Il y a probablement une classe ou une méthode cachée dans la classe `Game`. En effet, on a plusieurs méthodes qui prennent toutes un index en premier paramètre, et le paramètre en question nécessite un commentaire pour être compris.

Résoudre ces deux problèmes sera laissé en exercice au lecteur :P

# Conclusion

Voilà pour cette présentation sur le TDD. Je vous recommande d'essayer cette méthode par vous-mêmes. En ce qui me concerne elle a changé ma façon d'écrire du code en profondeur, et après plus de 5 ans de pratique, j'ai du mal à envisager de coder autrement.

À +

[^1]: C'est payant, c'est en anglais, les exemples sont en Java, mais c'est vraiment très bien.
[^2]: Voir [cet article]({{< relref "0002-bibliotheques-tierces-python.md" >}}) pour comprendre pourquoi on procède ansi.
[^3]: Il existe de nombreux outils pour palier aux limitations des tests, mais on en parlera une prochaine fois.
[^4]: Les trois premières règles sont de Uncle Bob, la dernière est de moi.
[^5]: Vous avez tout à fait le droit d'écrire du code en français. Mais au moindre doute sur la possibilité qu'un non-francophone doive lire votre code un jour, vous *devez* passer à l'anglais.
[^6]: Si cette façon de commenter du code vous intrigue, vous pouvez lire [cet excellent article](https://hackaday.com/2019/03/05/good-code-documents-itself-and-other-hilarious-jokes-you-shouldnt-tell-yourself/) (en anglais) pour plus de détails.
[^8]: Par exemple, quand on lance python avec l'option `-O`
